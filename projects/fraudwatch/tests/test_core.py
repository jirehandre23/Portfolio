import numpy as np
import pytest
from pydantic import ValidationError
from uuid import uuid4
from fraudwatch.features import Transaction, synthetic, features, FEATURES
from fraudwatch.metrics import evaluate, choose_threshold, psi


def test_no_label_leakage_and_reproducibility():
    data = synthetic(1000)
    assert data.equals(synthetic(1000))
    x = features(data)
    assert list(x.columns) == FEATURES
    assert "fraud" not in x and "sequence" not in x
    np.testing.assert_allclose(x.log_amount, np.log1p(data.amount))

@pytest.mark.parametrize("field,value", [("amount",-1), ("amount",float('nan')),
                                         ("hour",24), ("is_international",2)])
def test_bad_requests_rejected(field,value):
    data = dict(transaction_id=str(uuid4()), amount=30, hour=12, distance_km=10,
                account_age_days=50, is_international=0)
    data[field] = value
    with pytest.raises(ValidationError):
        Transaction(**data)


def test_metric_guards_and_correct_counts():
    assert evaluate([0,0], [.2,.3], .5)["status"] == "insufficient_classes"
    result = evaluate([0,0,1,1], [.1,.8,.2,.9], .5)
    assert result["false_positives"] == result["false_negatives"] == 1
    assert result["illustrative_cost"] == 105


def test_threshold_and_drift():
    y = np.array([0,0,1,1]); p = np.array([.01,.02,.4,.8])
    t = choose_threshold(y,p)
    assert .02 < t <= .4
    assert psi(np.arange(100), np.arange(100)) == 0
    assert psi(np.arange(100), np.arange(100)+1000) > .2
    assert psi([],[]) is None
