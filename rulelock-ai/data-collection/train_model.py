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
import joblib
from sklearn.ensemble import IsolationForest
from synthetic_data import generate_normal_sessions

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.joblib")


def train():
    # IsolationForest is trained unsupervised, on normal sessions only.
    # Abuse sessions are intentionally NOT used for training - they are
    # reserved for evaluating whether the model, trained purely on what
    # "normal" looks like, correctly flags abuse as anomalous.
    normal = generate_normal_sessions()
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(normal)
    joblib.dump(model, MODEL_PATH)
    return model


if __name__ == "__main__":
    train()
    print(f"Saved {MODEL_PATH}")
