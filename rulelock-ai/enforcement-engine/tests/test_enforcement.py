import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from decision import decide


def test_checkout_rule_failure_voids_discount():
    result = decide("order-1", "acct-1", rule_passed=False, rule_reason="quantity exceeded",
                     anomaly_score=0.5, payment_method="PREPAID", rule_code="quantity_ceiling")
    assert result["decision"] == "void_discount"


def test_cod_rule_failure_holds_order_instead_of_voiding():
    result = decide("order-2", "acct-2", rule_passed=False, rule_reason="refusal rate too high",
                     anomaly_score=0.5, payment_method="COD", rule_code="cod_refusal_rate")
    assert result["decision"] == "hold_cod_order"


def test_unknown_or_missing_rule_code_falls_back_to_void_discount():
    result = decide("order-3", "acct-3", rule_passed=False, rule_reason="some failure",
                     anomaly_score=0.5, payment_method="PREPAID")
    assert result["decision"] == "void_discount"


def test_high_anomaly_cod_order_gets_held():
    result = decide("order-4", "acct-4", rule_passed=True, rule_reason="",
                     anomaly_score=-0.5, payment_method="COD")
    assert result["decision"] == "hold_cod_order"


def test_high_anomaly_prepaid_order_gets_rate_limited():
    result = decide("order-5", "acct-5", rule_passed=True, rule_reason="",
                     anomaly_score=-0.5, payment_method="PREPAID")
    assert result["decision"] == "rate_limit_account"


def test_passes_when_clean():
    result = decide("order-6", "acct-6", rule_passed=True, rule_reason="",
                     anomaly_score=0.5, payment_method="PREPAID")
    assert result["decision"] == "none"