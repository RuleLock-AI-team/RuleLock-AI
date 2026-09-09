"""
RuleLock AI — Component 3: model training
Owner: Nihara

TODO: swap generate_normal_sessions() for a real public e-commerce
dataset once sourced (Kaggle etc. — see README) — synthetic data here
is the stated placeholder, not the final approach.
"""
import joblib
from sklearn.ensemble import IsolationForest
from synthetic_data import generate_normal_sessions


def train():
    # IsolationForest is trained unsupervised, on normal sessions only.
    # Abuse sessions are intentionally NOT used for training - they are
    # reserved for evaluate.py to test whether the model, trained purely
    # on what "normal" looks like, correctly flags abuse as anomalous.
    # This mirrors how the model would work in production, where labelled
    # abuse examples are scarce and normal behaviour is what's available.
    normal = generate_normal_sessions()
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(normal)
    joblib.dump(model, "model.joblib")
    return model


if __name__ == "__main__":
    train()
    print("Saved model.joblib")
