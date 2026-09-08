import requests

from config import ANOMALY_ENGINE_URL, RULE_ENGINE_URL


def call_rule_engine(order_payload):
    if not RULE_ENGINE_URL:
        return {"passed": True, "reason": "stub: rule-engine not connected yet"}
    try:
        response = requests.post(RULE_ENGINE_URL, json=order_payload, timeout=3)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        return {"passed": True, "reason": f"stub: rule-engine unreachable ({exc})"}


def call_anomaly_engine(session_features):
    if not ANOMALY_ENGINE_URL:
        return {"anomaly_score": 0.0, "reason": "stub: anomaly-detection not connected yet"}
    try:
        response = requests.post(ANOMALY_ENGINE_URL, json=session_features, timeout=3)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        return {"anomaly_score": 0.0, "reason": f"stub: anomaly-detection unreachable ({exc})"}
