"""Enforcement policy translating detections into contract decisions."""
import os

from actions import void_discount, hold_cod_order, rate_limit_account

ANOMALY_HOLD_THRESHOLD = float(os.environ.get("ANOMALY_HOLD_THRESHOLD", "-0.06"))
ANOMALY_REJECT_THRESHOLD = float(os.environ.get("ANOMALY_REJECT_THRESHOLD", "-0.1"))

RULE_ACTION_MAP = {
    "coupon_usage": "void_discount",
    "discount_range": "void_discount",
    "coupon_velocity": "void_discount",
    "minimum_purchase": "void_discount",
    "quantity_ceiling": "reject",
    "price_mismatch": "reject",
    "cod_order_value": "hold",
    "cod_abuse": "hold",
    "cod_abuse_severe": "reject",
}


def decide(order_id, account_id, rule_passed, rule_reason, anomaly_score, payment_method, rule_code=None, violations=None):
    if not rule_passed:
        if violations:
            severity = {"reject": 3, "hold": 2, "void_discount": 1}
            rule_code = max(violations, key=lambda violation: severity.get(RULE_ACTION_MAP.get(violation.get("code"), "hold"), 2)).get("code", rule_code)
        action = RULE_ACTION_MAP.get(rule_code, "hold")
        if action == "void_discount":
            execution = void_discount(order_id)
        elif action == "reject":
            execution = {"action": "reject_order"}
        else:
            execution = hold_cod_order(order_id)
        return {"decision": action, "reason": rule_reason, "rule_code": rule_code, **execution}

    if anomaly_score < ANOMALY_REJECT_THRESHOLD:
        return {"decision": "reject", "reason": "anomaly score indicates elevated risk",
                "account_action": {"type": "rate_limit", "minutes": 30},
                **rate_limit_account(account_id)}
    if anomaly_score < ANOMALY_HOLD_THRESHOLD:
        return {"decision": "hold", "reason": "anomaly score requires review",
                **hold_cod_order(order_id)}
    return {"decision": "accept", "reason": "passed all checks", "action": "none"}
