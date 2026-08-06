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
    if len(coupons_applied) > MAX_COUPONS_PER_SESSION:
        return RuleResult(
            False,
            f"{len(coupons_applied)} coupons applied, maximum allowed is {MAX_COUPONS_PER_SESSION}"
        )

    return RuleResult(True)


def check_discount_range(discount_value: float) -> RuleResult:
    if discount_value < VALID_DISCOUNT_RANGE[0] or discount_value > VALID_DISCOUNT_RANGE[1]:
        return RuleResult(
            False,
            f"discount {discount_value} is outside allowed range {VALID_DISCOUNT_RANGE}"
        )

    return RuleResult(True)


def check_quantity_ceiling(sku: str, quantity: int) -> RuleResult:
    if quantity > MAX_QUANTITY_PER_SKU:
        return RuleResult(False, f"quantity {quantity} exceeds ceiling {MAX_QUANTITY_PER_SKU} for {sku}")
    return RuleResult(True)


def check_minimum_purchase(subtotal: float) -> RuleResult:
    if subtotal < MIN_PURCHASE_AMOUNT:
        return RuleResult(False, f"subtotal {subtotal} below minimum {MIN_PURCHASE_AMOUNT}")
    return RuleResult(True)


def check_cod_order_value(total: float, account_verified: bool) -> RuleResult:
    """
    Unverified accounts cannot place high-value COD orders.
    """

    if not account_verified and total > COD_UNVERIFIED_ORDER_CAP:
        return RuleResult(
            False,
            f"COD order value {total} exceeds unverified account limit {COD_UNVERIFIED_ORDER_CAP}"
        )

    return RuleResult(True)

def check_cod_refusal_rate(past_orders: int, past_refusals: int) -> RuleResult:
    """
    Detect users with high COD refusal rate.
    """

    if past_orders == 0:
        return RuleResult(True)

    refusal_rate = past_refusals / past_orders

    if refusal_rate > COD_REFUSAL_RATE_THRESHOLD:
        return RuleResult(
            False,
            f"COD refusal rate {refusal_rate:.2f} exceeds threshold {COD_REFUSAL_RATE_THRESHOLD}"
        )

    return RuleResult(True)

def validate_transaction(transaction: dict) -> dict:

    failures = []

    results = [
        check_coupon_usage(
            transaction.get("coupons_applied", [])
        ),

        check_discount_range(
            transaction.get("discount_value", 0)
        ),

        check_quantity_ceiling(
            transaction.get("sku", "unknown"),
            transaction.get("quantity", 0)
        ),

        check_minimum_purchase(
            transaction.get("subtotal", 0)
        ),

        check_cod_order_value(
            transaction.get("total", 0),
            transaction.get("account_verified", False)
        ),

        check_cod_refusal_rate(
            transaction.get("past_orders", 0),
            transaction.get("past_refusals", 0)
        )
    ]

    for result in results:
        if not result.passed:
            failures.append(result.reason)

    return {
        "passed": len(failures) == 0,
        "failures": failures
    }
   
