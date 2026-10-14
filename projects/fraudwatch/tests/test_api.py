from contextlib import asynccontextmanager
from uuid import uuid4
import json
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from fraudwatch.api import app

class Model:
    def predict(self, x):
        return pd.DataFrame({"fraud_probability": [.7]})

class Pool:
    def __init__(self): self.rows = {}
    @asynccontextmanager
    async def acquire(self): yield self
    async def fetchrow(self, query, owner, identifier): return self.rows.get((owner, identifier))
    async def execute(self, query, *args):
        if query.startswith("INSERT"):
            owner, identifier, digest, feat, p, decision, threshold, version = args
            self.rows.setdefault((owner,identifier), dict(transaction_id=identifier, payload_hash=digest,
                features=feat, probability=p, decision=decision, threshold=threshold, model_version=version))
        else:
            label, owner, identifier = args
            return "UPDATE 1" if (owner,identifier) in self.rows else "UPDATE 0"
    async def fetch(self, query, owner):
        return [row for (tenant, _), row in self.rows.items() if tenant == owner]

@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("TENANT_API_KEYS", json.dumps({"a":"key-a","b":"key-b"}))
    app.state.pool=Pool(); app.state.model=Model()
    app.state.meta={"threshold":.4,"model_version":"test-model"}
    # Deliberately skip lifespan: API tests use explicit isolated service doubles.
    return TestClient(app)

def payload():
    return dict(transaction_id=str(uuid4()), amount=30, hour=12, distance_km=10,
                account_age_days=50,is_international=0)

def test_auth_idempotency_and_collision(client):
    tx = payload(); h={"X-API-Key":"key-a"}
    assert client.post("/score",json=tx).status_code == 401
    first=client.post("/score",json=tx,headers=h)
    assert first.status_code == 200
    assert first.json() == client.post("/score",json=tx,headers=h).json()
    assert len(app.state.pool.rows)==1
    assert client.post("/score",json=tx|{"amount":99},headers=h).status_code==409

def test_tenant_isolation_and_missing_feedback(client):
    tx=payload()
    client.post("/score",json=tx,headers={"X-API-Key":"key-a"})
    assert client.get("/predictions",headers={"X-API-Key":"key-b"}).json()==[]
    assert client.put('/labels/'+tx['transaction_id'],json={"fraud":True},headers={"X-API-Key":"key-b"}).status_code==404
    assert client.post("/score",json=tx,headers={"X-API-Key":"key-b"}).status_code==200
    assert len(app.state.pool.rows)==2

def test_stream_feature_parity(client):
    import math
    tx=payload(); h={"X-API-Key":"key-a"}
    assert client.post("/score/enriched",json=tx|{"log_amount":0},headers=h).status_code==422
    assert client.post("/score/enriched",json=tx|{"log_amount":math.log1p(tx['amount'])},headers=h).status_code==200
