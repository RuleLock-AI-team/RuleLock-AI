"""
RuleLock AI — Component 4: decision logic
Owner: Mishen

Takes the Rule Validation Engine's result and the Anomaly Detection
model's score, and decides which automated action (if any) to take.
This is the actual "brain" of the enforcement engine.
"""
from actions import void_discount, hold_cod_order, rate_limit_account

ANOMALY_THRESHOLD = -0.1  # IsolationForest decision_function: below this = high-confidence abuse


def decide(order_id: str, account_id: str, rule_passed: bool, rule_reason: str,
           anomaly_score: float, payment_method: str) -> dict:
    """
    TODO (Mishen): this is deliberately the simplest possible version —
    one rule failure or one anomaly breach triggers one action. The real
    coursework is making this smarter: e.g. distinguishing WHICH rule
    failed to choose void_discount vs. rate_limit_account, and combining
    the rule and anomaly signals instead of treating them independently.
    """
    if not rule_passed:
        return {"decision": "void_discount", "reason": rule_reason, **void_discount(order_id)}

    if anomaly_score < ANOMALY_THRESHOLD:
        if payment_method == "COD":
            return {"decision": "hold_cod_order", "reason": "anomaly score below threshold",
                     **hold_cod_order(order_id)}
        return {"decision": "rate_limit_account", "reason": "anomaly score below threshold",
                **rate_limit_account(account_id)}

    return {"decision": "none", "reason": "passed all checks"}
