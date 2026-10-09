"""
RuleLock AI — Component 3: model training
Owner: Nihara

TODO: swap generate_normal_sessions() for a real public e-commerce
dataset once sourced (Kaggle etc.) — synthetic data here is the stated
placeholder, not the final approach.

Merged in from the standalone anomaly-detection service; runs at Docker
build time so model.joblib ships inside the single backend image.
"""
import os
from datetime import datetime, timezone

import joblib
import sklearn
from sklearn.ensemble import IsolationForest
from features import TRAINING_RANGES
from synthetic_data import generate_normal_sessions

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.joblib")
ANOMALY_HOLD_THRESHOLD = float(os.environ.get("ANOMALY_HOLD_THRESHOLD", "-0.06"))
ANOMALY_REJECT_THRESHOLD = float(os.environ.get("ANOMALY_REJECT_THRESHOLD", "-0.1"))


def train():
    # IsolationForest is trained unsupervised, on normal sessions only.
    # Abuse sessions are intentionally NOT used for training - they are
    # reserved for evaluating whether the model, trained purely on what
    # "normal" looks like, correctly flags abuse as anomalous.
    normal = generate_normal_sessions(n=5000)
    model = IsolationForest(contamination=0.03, random_state=42)
    model.fit(normal)
    model.rulelock_metadata_ = {
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "sklearn_version": sklearn.__version__,
        "thresholds": {
            "hold": ANOMALY_HOLD_THRESHOLD,
            "reject": ANOMALY_REJECT_THRESHOLD,
        },
        "feature_ranges": TRAINING_RANGES,
        "training_data": "synthetic normal sessions; evaluation is synthetic and circular",
    }
    joblib.dump(model, MODEL_PATH)
    return model


if __name__ == "__main__":
    train()
    print(f"Saved {MODEL_PATH}")
