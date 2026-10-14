"""Submit synthetic traffic; reveal labels later, never in the scoring request."""
import argparse
import asyncio
import os
from uuid import uuid4
import httpx
from fraudwatch.features import synthetic, RAW

async def run(count, shift):
    data = synthetic(count, seed=73 if shift else 64, shift=shift)
    headers = {"X-API-Key": os.environ["DEMO_API_KEY"]}
    async with httpx.AsyncClient(base_url=os.getenv("API_URL", "http://api:8000"), headers=headers, timeout=30) as client:
        labels = []
        for _, row in data.iterrows():
            tx = {k: float(row[k]) if k in ("amount", "distance_km") else int(row[k]) for k in RAW}
            tx["transaction_id"] = str(uuid4())
            r = await client.post("/transactions", json=tx); r.raise_for_status()
            labels.append((tx["transaction_id"], bool(row.fraud)))
        # Retry only missing predictions; stream processing may still be catching up.
        for attempt in range(120):
            pending = []
            for identifier, label in labels:
                r = await client.put(f"/labels/{identifier}", json={"fraud": label})
                if r.status_code == 404:
                    pending.append((identifier, label))
                else:
                    r.raise_for_status()
            labels = pending
            if not labels:
                print(f"Scored and labeled {count} synthetic transactions (shift={shift})")
                return
            await asyncio.sleep(2)
        raise RuntimeError(f"{len(labels)} events were not scored. Check Flink and worker logs.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--count", type=int, default=500)
    parser.add_argument("--shift", action="store_true"); args = parser.parse_args()
    asyncio.run(run(args.count, args.shift))
