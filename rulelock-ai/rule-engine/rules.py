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
    # Machine-readable code matching enforcement-engine's RULE_ACTION_MAP keys
    # (decision.py) — this is what lets the enforcement engine pick the right
    # automated action (void_discount vs hold_cod_order) for THIS rule,
    # instead of only having a human-readable reason string.
    code: str = ""


def check_coupon_usage(coupons_applied: list[str]) -> RuleResult:
    if len(coupons_applied) > MAX_COUPONS_PER_SESSION:
        return RuleResult(
            False,
            f"applied {len(coupons_applied)} coupons; limit is {MAX_COUPONS_PER_SESSION}",
            code="coupon_usage",
        )
    return RuleResult(True)


def check_discount_range(discount_value: float) -> RuleResult:
    if not VALID_DISCOUNT_RANGE[0] <= discount_value <= VALID_DISCOUNT_RANGE[1]:
        return RuleResult(
            False,
            f"discount {discount_value} outside allowed range {VALID_DISCOUNT_RANGE[0]}-{VALID_DISCOUNT_RANGE[1]}",
            code="discount_range",
        )
    return RuleResult(True)


def check_quantity_ceiling(sku: str, quantity: int) -> RuleResult:
    if quantity > MAX_QUANTITY_PER_SKU:
        return RuleResult(
            False,
            f"quantity {quantity} exceeds ceiling {MAX_QUANTITY_PER_SKU} for {sku}",
            code="quantity_ceiling",
        )
    return RuleResult(True)


def check_minimum_purchase(subtotal: float) -> RuleResult:
    if subtotal < MIN_PURCHASE_AMOUNT:
        return RuleResult(
            False,
            f"subtotal {subtotal} below minimum {MIN_PURCHASE_AMOUNT}",
            code="minimum_purchase",
        )
    return RuleResult(True)


def check_cod_order_value(total: float, account_verified: bool) -> RuleResult:
    if not account_verified and total > COD_UNVERIFIED_ORDER_CAP:
        return RuleResult(
            False,
            f"COD order total {total} exceeds limit {COD_UNVERIFIED_ORDER_CAP} for unverified account",
            code="cod_order_value",
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
            code="cod_refusal_rate",
        )
    return RuleResult(True)

def validate_transaction(transaction: dict) -> dict:
    """
    Returns:
        passed: bool
        failures: list[str]      — human-readable reasons (unchanged, for logs/UI)
        violations: list[dict]   — [{"code", "reason"}, ...] machine-readable
        rule_code: str | None    — code of the FIRST failing rule, ready to pass
                                    straight to enforcement-engine's /enforce
    """
    coupons = transaction.get("coupons_applied", [])
    discount_value = float(transaction.get("discount_value", 0))
    sku = transaction.get("sku", "")
    quantity = int(transaction.get("quantity", 0))
    subtotal = float(transaction.get("subtotal", 0))
    total = float(transaction.get("total", 0))
    account_verified = bool(transaction.get("account_verified", True))
    past_orders = int(transaction.get("past_orders", 0))
    past_refusals = int(transaction.get("past_refusals", 0))

    results = [
        check_coupon_usage(coupons),
        check_discount_range(discount_value),
        check_quantity_ceiling(sku, quantity),
        check_minimum_purchase(subtotal),
        check_cod_order_value(total, account_verified),
        check_cod_refusal_rate(past_orders, past_refusals),
    ]

    violations = [{"code": r.code, "reason": r.reason} for r in results if not r.passed]
    failures = [v["reason"] for v in violations]

    return {
        "passed": not failures,
        "failures": failures,
        "violations": violations,
        "rule_code": violations[0]["code"] if violations else None,
    }
