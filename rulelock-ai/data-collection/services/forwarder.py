"""
In-process versions of the rule/anomaly/enforcement steps.

These used to be HTTP calls to three separate Render services. Now that
everything runs in one backend, a cold start or network hiccup between
components can no longer cause a false "unreachable" hold — it's just a
Python function call. Function names/signatures are kept identical to the
old HTTP-calling versions so routes/events.py (and its tests, which
monkeypatch these three names) don't need to change.
"""
from rules import validate_transaction
from anomaly_scoring import score_session
from decision import decide


def call_rule_engine(order_payload):
    try:
        return validate_transaction(order_payload)
    except Exception as exc:
        return {"available": False, "passed": False, "reason": f"rule validation error ({exc})"}


def call_anomaly_engine(session_features):
    try:
        raw_score, is_anomaly = score_session(session_features)
        return {"raw_score": raw_score, "is_anomaly": is_anomaly}
    except Exception as exc:
        return {"available": False, "raw_score": 0.0, "is_anomaly": True, "reason": f"anomaly scoring error ({exc})"}


def call_enforcement_engine(order_id, account_id, rule_result, anomaly_result, payment_method):
    try:
        return decide(
            order_id=order_id,
            account_id=account_id,
            rule_passed=rule_result.get("passed", True),
            rule_reason="; ".join(rule_result.get("failures", [])) or rule_result.get("reason", ""),
            anomaly_score=anomaly_result.get("raw_score", 0.0),
            payment_method=payment_method,
            rule_code=rule_result.get("rule_code"),
        )
    except Exception as exc:
        return {"available": False, "decision": "hold", "reason": f"enforcement error ({exc})"}

