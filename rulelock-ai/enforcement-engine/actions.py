"""
RuleLock AI — Component 4: automated actions
Owner: Mishen

Each function simulates the real-world action it names. In the full
system these would call payment/logistics APIs; here they return what
the action WOULD do, which is enough to prove the decision logic and
demo the flow end-to-end.
"""


def void_discount(order_id: str) -> dict:
    return {"action": "void_discount", "order_id": order_id, "status": "executed"}


def hold_cod_order(order_id: str) -> dict:
    return {"action": "hold_cod_order", "order_id": order_id, "status": "held_for_prepayment"}


def rate_limit_account(account_id: str) -> dict:
    return {"action": "rate_limit_account", "account_id": account_id, "status": "rate_limited"}
