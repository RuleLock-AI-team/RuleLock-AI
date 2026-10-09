"""Configurable checkout rules for the RuleLock review pipeline."""
from dataclasses import dataclass
import math
import os
import logging

from db import get_coupon_review_count, get_products

logger = logging.getLogger(__name__)


def _int_env(name, default):
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        logger.warning("Invalid integer rule setting %s; using default", name)
        return int(default)


def _float_env(name, default):
    try:
        return float(os.environ.get(name, default))
    except (TypeError, ValueError):
        logger.warning("Invalid numeric rule setting %s; using default", name)
        return float(default)


MAX_COUPONS = _int_env("MAX_COUPONS", 1)
MAX_COUPONS_PER_SESSION = MAX_COUPONS
MAX_DISCOUNT_RATIO = _float_env("MAX_DISCOUNT_RATIO", 0.6)
MAX_QUANTITY_PER_LINE = _int_env("MAX_QUANTITY_PER_LINE", 20)
MIN_PURCHASE_AMOUNT = _float_env("MIN_PURCHASE_AMOUNT", 500)
COD_UNVERIFIED_ORDER_CAP = _float_env("COD_UNVERIFIED_ORDER_CAP", 15000)
COD_BAD_HOLD = _int_env("COD_BAD_HOLD", 2)
COD_BAD_REJECT = _int_env("COD_BAD_REJECT", 3)
COUPON_VELOCITY_MAX_REVIEWS = _int_env("COUPON_VELOCITY_MAX_REVIEWS", 5)
PRICE_MATCH_TOLERANCE = _float_env("PRICE_MATCH_TOLERANCE", 0.01)


@dataclass
class RuleResult:
    passed: bool
    reason: str = ""
    code: str = ""


def check_coupon_usage(coupons_applied):
    if len(coupons_applied or []) > MAX_COUPONS_PER_SESSION:
        return RuleResult(False, f"Coupons {' + '.join(map(str, coupons_applied))} stacked (max {MAX_COUPONS_PER_SESSION})", "coupon_usage")
    return RuleResult(True, f"{len(coupons_applied or [])} coupons applied (max {MAX_COUPONS_PER_SESSION})", "coupon_usage")


def check_discount_range(discount_value, subtotal):
    if (not math.isfinite(discount_value) or not math.isfinite(subtotal) or subtotal < 0
            or discount_value < 0 or discount_value > subtotal
            or discount_value > subtotal * MAX_DISCOUNT_RATIO):
        return RuleResult(False, f"Discount {discount_value:g} exceeds {MAX_DISCOUNT_RATIO:.0%} of subtotal {subtotal:g}", "discount_range")
    return RuleResult(True, f"Discount {discount_value:g} is within {MAX_DISCOUNT_RATIO:.0%} of subtotal {subtotal:g}", "discount_range")


def check_quantity_ceiling(sku, quantity):
    if quantity <= 0 or quantity > MAX_QUANTITY_PER_LINE:
        return RuleResult(False, f"Quantity {quantity} exceeds the limit of {MAX_QUANTITY_PER_LINE} for {sku}", "quantity_ceiling")
    return RuleResult(True, f"Quantity {quantity} is within the limit of {MAX_QUANTITY_PER_LINE} for {sku}", "quantity_ceiling")


def check_minimum_purchase(subtotal):
    if subtotal < MIN_PURCHASE_AMOUNT:
        return RuleResult(False, f"Subtotal {subtotal:g} is below the minimum purchase of {MIN_PURCHASE_AMOUNT:g}", "minimum_purchase")
    return RuleResult(True, f"Subtotal {subtotal:g} meets the minimum purchase of {MIN_PURCHASE_AMOUNT:g}", "minimum_purchase")


def check_cod_order_value(total, account_verified):
    if not account_verified and total > COD_UNVERIFIED_ORDER_CAP:
        return RuleResult(False, f"Unverified COD total {total:g} exceeds the cap of {COD_UNVERIFIED_ORDER_CAP:g}", "cod_order_value")
    return RuleResult(True, f"COD total {total:g}; verified={bool(account_verified)}; cap {COD_UNVERIFIED_ORDER_CAP:g}", "cod_order_value")


def check_cod_abuse(total, bad):
    rate = bad / total if total else 0
    detail = f"COD abuse: {bad} of {total} previous COD orders were cancelled by the customer or refused"
    if bad >= COD_BAD_REJECT and rate >= 0.5:
        return RuleResult(False, detail, "cod_abuse_severe")
    if bad >= COD_BAD_HOLD and rate >= 0.5:
        return RuleResult(False, detail, "cod_abuse")
    return RuleResult(True, detail, "cod_abuse")


def _catalog_price(product, size):
    sizes = product.get("sizes")
    if isinstance(sizes, dict) and size in sizes:
        value = sizes[size]
        return float(value.get("price")) if isinstance(value, dict) and value.get("price") is not None else float(value)
    if isinstance(sizes, list):
        for entry in sizes:
            if isinstance(entry, dict) and str(entry.get("size")) == str(size):
                value = entry.get("price", entry.get("unit_price"))
                if value is not None:
                    return float(value)
    base = float(product["price"])
    try:
        kg = float(str(size).lower().replace("kg", "").strip())
    except (TypeError, ValueError):
        kg = 1.0
    return base * kg


def check_price_mismatch(items):
    products = get_products() or {}
    checked = []
    for item in items:
        sku = str(item.get("sku", ""))
        # Older integrations supplied only sku/quantity. The current contract
        # always supplies unit_price; retain compatibility for old payloads.
        if "unit_price" not in item:
            continue
        product = products.get(sku)
        if product is None:
            return RuleResult(False, f"Price for {sku} could not be matched: item missing from catalog", "price_mismatch")
        try:
            supplied = float(item["unit_price"])
            expected = _catalog_price(product, item.get("size"))
        except (KeyError, TypeError, ValueError):
            return RuleResult(False, f"Price for {sku} could not be verified", "price_mismatch")
        if (not math.isfinite(supplied) or not math.isfinite(expected) or expected <= 0
                or abs(supplied - expected) / expected > PRICE_MATCH_TOLERANCE):
            return RuleResult(False, f"Price mismatch for {sku}: supplied {supplied:g}, catalog {expected:g}", "price_mismatch")
        checked.append(f"{sku}: supplied {supplied:g}, catalog {expected:g}")
    return RuleResult(True, "; ".join(checked) if checked else "No client prices supplied; catalog comparison not applicable", "price_mismatch")


def validate_transaction(transaction):
    items = transaction.get("items")
    if not isinstance(items, list):
        items = [{"sku": transaction.get("sku", ""), "quantity": transaction.get("quantity", 0)}]
    normalized = []
    for item in items:
        if not isinstance(item, dict):
            normalized.append({})
            continue
        normalized.append({**item, "quantity": item.get("quantity", item.get("qty", 0))})

    coupons = transaction.get("coupons_applied", []) or []
    discount = float(transaction.get("discount_value", 0) or 0)
    subtotal = float(transaction.get("subtotal", 0) or 0)
    total = float(transaction.get("total", subtotal - discount) or 0)
    method = str(transaction.get("payment_method", "CARD")).upper()
    verified = bool(transaction.get("account_verified", True))
    past_orders = int(transaction.get("past_orders", 0) or 0)
    past_refusals = int(transaction.get("past_refusals", 0) or 0)
    account_id = transaction.get("account_id") or transaction.get("user_id")
    results = [check_coupon_usage(coupons), check_discount_range(discount, subtotal)]
    results.extend(check_quantity_ceiling(item.get("sku", ""), int(item.get("quantity", 0) or 0)) for item in normalized)
    results.extend([check_minimum_purchase(subtotal), check_price_mismatch(normalized)])
    if account_id and coupons:
        try:
            coupon_reviews = get_coupon_review_count(account_id, hours=24)
            if coupon_reviews > COUPON_VELOCITY_MAX_REVIEWS:
                results.append(RuleResult(False, f"Coupon velocity {coupon_reviews} reviews exceeds the limit of {COUPON_VELOCITY_MAX_REVIEWS}", "coupon_velocity"))
            else:
                results.append(RuleResult(True, f"Coupon velocity {coupon_reviews} reviews (max {COUPON_VELOCITY_MAX_REVIEWS})", "coupon_velocity"))
        except Exception:
            logger.exception("Could not load coupon velocity history")
            raise
    else:
        results.append(RuleResult(True, "Coupon velocity not applicable without an account and coupon", "coupon_velocity"))
    if method == "COD":
        results.extend([check_cod_order_value(total, verified), check_cod_abuse(past_orders, past_refusals)])

    actions = {"reject": 3, "hold": 2, "void_discount": 1}
    action_by_code = {"quantity_ceiling": "reject", "price_mismatch": "reject",
                      "cod_abuse_severe": "reject", "cod_order_value": "hold", "cod_abuse": "hold",
                      "coupon_usage": "void_discount", "discount_range": "void_discount",
                      "coupon_velocity": "void_discount", "minimum_purchase": "void_discount"}
    failed = sorted((r for r in results if not r.passed), key=lambda r: actions[action_by_code.get(r.code, "hold")], reverse=True)
    violations = [{"code": result.code, "reason": result.reason} for result in failed]
    checks = [{"code": result.code, "label": result.code.replace("_", " ").title(),
               "passed": result.passed, "detail": result.reason} for result in results]
    return {"passed": not violations, "failures": [v["reason"] for v in violations],
            "violations": violations, "checks": checks,
            "rule_code": violations[0]["code"] if violations else None}
