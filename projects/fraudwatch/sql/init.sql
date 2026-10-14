CREATE TABLE IF NOT EXISTS predictions (
 tenant_id TEXT NOT NULL,
 transaction_id UUID NOT NULL,
 payload_hash TEXT NOT NULL,
 features JSONB NOT NULL,
 probability DOUBLE PRECISION NOT NULL CHECK (probability BETWEEN 0 AND 1),
 decision BOOLEAN NOT NULL,
 threshold DOUBLE PRECISION NOT NULL,
 model_version TEXT NOT NULL,
 created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
 label BOOLEAN,
 labeled_at TIMESTAMPTZ,
 PRIMARY KEY (tenant_id, transaction_id)
);
CREATE INDEX IF NOT EXISTS predictions_tenant_time ON predictions(tenant_id, created_at DESC);
