"""At-least-once worker: persist before offset commit; idempotent DB key handles replay."""
import asyncio
import json
import logging
import os
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
import httpx
from pydantic import ValidationError
from fraudwatch.features import EnrichedTransaction

logging.basicConfig(level=logging.INFO)

async def main():
    bootstrap = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
    consumer = AIOKafkaConsumer("transactions.features", bootstrap_servers=bootstrap,
                               group_id="fraudwatch-v1", enable_auto_commit=False,
                               auto_offset_reset="earliest", max_poll_interval_ms=900000)
    producer = AIOKafkaProducer(bootstrap_servers=bootstrap, enable_idempotence=True)
    keys = json.loads(os.environ["TENANT_API_KEYS"])
    await consumer.start(); await producer.start()
    try:
        async with httpx.AsyncClient(base_url=os.getenv("API_URL", "http://api:8000"), timeout=30) as client:
            async for record in consumer:
                try:
                    event = json.loads(record.value)
                    owner = event.pop("tenant_id")
                    if owner not in keys:
                        raise ValueError("Unknown tenant")
                    EnrichedTransaction.model_validate(event)
                    for attempt in range(8):
                        try:
                            result = await client.post("/score/enriched", json=event,
                                                       headers={"X-API-Key": keys[owner]})
                            if result.status_code in (409, 422):
                                raise ValueError(f"Permanent scoring failure: {result.status_code}")
                            result.raise_for_status()
                            break
                        except (httpx.TransportError, httpx.HTTPStatusError):
                            if attempt == 7:
                                raise  # Stop without commit; restart safely replays.
                            await asyncio.sleep(min(2 ** attempt, 20))
                except (ValueError, KeyError, TypeError, ValidationError) as exc:
                    await producer.send_and_wait("transactions.dlq", json.dumps({
                        "reason": str(exc), "raw": record.value.decode(errors="replace"),
                        "partition": record.partition, "offset": record.offset}).encode())
                    logging.warning("Quarantined record partition=%s offset=%s", record.partition, record.offset)
                await consumer.commit()
    finally:
        await consumer.stop(); await producer.stop()

if __name__ == "__main__":
    asyncio.run(main())
