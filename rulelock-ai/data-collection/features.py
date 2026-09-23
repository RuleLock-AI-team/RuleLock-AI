"""
RuleLock AI — AI-Based Anomaly Detection: feature engineering
Owner: Nihara

Merged in from the standalone anomaly-detection service.
"""
import numpy as np

FEATURE_NAMES = [
    "coupon_attempts_per_session",
    "avg_seconds_between_requests",
    "distinct_accounts_same_device",
    "distinct_addresses_same_phone",
]

FEATURE_DEFAULTS = {
    "coupon_attempts_per_session": 0,
    "avg_seconds_between_requests": 30,
    "distinct_accounts_same_device": 1,
    "distinct_addresses_same_phone": 1,
}


def session_to_features(session: dict) -> np.ndarray:
    """
    TODO (Nihara): once real session/order history is available, compute
    these four values from it instead of expecting the caller to supply
    them pre-computed.
    """
    return np.array([[session.get(name, FEATURE_DEFAULTS[name]) for name in FEATURE_NAMES]], dtype=float)
