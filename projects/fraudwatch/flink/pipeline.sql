SET 'execution.runtime-mode' = 'streaming';
SET 'execution.checkpointing.interval' = '10 s';
SET 'execution.checkpointing.mode' = 'AT_LEAST_ONCE';
SET 'parallelism.default' = '1';
SET 'table.dml-sync' = 'false';

CREATE TABLE raw_transactions (
 tenant_id STRING, transaction_id STRING, amount DOUBLE, `hour` INT,
 distance_km DOUBLE, account_age_days INT, is_international INT
) WITH (
 'connector'='kafka', 'topic'='transactions.raw',
 'properties.bootstrap.servers'='kafka:9092',
 'properties.group.id'='flink-feature-transform-v1',
 'scan.startup.mode'='earliest-offset', 'format'='json',
 'json.fail-on-missing-field'='true', 'json.ignore-parse-errors'='false'
);

CREATE TABLE enriched_transactions (
 tenant_id STRING, transaction_id STRING, amount DOUBLE, `hour` INT,
 distance_km DOUBLE, account_age_days INT, is_international INT, log_amount DOUBLE
) WITH (
 'connector'='kafka', 'topic'='transactions.features',
 'properties.bootstrap.servers'='kafka:9092', 'format'='json',
 'sink.delivery-guarantee'='at-least-once'
);

INSERT INTO enriched_transactions
SELECT tenant_id, transaction_id, amount, `hour`, distance_km,
       account_age_days, is_international, LN(1.0 + amount)
FROM raw_transactions;
