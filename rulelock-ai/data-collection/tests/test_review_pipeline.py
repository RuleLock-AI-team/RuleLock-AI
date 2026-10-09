import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import db
import routes.events as events
from app import app


def test_cod_history_excludes_admin_cancel_and_current_order(monkeypatch):
    captured = {}
    monkeypatch.setattr(db, "_request", lambda table, **kwargs: captured.update(table=table, **kwargs) or [
        {"id": 1, "status": "CANCELLED", "cancelled_by": "ADMIN"},
        {"id": 2, "status": "REFUSED", "cancelled_by": None},
        {"id": 3, "status": "CANCELLED", "cancelled_by": "CUSTOMER"},
    ])
    assert db.get_cod_history(9, 10) == {"total": 3, "bad": 2}
    assert captured["params"]["id"] == "neq.10"
    assert captured["params"]["payment_method"] == "eq.COD"


def test_database_cod_counts_drive_hold_and_reject_rules(monkeypatch):
    import rules
    monkeypatch.setattr(rules, "get_products", lambda: {})

    def load_history(bad_count):
        rows = [{"id": 100, "status": "CANCELLED", "cancelled_by": "ADMIN"},
                {"id": 101, "status": "COMPLETED", "cancelled_by": None},
                {"id": 102, "status": "REFUSED", "cancelled_by": None},
                {"id": 103, "status": "CANCELLED", "cancelled_by": "CUSTOMER"}]
        if bad_count == 3:
            rows.append({"id": 104, "status": "REFUSED", "cancelled_by": None})
        monkeypatch.setattr(db, "_request", lambda *args, **kwargs: rows)
        history = db.get_cod_history(9, exclude_order_id=999)
        payload = {"payment_method": "COD", "subtotal": 1000, "total": 1000, "items": [],
                   "past_orders": history["total"], "past_refusals": history["bad"]}
        return history, rules.validate_transaction(payload)

    hold_history, hold = load_history(2)
    reject_history, reject = load_history(3)
    assert hold_history == {"total": 4, "bad": 2}
    assert hold["rule_code"] == "cod_abuse"
    assert reject_history == {"total": 5, "bad": 3}
    assert reject["rule_code"] == "cod_abuse_severe"


def test_simulation_account_override_and_pipeline_snapshot(monkeypatch):
    monkeypatch.setattr(events, "RULELOCK_API_TOKEN", None)
    monkeypatch.setattr(events, "RULELOCK_ALLOW_NO_AUTH", True)
    monkeypatch.setattr(events, "get_review_event", lambda *args, **kwargs: None)
    monkeypatch.setattr(events, "session_features", lambda *args: {
        "event_count": 6, "coupon_attempts_per_session": 2,
        "avg_seconds_between_requests": 8, "distinct_accounts_same_device": 1,
        "distinct_addresses_same_phone": 1,
    })
    monkeypatch.setattr(events, "insert_review_record", lambda *args: None)

    def pipeline(order_id, account_id, payment_method, order_payload, features):
        assert order_payload["past_orders"] == 4
        assert order_payload["past_refusals"] == 2
        assert order_payload["account_verified"] is True
        rule_result = {"passed": False, "rule_code": "cod_abuse", "failures": ["2 of 4"],
                       "violations": [{"code": "cod_abuse", "reason": "2 of 4"}], "checks": []}
        anomaly = {"raw_score": -0.08, "is_anomaly": True}
        enforcement = {"decision": "hold", "action": "hold_cod_order", "reason": "COD abuse"}
        return rule_result, anomaly, enforcement

    monkeypatch.setattr(events, "_run_review_pipeline", pipeline)
    response = app.test_client().post("/review-order", json={
        "order_id": 777, "user_id": 22, "simulation": True, "payment_method": "COD",
        "past_orders": 0, "past_refusals": 0,
        "simulated_account": {"cod_orders": 4, "cod_bad": 2, "completed_orders": 1, "account_age_days": 90},
    }).get_json()
    assert response["decision"] == "hold"
    pipeline_result = response["pipeline"]
    assert set(pipeline_result) == {"c1_data_collection", "c2_rule_engine", "c3_anomaly", "c4_enforcement"}
    assert pipeline_result["c1_data_collection"]["account"]["cod_bad_orders"] == 2
    assert pipeline_result["c2_rule_engine"]["status"] == "fail"
    assert pipeline_result["c3_anomaly"]["status"] == "suspicious"
    assert pipeline_result["c4_enforcement"]["decision"] == "hold"


def test_live_cod_lookup_failure_returns_specific_hold(monkeypatch):
    monkeypatch.setattr(events, "RULELOCK_API_TOKEN", None)
    monkeypatch.setattr(events, "RULELOCK_ALLOW_NO_AUTH", True)
    monkeypatch.setattr(events, "get_review_event", lambda *args, **kwargs: None)
    monkeypatch.setattr(events, "get_account_profile", lambda user_id: (_ for _ in ()).throw(RuntimeError("offline")))
    monkeypatch.setattr(events, "insert_review_record", lambda *args: None)
    response = app.test_client().post("/review-order", json={"order_id": 778, "user_id": 22, "payment_method": "COD"})
    assert response.get_json()["decision"] == "hold"
    assert response.get_json()["reason"] == "account history unavailable"


def test_order_reference_lookup_for_live_review_and_simulation_label(monkeypatch):
    monkeypatch.setattr(events, "RULELOCK_API_TOKEN", None)
    monkeypatch.setattr(events, "RULELOCK_ALLOW_NO_AUTH", True)
    monkeypatch.setattr(events, "get_review_event", lambda *args, **kwargs: None)
    monkeypatch.setattr(events, "get_account_profile", lambda user_id: {
        "user_id": user_id, "username": "demo", "account_age_days": 20, "completed_orders": 1,
    })
    monkeypatch.setattr(events, "get_order_reference", lambda order_id: "CK-20261003123456")
    monkeypatch.setattr(events, "session_features", lambda *args: {})
    stored = []
    monkeypatch.setattr(events, "insert_review_record", lambda *args: stored.append(args[4]) or None)
    monkeypatch.setattr(events, "_run_review_pipeline", lambda **kwargs: (
        {"passed": True, "checks": [], "violations": [], "failures": []},
        {"raw_score": 0.2, "is_anomaly": False}, {"decision": "accept", "action": "none"},
    ))
    client = app.test_client()

    live = client.post("/review-order", json={"order_id": 9001, "user_id": 31, "payment_method": "CARD"}).get_json()
    assert live["order_reference"] == "CK-20261003123456"
    assert stored[-1]["order_reference"] == "CK-20261003123456"

    monkeypatch.setattr(events, "get_order_reference", lambda order_id: (_ for _ in ()).throw(AssertionError("simulation must not query orders")))
    simulation = client.post("/review-order", json={"order_id": 9002, "simulation": True}).get_json()
    assert simulation["order_reference"] == "SIM-9002"
    assert stored[-1]["order_reference"] == "SIM-9002"
