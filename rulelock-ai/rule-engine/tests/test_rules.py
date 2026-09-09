import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from rules import (
    check_coupon_usage,
    check_discount_range,
    check_quantity_ceiling,
    check_minimum_purchase,
    check_cod_order_value,
    check_cod_refusal_rate,
    validate_transaction,
)


def test_quantity_ceiling_passes_under_limit():
    assert check_quantity_ceiling("sku-1", 5).passed


def test_quantity_ceiling_fails_over_limit():
    result = check_quantity_ceiling("sku-1", 50)
    assert not result.passed
    assert "sku-1" in result.reason


def test_minimum_purchase_fails_below_threshold():
    assert not check_minimum_purchase(100).passed


def test_minimum_purchase_passes_above_threshold():
    assert check_minimum_purchase(1000).passed


def test_coupon_usage_fails_when_multiple_coupons_are_applied():
    result = check_coupon_usage(["WELCOME10", "SAVE500"])
    assert not result.passed
    assert "coupon" in result.reason.lower()


def test_discount_range_fails_for_excessive_discount():
    result = check_discount_range(6000)
    assert not result.passed
    assert "discount" in result.reason.lower()


def test_cod_order_value_fails_for_unverified_large_cod_order():
    result = check_cod_order_value(20000, False)
    assert not result.passed
    assert "unverified" in result.reason.lower()


def test_cod_refusal_rate_fails_when_threshold_is_exceeded():
    result = check_cod_refusal_rate(10, 6)
    assert not result.passed
    assert "refusal" in result.reason.lower()


def test_validate_transaction_aggregates_all_failures():
    transaction = {
        "coupons_applied": ["WELCOME10", "SAVE500"],
        "discount_value": 6000,
        "sku": "sku-1",
        "quantity": 50,
        "subtotal": 100,
        "total": 20000,
        "account_verified": False,
        "past_orders": 10,
        "past_refusals": 6,
    }
    result = validate_transaction(transaction)
    assert not result["passed"]
    assert len(result["failures"]) >= 5
