import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import db


def test_audit_query_filters_action_search_cursor_and_time_before_limit(monkeypatch):
    captured = {}
    monkeypatch.setattr(db, "_request", lambda table, **kwargs: captured.update(table=table, **kwargs) or [])
    db.get_audit_log(action="HOLD", search="order 42", cursor="91", limit=25)
    params = captured["params"]
    assert captured["table"] == "rulelock_audit_log"
    assert params["event_type"] == "eq.RULELOCK_REVIEW"
    assert params["action"] == "eq.HOLD"
    assert params["audit_id"] == "lt.91"
    assert params["limit"] == "26"
    assert "or" in params
    assert "SUSPEND" not in params["or"]


def test_audit_query_search_matches_reference_and_numeric_id(monkeypatch):
    captured = {}
    monkeypatch.setattr(db, "_request", lambda table, **kwargs: captured.update(table=table, **kwargs) or [])
    db.get_audit_log(search="CK-20261003")
    assert "order_reference.ilike.*CK-20261003*" in captured["params"]["or"]
    db.get_audit_log(search="9001")
    assert "order_id.eq.9001" in captured["params"]["or"]


def test_audit_query_applies_range_before_limit_and_excludes_simulations(monkeypatch):
    from datetime import datetime, timezone

    captured = {}
    monkeypatch.setattr(db, "_request", lambda table, **kwargs: captured.update(table=table, **kwargs) or [])
    start = datetime(2026, 10, 2, tzinfo=timezone.utc)
    end = datetime(2026, 10, 3, tzinfo=timezone.utc)
    db.get_audit_log(start=start, end=end, limit=10)
    assert captured["params"]["event_type"] == "eq.RULELOCK_REVIEW"
    assert "created_at.gte" in captured["params"]["and"]
    assert "created_at.lt" in captured["params"]["and"]
    assert captured["params"]["limit"] == "11"


def test_review_record_uses_atomic_rpc_payload(monkeypatch):
    captured = {}
    monkeypatch.setattr(db, "_request", lambda table, **kwargs: captured.update(table=table, **kwargs) or [])
    db.insert_review_record("RULELOCK_SIMULATION", "session-1", 42, 123, {
        "decision": "hold", "reason": "simulation", "account_id": "acct",
        "rule_result": {"rule_code": "coupon_usage"}, "anomaly_result": {"raw_score": -0.2},
    }, "event-id")
    assert captured["table"] == "rpc/record_rulelock_review"
    event = captured["payload"]["p_event"]
    audit = captured["payload"]["p_audit"]
    assert event["event_type"] == audit["event_type"] == "RULELOCK_SIMULATION"
    assert event["metadata"]["session_id"] == "session-1"
    assert audit["event_id"] == "event-id"
    assert audit["action"] == "HOLD"
    assert audit["rule_code"] == "coupon_usage"
