import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import app


def _audit_row(event_id, decision, rule_code=None, score=0.1):
    return {
        "event_id": event_id, "event_type": "RULELOCK_REVIEW", "audit_id": 1,
        "created_at": datetime.now(timezone.utc).isoformat(), "order_id": 1001,
        "decision": decision, "action": {"reject": "REJECT", "hold": "HOLD", "accept": "PASS", "void_discount": "VOID"}[decision],
        "reason": "test review", "rule_code": rule_code, "anomaly_score": score,
        "account_id": "acct", "total": 1000,
    }


def _authorize(monkeypatch, events):
    monkeypatch.setattr(events, "RULELOCK_API_TOKEN", None)
    monkeypatch.setattr(events, "RULELOCK_ALLOW_NO_AUTH", True)


def test_dashboard_summary_uses_audit_counts_and_excludes_simulations(monkeypatch):
    import routes.events as events

    _authorize(monkeypatch, events)
    rows = [_audit_row("evt-1", "reject", "coupon_usage"), _audit_row("evt-2", "hold", "cod_abuse", -0.2), _audit_row("evt-3", "accept")]
    monkeypatch.setattr(events, "get_audit_log", lambda **kwargs: rows)
    monkeypatch.setattr(events, "get_usernames", lambda ids: {})
    blocked = iter([2, 3])
    monkeypatch.setattr(events, "count_audit_events", lambda start, end, blocked_only=False: next(blocked) if blocked_only else 3)
    monkeypatch.setattr(events, "count_transaction_events", lambda *args: 4)
    data = app.test_client().get("/dashboard/summary").get_json()
    assert data["threats_blocked"] == 2
    assert data["threats_blocked_delta"] == -1
    assert data["rule_violations"] == {"total": 2, "coupon": 1, "cod": 1}
    assert data["anomaly_detections"] == 1
    assert data["components"]["enforcement_engine"]["manual_overrides"] == 4


def test_dashboard_summary_counts_current_rule_codes_and_anomaly_rejects(monkeypatch):
    import routes.events as events
    _authorize(monkeypatch, events)
    rows = [
        _audit_row("1", "hold", "cod_abuse"),
        _audit_row("2", "hold", "cod_order_value"),
        _audit_row("3", "reject", None),
        _audit_row("4", "void_discount", "coupon_velocity"),
        _audit_row("5", "reject", "price_mismatch"),
    ]
    monkeypatch.setattr(events, "get_audit_log", lambda **kwargs: rows)
    monkeypatch.setattr(events, "get_usernames", lambda ids: {})
    monkeypatch.setattr(events, "count_audit_events", lambda *args, **kwargs: 5)
    monkeypatch.setattr(events, "count_transaction_events", lambda *args: 0)
    data = app.test_client().get("/dashboard/summary").get_json()
    assert data["cod_orders_held"] == 2
    assert data["accounts_suspended"] == 1
    assert data["abuse_breakdown"] == {
        "coupon_discount_abuse": 1, "price_quantity_manipulation": 1, "cod_fake_order_abuse": 2,
    }


def test_dashboard_summary_empty_state(monkeypatch):
    import routes.events as events

    _authorize(monkeypatch, events)
    monkeypatch.setattr(events, "get_audit_log", lambda **kwargs: [])
    monkeypatch.setattr(events, "count_audit_events", lambda *args, **kwargs: 0)
    monkeypatch.setattr(events, "count_transaction_events", lambda *args: 0)
    data = app.test_client().get("/dashboard/summary").get_json()
    assert data["threats_blocked"] == 0
    assert data["threats_blocked_delta"] == 0
    assert data["enforcement_feed"] == []


def test_dashboard_summary_requires_auth_when_token_is_set(monkeypatch):
    import routes.events as events
    monkeypatch.setattr(events, "RULELOCK_API_TOKEN", "test-token")
    assert app.test_client().get("/dashboard/summary").status_code == 401


def test_dashboard_summary_rejects_invalid_token(monkeypatch):
    import routes.events as events
    monkeypatch.setattr(events, "RULELOCK_API_TOKEN", "test-token")
    response = app.test_client().get("/dashboard/summary", headers={"Authorization": "Bearer wrong-token"})
    assert response.status_code == 401
