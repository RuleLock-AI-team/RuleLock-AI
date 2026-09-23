"""
RuleLock AI — AI-Based Anomaly Detection: scoring
Owner: Nihara

Merged in from the standalone anomaly-detection service's score_service.py:
same model, same threshold, called in-process instead of over HTTP.
"""
import os
import joblib

from features import session_to_features

MODEL_PATH = os.environ.get("MODEL_PATH", os.path.join(os.path.dirname(__file__), "model.joblib"))
ANOMALY_THRESHOLD = float(os.environ.get("ANOMALY_THRESHOLD", "-0.06"))

_model = None


def _get_model():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model


def score_session(session_features: dict):
    """Returns (raw_score: float, is_anomaly: bool), same contract as /score used to."""
    features = session_to_features(session_features)
    raw_score = float(_get_model().decision_function(features)[0])
    return raw_score, bool(raw_score < ANOMALY_THRESHOLD)
