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
