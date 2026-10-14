import numpy as np
import pandas as pd
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID

FEATURES = ["log_amount", "hour", "distance_km", "account_age_days", "is_international"]
RAW = ["amount", "hour", "distance_km", "account_age_days", "is_international"]

class Transaction(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    transaction_id: UUID
    amount: float = Field(gt=0, le=1_000_000)
    hour: int = Field(ge=0, le=23)
    distance_km: float = Field(ge=0, le=20_000)
    account_age_days: int = Field(ge=0, le=36_500)
    is_international: int = Field(ge=0, le=1)

class EnrichedTransaction(Transaction):
    log_amount: float = Field(ge=0, le=14)

class Feedback(BaseModel):
    model_config = ConfigDict(extra="forbid")
    fraud: bool


def features(frame):
    result = pd.DataFrame(frame).copy()
    result["log_amount"] = np.log1p(result["amount"])
    return result[FEATURES].astype(float)


def synthetic(n=30000, seed=42, shift=False):
    """Known synthetic process. Labels never enter feature generation or inference."""
    rng = np.random.default_rng(seed)
    frame = pd.DataFrame({
        "amount": np.minimum(rng.lognormal(3.8 + 0.5 * shift, 1.1, n), 1_000_000),
        "hour": rng.integers(0, 24, n),
        "distance_km": np.minimum(rng.exponential(80 + 150 * shift, n), 20_000),
        "account_age_days": rng.integers(0, 3650, n),
        "is_international": rng.binomial(1, 0.12 + 0.15 * shift, n),
    })
    logits = (-6.7 + 1.6 * (frame.amount > 200) + 1.2 * (frame.hour < 5)
              + 1.8 * (frame.distance_km > 200) + 2 * (frame.account_age_days < 60)
              + 1.7 * frame.is_international)
    if shift:
        # Deliberate concept change as well as covariate shift, only in demo stream.
        logits += 2.0 * (frame.amount < 70)
    frame["fraud"] = rng.binomial(1, 1 / (1 + np.exp(-logits)))
    frame["sequence"] = np.arange(n)
    return frame
