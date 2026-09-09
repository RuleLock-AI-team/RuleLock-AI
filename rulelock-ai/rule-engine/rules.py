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
            f"applied {len(coupons_applied)} coupons; limit is {MAX_COUPONS_PER_SESSION}",
        )
    return RuleResult(True)


def check_discount_range(discount_value: float) -> RuleResult:
    if not VALID_DISCOUNT_RANGE[0] <= discount_value <= VALID_DISCOUNT_RANGE[1]:
        return RuleResult(
            False,
            f"discount {discount_value} outside allowed range {VALID_DISCOUNT_RANGE[0]}-{VALID_DISCOUNT_RANGE[1]}",
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
    if not account_verified and total > COD_UNVERIFIED_ORDER_CAP:
        return RuleResult(
            False,
            f"COD order total {total} exceeds limit {COD_UNVERIFIED_ORDER_CAP} for unverified account",
        )
    return RuleResult(True)


def check_cod_refusal_rate(past_orders: int, past_refusals: int) -> RuleResult:
    if past_orders <= 0:
        return RuleResult(True)
    refusal_rate = past_refusals / past_orders
    if refusal_rate > COD_REFUSAL_RATE_THRESHOLD:
        return RuleResult(
            False,
            f"refusal rate {refusal_rate:.2f} exceeds threshold {COD_REFUSAL_RATE_THRESHOLD}",
        )
    return RuleResult(True)


def validate_transaction(transaction: dict) -> dict:
    """
    Runs every rule against a transaction dict and returns a combined
    result — this is what POST /validate exposes to the enforcement engine.
    """
    failures = []

    coupons = transaction.get("coupons_applied", [])
    if not check_coupon_usage(coupons).passed:
        failures.append(check_coupon_usage(coupons).reason)

    discount_value = float(transaction.get("discount_value", 0))
    if not check_discount_range(discount_value).passed:
        failures.append(check_discount_range(discount_value).reason)

    sku = transaction.get("sku", "")
    quantity = int(transaction.get("quantity", 0))
    if not check_quantity_ceiling(sku, quantity).passed:
        failures.append(check_quantity_ceiling(sku, quantity).reason)

    subtotal = float(transaction.get("subtotal", 0))
    if not check_minimum_purchase(subtotal).passed:
        failures.append(check_minimum_purchase(subtotal).reason)

    total = float(transaction.get("total", 0))
    account_verified = bool(transaction.get("account_verified", True))
    if not check_cod_order_value(total, account_verified).passed:
        failures.append(check_cod_order_value(total, account_verified).reason)

    past_orders = int(transaction.get("past_orders", 0))
    past_refusals = int(transaction.get("past_refusals", 0))
    if not check_cod_refusal_rate(past_orders, past_refusals).passed:
        failures.append(check_cod_refusal_rate(past_orders, past_refusals).reason)

    return {"passed": not failures, "failures": failures}
