"""Run against Docker Compose: actual Kafka -> Flink -> worker -> PostgreSQL path."""
import os
import time
from uuid import uuid4
import httpx

base = os.getenv("API_URL", "http://localhost:8000")
keys = {"X-API-Key": os.getenv("DEMO_API_KEY", "demo-shop-local-key")}
with httpx.Client(base_url=base, headers=keys, timeout=20) as client:
    for _ in range(90):
        try:
            if client.get("/health").status_code==200: break
        except httpx.HTTPError: pass
        time.sleep(2)
    else: raise RuntimeError("API did not become ready")
    tx=dict(transaction_id=str(uuid4()),amount=300,hour=2,distance_km=400,account_age_days=12,is_international=1)
    r=client.post("/transactions",json=tx); r.raise_for_status()
    for _ in range(90):
        rows=client.get("/predictions").json()
        matching=[x for x in rows if x["transaction_id"]==tx["transaction_id"]]
        if matching: break
        time.sleep(2)
    else: raise RuntimeError("Stream did not produce prediction")
    assert 0 <= matching[0]["probability"] <= 1
    client.put('/labels/'+tx['transaction_id'],json={"fraud":True}).raise_for_status()
    # Replay the same transaction, including through synchronous endpoint.
    replay=client.post("/score",json=tx); replay.raise_for_status()
    assert replay.json()["probability"] == matching[0]["probability"]
    assert client.post("/score",json=tx|{"amount":350}).status_code==409
    assert client.get("/predictions",headers={"X-API-Key":"invalid"}).status_code==401
    assert len([x for x in client.get('/predictions').json() if x['transaction_id']==tx['transaction_id']])==1
print("PASS: Kafka → Flink → worker → API → PostgreSQL, feedback, replay, auth")
