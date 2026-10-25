
import joblib
import pandas as pd

from memory.smart_forgetting.config import (
    MODEL_PATH,
    CONFIDENCE_THRESHOLD,
)


class SmartForgettingModel:
    def __init__(self):
        if not MODEL_PATH.is_file():
            raise FileNotFoundError(
                f"Smart Forgetting model not found: {MODEL_PATH}"
            )

        self.bundle = joblib.load(MODEL_PATH)
        self.pipeline = self.bundle["pipeline"]
        self.feature_columns = self.bundle["feature_columns"]

    def predict(self, features: dict) -> dict:
        missing = [
            col for col in self.feature_columns
            if col not in features
        ]

        if missing:
            raise ValueError(
                f"Missing model features: {missing}"
            )

        row = pd.DataFrame(
            [{col: features[col] for col in self.feature_columns}],
            columns=self.feature_columns,
        )

        prediction = str(self.pipeline.predict(row)[0])

        probabilities = None
        confidence = None

        if hasattr(self.pipeline, "predict_proba"):
            probabilities = self.pipeline.predict_proba(row)[0]
            confidence = float(max(probabilities))

        return {
            "label": prediction,
            "confidence": confidence,
            "needs_llm_fallback": (
                confidence is None
                or confidence < CONFIDENCE_THRESHOLD
            ),
        }
