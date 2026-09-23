"""
RuleLock AI — Automated Enforcement Engine: decision logic
Owner: Mishen

Merged in from the standalone enforcement-engine service.
"""
import os

from actions import void_discount, hold_cod_order, rate_limit_account

# IsolationForest decision_function: below this = high-confidence abuse.
# MUST match anomaly_scoring.py's own ANOMALY_THRESHOLD (the value Nihara
# calibrated with evaluate.py's precision/recall analysis — -0.06, not an
# independent guess here). Both read the same env var so they can't
# silently disagree on what counts as anomalous.
ANOMALY_THRESHOLD = float(os.environ.get("ANOMALY_THRESHOLD", "-0.06"))

RULE_ACTION_MAP = {
    "coupon_usage": "void_discount",
    "discount_range": "void_discount",
    "quantity_ceiling": "void_discount",
    "minimum_purchase": "void_discount",
    "cod_order_value": "hold_cod_order",
    "cod_refusal_rate": "hold_cod_order",
}


def _run_rule_action(action_name: str, order_id: str) -> dict:
    if action_name == "hold_cod_order":
        return hold_cod_order(order_id)
    return void_discount(order_id)


def decide(order_id: str, account_id: str, rule_passed: bool, rule_reason: str,
           anomaly_score: float, payment_method: str, rule_code: str = None) -> dict:
    if not rule_passed:
        action_name = RULE_ACTION_MAP.get(rule_code, "void_discount")
        return {
            "decision": action_name,
            "reason": rule_reason,
            "rule_code": rule_code,
            **_run_rule_action(action_name, order_id),
        }

    if anomaly_score < ANOMALY_THRESHOLD:
        if payment_method == "COD":
            return {"decision": "hold_cod_order", "reason": "anomaly score below threshold",
                     **hold_cod_order(order_id)}
        return {"decision": "rate_limit_account", "reason": "anomaly score below threshold",
                **rate_limit_account(account_id)}

    return {"decision": "none", "reason": "passed all checks"}
