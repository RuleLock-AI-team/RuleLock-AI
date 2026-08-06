import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from rules import check_quantity_ceiling, check_minimum_purchase


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

from rules import (
    check_coupon_usage,
    check_discount_range,
    check_cod_order_value,
    check_cod_refusal_rate
)


def test_coupon_usage_passes():
    assert check_coupon_usage(["SAVE10"]).passed


def test_coupon_usage_fails():
    result = check_coupon_usage(["SAVE10", "SAVE20"])
    assert not result.passed
    assert "maximum allowed" in result.reason


def test_discount_range_passes():
    assert check_discount_range(1000).passed


def test_discount_range_fails():
    result = check_discount_range(6000)
    assert not result.passed
    assert "outside allowed range" in result.reason


def test_cod_order_value_passes():
    assert check_cod_order_value(5000, False).passed


def test_cod_order_value_fails():
    result = check_cod_order_value(20000, False)
    assert not result.passed
    assert "unverified account limit" in result.reason


def test_cod_refusal_rate_passes():
    assert check_cod_refusal_rate(10, 2).passed


def test_cod_refusal_rate_fails():
    result = check_cod_refusal_rate(10, 8)
    assert not result.passed
    assert "threshold" in result.reason