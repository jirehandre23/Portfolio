import asyncio
from contextlib import asynccontextmanager
import hashlib
import hmac
import json
import math
import os
from pathlib import Path
import asyncpg
from aiokafka import AIOKafkaProducer
from fastapi import FastAPI, Header, HTTPException, Depends
import mlflow.pyfunc
from fraudwatch.features import Transaction, EnrichedTransaction, Feedback, features


def tenant(x_api_key: str = Header(default="")):
    keys = json.loads(os.environ["TENANT_API_KEYS"])
    for name, key in keys.items():
        if hmac.compare_digest(x_api_key, key):
            return name
    raise HTTPException(401, "Invalid API key")


@asynccontextmanager
async def lifespan(app):
    artifact = Path(os.getenv("ARTIFACT_DIR", "artifacts"))
    app.state.model = mlflow.pyfunc.load_model(str(artifact / "model"))
    app.state.meta = json.loads((artifact / "metadata.json").read_text())
    app.state.pool = await asyncpg.create_pool(os.environ["DATABASE_URL"], min_size=1, max_size=5)
    app.state.producer = AIOKafkaProducer(bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP", "kafka:9092"),
                                        acks="all", enable_idempotence=True)
    await app.state.producer.start()
    try:
        yield
    finally:
        await app.state.producer.stop()
        await app.state.pool.close()

app = FastAPI(title="FraudWatch", version="1.0.0", lifespan=lifespan)


@app.get("/health")
async def health():
    await app.state.pool.fetchval("SELECT 1")
    return {"status": "ready", "model_version": app.state.meta["model_version"]}


@app.post("/transactions", status_code=202)
async def enqueue(tx: Transaction, owner=Depends(tenant)):
    event = tx.model_dump(mode="json") | {"tenant_id": owner}
    await asyncio.wait_for(app.state.producer.send_and_wait(
        "transactions.raw", json.dumps(event).encode(), key=f"{owner}:{tx.transaction_id}".encode()), timeout=15)
    return {"transaction_id": str(tx.transaction_id), "status": "queued"}


def response(row):
    return {k: row[k] for k in ("transaction_id", "probability", "decision", "threshold", "model_version")}


async def score(tx, owner):
    payload = tx.model_dump(mode="json", exclude={"log_amount"})
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    async with app.state.pool.acquire() as conn:
        existing = await conn.fetchrow("SELECT * FROM predictions WHERE tenant_id=$1 AND transaction_id=$2",
                                       owner, tx.transaction_id)
        if existing:
            if existing["payload_hash"] != digest:
                raise HTTPException(409, "Transaction ID already used for different input")
            return response(existing)
        frame = features([payload])
        # CPU-bound inference runs off the event loop; database I/O is awaited.
        result = await asyncio.to_thread(app.state.model.predict, frame)
        p = float(result["fraud_probability"].iloc[0])
        meta = app.state.meta
        await conn.execute("""INSERT INTO predictions
          (tenant_id,transaction_id,payload_hash,features,probability,decision,threshold,model_version)
          VALUES ($1,$2,$3,$4,$5,$6,$7,$8) ON CONFLICT DO NOTHING""",
          owner, tx.transaction_id, digest, frame.iloc[0].to_json(), p, p >= meta["threshold"],
          meta["threshold"], meta["model_version"])
        row = await conn.fetchrow("SELECT * FROM predictions WHERE tenant_id=$1 AND transaction_id=$2",
                                  owner, tx.transaction_id)
        if row["payload_hash"] != digest:
            raise HTTPException(409, "Transaction ID already used for different input")
        return response(row)


@app.post("/score")
async def direct_score(tx: Transaction, owner=Depends(tenant)):
    return await score(tx, owner)


@app.post("/score/enriched")
async def enriched_score(tx: EnrichedTransaction, owner=Depends(tenant)):
    # Guard against training/stream transformation skew.
    if not math.isclose(tx.log_amount, math.log1p(tx.amount), rel_tol=1e-7, abs_tol=1e-7):
        raise HTTPException(422, "Stream feature differs from training transformation")
    return await score(tx, owner)


@app.put("/labels/{transaction_id}")
async def label(transaction_id: str, feedback: Feedback, owner=Depends(tenant)):
    from uuid import UUID
    try:
        identifier = UUID(transaction_id)
    except ValueError:
        raise HTTPException(422, "Invalid UUID")
    status = await app.state.pool.execute("""UPDATE predictions SET label=$1, labeled_at=now()
        WHERE tenant_id=$2 AND transaction_id=$3""", feedback.fraud, owner, identifier)
    if status == "UPDATE 0":
        raise HTTPException(404, "Prediction not found")
    return {"status": "recorded"}


@app.get("/predictions")
async def predictions(owner=Depends(tenant)):
    rows = await app.state.pool.fetch("""SELECT transaction_id,features,probability,decision,
        threshold,model_version,created_at,label FROM predictions
        WHERE tenant_id=$1 ORDER BY created_at DESC LIMIT 5000""", owner)
    return [dict(r) | {"features": json.loads(r["features"])} for r in rows]
