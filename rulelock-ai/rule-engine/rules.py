"""
RuleLock AI — Component 2: Business Rule Validation Engine
Owner: Sadini

Each rule is an independent function returning a RuleResult — this
mirrors the "declarative rule list" pattern rather than one big
if/else block, so rules stay independently testable.
"""
from dataclasses import dataclass

MAX_COUPONS_PER_SESSION = 1
VALID_DISCOUNT_RANGE = (0, 5000)       # LKR
MAX_QUANTITY_PER_SKU = 10
MIN_PURCHASE_AMOUNT = 500              # LKR
COD_UNVERIFIED_ORDER_CAP = 15000       # LKR
COD_REFUSAL_RATE_THRESHOLD = 0.5       # share of a phone/address's past COD orders refused


@dataclass
class RuleResult:
    passed: bool
    reason: str = ""


def check_coupon_usage(coupons_applied: list[str]) -> RuleResult:
    """TODO (Sadini): flag orders applying more coupons than MAX_COUPONS_PER_SESSION."""
    raise NotImplementedError


def check_discount_range(discount_value: float) -> RuleResult:
    """TODO (Sadini): flag discounts outside VALID_DISCOUNT_RANGE."""
    raise NotImplementedError


def check_quantity_ceiling(sku: str, quantity: int) -> RuleResult:
    if quantity > MAX_QUANTITY_PER_SKU:
        return RuleResult(False, f"quantity {quantity} exceeds ceiling {MAX_QUANTITY_PER_SKU} for {sku}")
    return RuleResult(True)


def check_minimum_purchase(subtotal: float) -> RuleResult:
    if subtotal < MIN_PURCHASE_AMOUNT:
        return RuleResult(False, f"subtotal {subtotal} below minimum {MIN_PURCHASE_AMOUNT}")
    return RuleResult(True)


def check_cod_order_value(total: float, account_verified: bool) -> RuleResult:
    """TODO (Sadini): unverified accounts placing COD orders above COD_UNVERIFIED_ORDER_CAP should fail."""
    raise NotImplementedError


def check_cod_refusal_rate(past_orders: int, past_refusals: int) -> RuleResult:
    """TODO (Sadini): flag phone/address combos whose refusal rate exceeds COD_REFUSAL_RATE_THRESHOLD."""
    raise NotImplementedError


def validate_transaction(transaction: dict) -> dict:
    """
    Runs every rule against a transaction dict and returns a combined
    result — this is what POST /validate exposes to the enforcement engine.

    TODO (Sadini): call each check_* function above with the right
    fields out of `transaction`, and aggregate into:
        {"passed": bool, "failures": [reason, ...]}
    """
    raise NotImplementedError
