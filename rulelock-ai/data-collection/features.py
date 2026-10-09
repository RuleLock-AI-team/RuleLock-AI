"""Feature extraction for the in-process anomaly model."""
from datetime import datetime, timedelta, timezone

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
# These are explicit bounds used by both training and scoring. The wider
# cross-account bounds preserve the signal while preventing wild input values.
TRAINING_RANGES = {
    "coupon_attempts_per_session": (0.0, 15.0),
    "avg_seconds_between_requests": (1.0, 600.0),
    "distinct_accounts_same_device": (1.0, 8.0),
    "distinct_addresses_same_phone": (1.0, 8.0),
}


def recent_session_events(rows, now=None):
    """Keep session events from the trailing 30 minutes with parseable times."""
    now = now or datetime.now(timezone.utc)
    cutoff = now - timedelta(minutes=30)
    selected = []
    for row in rows or []:
        value = row.get("created_at")
        if not value:
            continue
        try:
            stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if stamp.tzinfo is None:
                stamp = stamp.replace(tzinfo=timezone.utc)
        except (TypeError, ValueError):
            continue
        if cutoff <= stamp <= now:
            selected.append((stamp, row))
    return sorted(selected, key=lambda item: item[0])


def average_seconds_between_requests(rows, now=None):
    recent = recent_session_events(rows, now)
    if len(recent) < 3:
        return FEATURE_DEFAULTS["avg_seconds_between_requests"]
    elapsed = (recent[-1][0] - recent[0][0]).total_seconds()
    return max(elapsed / (len(recent) - 1), 0.0)


def session_to_features(session: dict) -> np.ndarray:
    values = []
    for name in FEATURE_NAMES:
        value = session.get(name, FEATURE_DEFAULTS[name])
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            numeric = float(FEATURE_DEFAULTS[name])
        if not np.isfinite(numeric):
            numeric = float(FEATURE_DEFAULTS[name])
        low, high = TRAINING_RANGES[name]
        values.append(float(np.clip(numeric, low, high)))
    return np.asarray([values], dtype=float)
