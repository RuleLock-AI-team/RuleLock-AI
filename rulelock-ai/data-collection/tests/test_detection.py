import os
import sys
from datetime import datetime, timedelta, timezone

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from features import FEATURE_NAMES, average_seconds_between_requests, session_to_features
from synthetic_data import generate_abuse_sessions, generate_normal_sessions
from sklearn.ensemble import IsolationForest


def _score_model_fixture_set():
    model = IsolationForest(contamination=0.03, random_state=42).fit(generate_normal_sessions(n=5000))
    cases = {
        "slow_normal": [0, 420, 1, 1],
        "typical_cakely": [1, 18, 1, 1],
    }
    scores = {name: model.decision_function(session_to_features(dict(zip(FEATURE_NAMES, values))))[0]
              for name, values in cases.items()}
    return model, scores


def test_slow_and_typical_sessions_are_not_anomalous():
    model, scores = _score_model_fixture_set()
    assert scores["slow_normal"] >= -0.06
    assert scores["typical_cakely"] >= -0.06


def test_existing_abuse_fixture_distribution_remains_anomalous():
    model = IsolationForest(contamination=0.03, random_state=42).fit(generate_normal_sessions(n=5000))
    abuse = generate_abuse_sessions(n=50)
    scored = np.vstack([session_to_features(dict(zip(FEATURE_NAMES, row)))[0] for row in abuse])
    assert (model.decision_function(scored) < -0.06).mean() >= 0.8


def test_session_average_uses_recent_events_and_requires_three():
    now = datetime(2026, 10, 3, 12, tzinfo=timezone.utc)
    rows = [
        {"created_at": (now - timedelta(hours=1)).isoformat()},
        {"created_at": (now - timedelta(minutes=2)).isoformat()},
        {"created_at": (now - timedelta(minutes=1)).isoformat()},
    ]
    assert average_seconds_between_requests(rows, now=now) == 30
    recent = [
        {"created_at": (now - timedelta(minutes=3)).isoformat()},
        {"created_at": (now - timedelta(minutes=2)).isoformat()},
        {"created_at": (now - timedelta(minutes=1)).isoformat()},
    ]
    assert average_seconds_between_requests(recent, now=now) == 60


def test_features_are_clipped_to_training_ranges():
    values = session_to_features({"coupon_attempts_per_session": 999, "avg_seconds_between_requests": 9999,
                                  "distinct_accounts_same_device": 99, "distinct_addresses_same_phone": 0})[0]
    assert values.tolist() == [15.0, 600.0, 8.0, 1.0]
