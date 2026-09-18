import requests

from config import ANOMALY_ENGINE_URL, ENFORCEMENT_ENGINE_URL, RULE_ENGINE_URL


def call_rule_engine(order_payload):
    if not RULE_ENGINE_URL:
        return {"available": False, "passed": False, "reason": "rule-engine is not configured"}
    try:
        response = requests.post(RULE_ENGINE_URL, json=order_payload, timeout=3)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        return {"available": False, "passed": False, "reason": f"rule-engine unreachable ({exc})"}


def call_anomaly_engine(session_features):
    if not ANOMALY_ENGINE_URL:
        return {"available": False, "raw_score": 0.0, "is_anomaly": True, "reason": "anomaly-detection is not configured"}
    try:
        response = requests.post(ANOMALY_ENGINE_URL, json=session_features, timeout=3)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        return {"available": False, "raw_score": 0.0, "is_anomaly": True, "reason": f"anomaly-detection unreachable ({exc})"}


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
        "rule_reason": "; ".join(rule_result.get("failures", [])),
        "rule_code": rule_result.get("rule_code"),
        # anomaly_score kept for logging/back-compat; decide() re-derives
        # is_anomaly from it using the SAME ANOMALY_THRESHOLD env var
        # anomaly-detection was scored with, so the two services can't
        # silently drift apart again.
        "anomaly_score": anomaly_result.get("raw_score", 0.0),
        "payment_method": payment_method,
    }
    try:
        response = requests.post(ENFORCEMENT_ENGINE_URL, json=payload, timeout=3)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        return {"available": False, "decision": "hold", "reason": f"enforcement-engine unreachable ({exc})"}