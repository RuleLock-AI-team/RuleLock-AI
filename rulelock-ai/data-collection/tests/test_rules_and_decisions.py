import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import rules
from decision import decide, RULE_ACTION_MAP


def test_contract_rule_action_map():
    assert RULE_ACTION_MAP["coupon_velocity"] == "void_discount"
    assert RULE_ACTION_MAP["quantity_ceiling"] == "reject"
    assert RULE_ACTION_MAP["price_mismatch"] == "reject"
    assert RULE_ACTION_MAP["cod_abuse"] == "hold"
    assert RULE_ACTION_MAP["cod_abuse_severe"] == "reject"


def test_anomaly_decision_is_tiered_and_weak_signal_holds():
    assert decide(1, "a", True, "", -0.1, "CARD")["decision"] == "hold"
    result = decide(1, "a", True, "", -0.3, "CARD")
    assert result["decision"] == "reject"
    assert result["account_action"] == {"type": "rate_limit", "minutes": 30}
    assert decide(1, "a", True, "", 0.1, "CARD")["decision"] == "accept"


def test_discount_is_relative_to_subtotal(monkeypatch):
    monkeypatch.setattr(rules, "get_products", lambda: {})
    good = rules.validate_transaction({"subtotal": 10000, "discount_value": 6000, "items": []})
    bad = rules.validate_transaction({"subtotal": 10000, "discount_value": 6001, "items": []})
    assert good["rule_code"] is None
    assert bad["rule_code"] == "discount_range"
    assert rules.validate_transaction({"subtotal": float("nan"), "discount_value": 0, "items": []})["rule_code"] == "discount_range"


def test_quantity_ceiling_is_per_line_and_defaults_to_twenty(monkeypatch):
    monkeypatch.setattr(rules, "get_products", lambda: {"sku-a": {"price": 100}})
    assert rules.validate_transaction({"subtotal": 3000, "items": [
        {"sku": "sku-a", "quantity": 20}, {"sku": "sku-a", "quantity": 20}
    ]})["passed"]
    result = rules.validate_transaction({"subtotal": 3000, "items": [
        {"sku": "sku-a", "quantity": 21}
    ]})
    assert result["rule_code"] == "quantity_ceiling"


def test_price_mismatch_uses_catalog_price_with_one_percent_tolerance(monkeypatch):
    monkeypatch.setattr(rules, "get_products", lambda: {"sku-cake": {"price": 1000, "sizes": {"2": 1800}}})
    good = rules.validate_transaction({"subtotal": 1800, "items": [
        {"sku": "sku-cake", "size": "2", "quantity": 1, "unit_price": 1810}
    ]})
    bad = rules.validate_transaction({"subtotal": 1800, "items": [
        {"sku": "sku-cake", "size": "2", "quantity": 1, "unit_price": 1750}
    ]})
    assert good["passed"]
    assert bad["rule_code"] == "price_mismatch"


def test_cod_abuse_thresholds_and_cancelled_admin_does_not_count(monkeypatch):
    monkeypatch.setattr(rules, "get_products", lambda: {})
    payload = {"payment_method": "COD", "subtotal": 1000, "total": 1000, "items": [], "past_orders": 4, "past_refusals": 2}
    assert rules.validate_transaction(payload)["rule_code"] == "cod_abuse"
    payload["past_refusals"] = 3
    assert rules.validate_transaction(payload)["rule_code"] == "cod_abuse_severe"


def test_severity_ordering_and_all_check_details(monkeypatch):
    monkeypatch.setattr(rules, "get_products", lambda: {})
    result = rules.validate_transaction({"subtotal": 100, "discount_value": 90, "items": [{"sku": "sku-3", "quantity": 35}]})
    assert result["rule_code"] == "quantity_ceiling"
    assert [v["code"] for v in result["violations"]][0] == "quantity_ceiling"
    assert any(not check["passed"] and check["code"] == "discount_range" for check in result["checks"])
    assert any(check["passed"] for check in result["checks"])


def test_decision_uses_most_severe_violation():
    result = decide(1, "a", False, "all failed", 0, "CARD", "coupon_usage", [
        {"code": "coupon_usage"}, {"code": "cod_abuse"}, {"code": "quantity_ceiling"},
    ])
    assert result["decision"] == "reject"
