"""
RuleLock AI — AI-Based Anomaly Detection: scoring
Owner: Nihara

Merged in from the standalone anomaly-detection service's score_service.py:
same model, same threshold, called in-process instead of over HTTP.
"""
import os
import logging
import joblib
import sklearn

from features import session_to_features

MODEL_PATH = os.environ.get("MODEL_PATH", os.path.join(os.path.dirname(__file__), "model.joblib"))
ANOMALY_THRESHOLD = float(os.environ.get("ANOMALY_HOLD_THRESHOLD", os.environ.get("ANOMALY_THRESHOLD", "-0.06")))

_model = None
logger = logging.getLogger(__name__)


def _get_model():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model


def is_model_loaded():
    return _model is not None


def model_metadata():
    try:
        model = _get_model()
        metadata = getattr(model, "rulelock_metadata_", {})
    except Exception:
        logger.exception("Could not load anomaly model metadata")
        metadata = {}
    from features import FEATURE_NAMES
    return {
        "model": "IsolationForest",
        "trained_at": metadata.get("trained_at"),
        "sklearn_version": metadata.get("sklearn_version", sklearn.__version__),
        "thresholds": metadata.get("thresholds", {
            "hold": float(os.environ.get("ANOMALY_HOLD_THRESHOLD", os.environ.get("ANOMALY_THRESHOLD", "-0.06"))),
            "reject": float(os.environ.get("ANOMALY_REJECT_THRESHOLD", "-0.1")),
        }),
        "feature_ranges": metadata.get("feature_ranges"),
        "features": FEATURE_NAMES,
        "training_data": metadata.get("training_data", "synthetic; evaluation is circular"),
    }


def score_session(session_features: dict):
    """Returns (raw_score: float, is_anomaly: bool), same contract as /score used to."""
    features = session_to_features(session_features)
    raw_score = float(_get_model().decision_function(features)[0])
    return raw_score, bool(raw_score < ANOMALY_THRESHOLD)
