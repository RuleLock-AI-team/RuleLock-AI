import time

import requests

from config import ANOMALY_ENGINE_URL, ENFORCEMENT_ENGINE_URL, RULE_ENGINE_URL

# Render's free plan spins services down when idle, so the first request
# after a cold start can legitimately take several seconds — a 3s timeout
# with no retry was misreporting cold starts as "unreachable" and holding
# every order. One retry with a longer timeout gives the cold start a
# chance to finish instead of failing on the very first probe.
REQUEST_TIMEOUT = 10
RETRY_DELAY_SECONDS = 2


def _post_with_retry(url, payload):
    last_exc = None
    for attempt in range(2):
        try:
            response = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.json(), None
        except requests.RequestException as exc:
            last_exc = exc
            if attempt == 0:
                time.sleep(RETRY_DELAY_SECONDS)
    return None, last_exc


def call_rule_engine(order_payload):
    if not RULE_ENGINE_URL:
        return {"available": False, "passed": False, "reason": "rule-engine is not configured"}
    result, exc = _post_with_retry(RULE_ENGINE_URL, order_payload)
    if exc is not None:
        return {"available": False, "passed": False, "reason": f"rule-engine unreachable ({exc})"}
    return result


def call_anomaly_engine(session_features):
    if not ANOMALY_ENGINE_URL:
        return {"available": False, "raw_score": 0.0, "is_anomaly": True, "reason": "anomaly-detection is not configured"}
    result, exc = _post_with_retry(ANOMALY_ENGINE_URL, session_features)
    if exc is not None:
        return {"available": False, "raw_score": 0.0, "is_anomaly": True, "reason": f"anomaly-detection unreachable ({exc})"}
    return result


def call_enforcement_engine(order_id, account_id, rule_result, anomaly_result, payment_method):
    """
    Closes the loop the proposal's own Figure 2 describes: data-collection
    calls /enforce with BOTH upstream results so decide() actually
    determines what happens to the order, instead of the caller only
    seeing the raw rule/anomaly results and no decision.
    """
    if not ENFORCEMENT_ENGINE_URL:
        return {"available": False, "decision": "hold", "reason": "enforcement-engine is not configured"}
    payload = {
        "order_id": order_id,
        "account_id": account_id,
        "rule_passed": rule_result.get("passed", True),
        "rule_reason": "; ".join(rule_result.get("failures", [])) or rule_result.get("reason", ""),
        "rule_code": rule_result.get("rule_code"),
        # anomaly_score kept for logging/back-compat; decide() re-derives
        # is_anomaly from it using the SAME ANOMALY_THRESHOLD env var
        # anomaly-detection was scored with, so the two services can't
        # silently drift apart again.
        "anomaly_score": anomaly_result.get("raw_score", 0.0),
        "payment_method": payment_method,
    }
    result, exc = _post_with_retry(ENFORCEMENT_ENGINE_URL, payload)
    if exc is not None:
        return {"available": False, "decision": "hold", "reason": f"enforcement-engine unreachable ({exc})"}
    return result
