import mlflow.pyfunc
import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from fraudwatch.features import FEATURES


class FraudModel(mlflow.pyfunc.PythonModel):
    def load_context(self, context):
        self.model = XGBClassifier()
        self.model.load_model(context.artifacts["booster"])

    def predict(self, context, model_input, params=None):
        frame = pd.DataFrame(model_input)
        if not set(FEATURES).issubset(frame.columns):
            raise ValueError("Missing model features")
        frame = frame[FEATURES].astype(float)
        if not np.isfinite(frame.to_numpy()).all():
            raise ValueError("Features must be finite")
        return pd.DataFrame({"fraud_probability": self.model.predict_proba(frame)[:, 1]})
