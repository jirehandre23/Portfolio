import numpy as np
from sklearn.metrics import (average_precision_score, roc_auc_score, precision_score,
                             recall_score, confusion_matrix)


def evaluate(y, probability, threshold):
    y, p = np.asarray(y), np.asarray(probability)
    if len(y) == 0 or len(np.unique(y)) < 2:
        return {"status": "insufficient_classes", "n": len(y)}
    predicted = p >= threshold
    tn, fp, fn, tp = confusion_matrix(y, predicted, labels=[0, 1]).ravel()
    return {"status": "ok", "n": len(y), "prevalence": float(y.mean()),
            "roc_auc": float(roc_auc_score(y, p)),
            "average_precision": float(average_precision_score(y, p)),
            "precision": float(precision_score(y, predicted, zero_division=0)),
            "recall": float(recall_score(y, predicted, zero_division=0)),
            "false_positives": int(fp), "false_negatives": int(fn),
            "true_positives": int(tp), "true_negatives": int(tn),
            "illustrative_cost": int(5 * fp + 100 * fn)}


def choose_threshold(y, probability):
    """Optimize illustrative costs on VALIDATION data only; never on test data."""
    candidates = np.linspace(0.01, 0.99, 99)
    costs = [5 * np.sum((probability >= t) & (y == 0)) +
             100 * np.sum((probability < t) & (y == 1)) for t in candidates]
    return float(candidates[np.argmin(costs)])


def psi(reference, current):
    """Population stability index with reference-derived bins and tail coverage."""
    reference, current = np.asarray(reference), np.asarray(current)
    if len(reference) == 0 or len(current) == 0:
        return None
    bins = np.unique(np.quantile(reference, np.linspace(0, 1, 11)))
    if len(bins) < 2:
        bins = np.array([-np.inf, float(reference[0]), np.inf])
    else:
        bins[0], bins[-1] = -np.inf, np.inf
    a = np.histogram(reference, bins)[0] / len(reference)
    b = np.histogram(current, bins)[0] / len(current)
    a, b = np.clip(a, 1e-6, None), np.clip(b, 1e-6, None)
    return float(np.sum((b - a) * np.log(b / a)))
