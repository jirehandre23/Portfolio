"""Reproducible training, validation-only decision threshold, untouched test set."""
import json
import os
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mlflow
import mlflow.pyfunc
import numpy as np
from mlflow.models import infer_signature
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import RocCurveDisplay, PrecisionRecallDisplay
from xgboost import XGBClassifier
from fraudwatch.features import synthetic, features, FEATURES
from fraudwatch.metrics import evaluate, choose_threshold
from fraudwatch.model import FraudModel


def main():
    out = Path(os.getenv("ARTIFACT_DIR", "artifacts")); out.mkdir(exist_ok=True)
    reports = Path("reports"); reports.mkdir(exist_ok=True)
    data = synthetic()
    # Ordered split, no shuffling and no fitting on validation/test rows.
    train, val, test = data.iloc[:18000], data.iloc[18000:24000], data.iloc[24000:]
    x, xv, xt = map(features, (train, val, test))
    model = XGBClassifier(n_estimators=180, max_depth=3, learning_rate=.05,
                          subsample=.85, colsample_bytree=.9, objective="binary:logistic",
                          eval_metric="aucpr", random_state=42, n_jobs=2)
    model.fit(x, train.fraud)
    threshold = choose_threshold(val.fraud.to_numpy(), model.predict_proba(xv)[:, 1])
    p = model.predict_proba(xt)[:, 1]
    baseline = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
    baseline.fit(x, train.fraud)
    bp = baseline.predict_proba(xt)[:, 1]
    bt = choose_threshold(val.fraud.to_numpy(), baseline.predict_proba(xv)[:, 1])
    report = {"dataset": "Synthetic only; not evidence of real-world fraud performance",
              "seed": 42, "split": {"train": 18000, "validation": 6000, "test": 6000},
              "cost_assumption": {"false_positive": 5, "false_negative": 100},
              "threshold": threshold, "xgboost": evaluate(test.fraud, p, threshold),
              "logistic_regression": evaluate(test.fraud, bp, bt),
              "always_allow": evaluate(test.fraud, np.zeros(len(test)), 0.5)}
    (reports / "evaluation.json").write_text(json.dumps(report, indent=2))
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    RocCurveDisplay.from_predictions(test.fraud, p, name="XGBoost", ax=axes[0])
    PrecisionRecallDisplay.from_predictions(test.fraud, p, name="XGBoost", ax=axes[1])
    axes[1].axhline(test.fraud.mean(), linestyle="--", color="gray", label="Prevalence")
    axes[1].legend(); fig.suptitle("FraudWatch • synthetic held-out evaluation")
    fig.tight_layout(); fig.savefig(reports / "evaluation.svg"); plt.close(fig)
    model.save_model(out / "booster.json")
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "sqlite:///artifacts/mlflow.db"))
    if mlflow.get_experiment_by_name("fraudwatch-synthetic") is None:
        mlflow.create_experiment("fraudwatch-synthetic", artifact_location=str((out / "runs").resolve()))
    mlflow.set_experiment("fraudwatch-synthetic")
    with mlflow.start_run() as run:
        mlflow.log_params({"seed": 42, "threshold": threshold, "data": "synthetic", "features": FEATURES})
        mlflow.log_metrics({k: v for k, v in report["xgboost"].items() if isinstance(v, (float, int))})
        # Use a DataFrame output signature matching the actual pyfunc wrapper.
        import pandas as pd
        signature = infer_signature(x.head(), pd.DataFrame({"fraud_probability": model.predict_proba(x.head())[:, 1]}))
        kwargs = dict(python_model=FraudModel(), artifacts={"booster": str(out / "booster.json")},
                      signature=signature, input_example=x.head(), code_paths=["fraudwatch"],
                      pip_requirements=["mlflow==2.22.0", "xgboost==2.1.4", "pandas==2.2.3", "numpy==1.26.4"])
        mlflow.pyfunc.log_model(artifact_path="model", **kwargs)
        import shutil
        shutil.rmtree(out / "model", ignore_errors=True)
        mlflow.pyfunc.save_model(path=str(out / "model"), **kwargs)
        mlflow.log_artifacts(str(reports), artifact_path="evaluation")
        metadata = {"model_version": run.info.run_id, "threshold": threshold, "test": report["xgboost"]}
        (out / "metadata.json").write_text(json.dumps(metadata))
    x.head(2000).to_csv(out / "reference.csv", index=False)
    # Round-trip check validates the packaged artifact, not just the estimator.
    loaded = mlflow.pyfunc.load_model(str(out / "model"))
    assert np.allclose(loaded.predict(xt.head())["fraud_probability"], p[:5])
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
