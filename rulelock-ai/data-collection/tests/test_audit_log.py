import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import app


def _rows():
    return [
        {
            "event_id": "evt-1",
            "created_at": "2026-09-20T10:00:00Z",
            "order_id": 1001,
            "metadata": {
                "decision": "reject",
                "reason": "coupon stacked",
                "rule_result": {"rule_code": "coupon_usage"},
                "anomaly_result": {"raw_score": 0.1},
                "enforcement_result": {"decision": "void_discount"},
            },
        },
        {
            "event_id": "evt-2",
            "created_at": "2026-09-20T10:01:00Z",
            "order_id": 1002,
            "metadata": {
                "decision": "hold",
                "reason": "COD refusal rate",
                "rule_result": {"rule_code": "cod_refusal_rate"},
                "anomaly_result": {"raw_score": -0.2},
                "enforcement_result": {"decision": "hold_cod_order"},
            },
        },
        {
            "event_id": "evt-3",
            "created_at": "2026-09-20T10:02:00Z",
            "order_id": 1003,
            "metadata": {
                "decision": "hold",
                "reason": "rapid requests",
                "rule_result": {},
                "anomaly_result": {"raw_score": -0.3},
                "enforcement_result": {"decision": "rate_limit_account"},
            },
        },
    ]


def test_audit_log_empty_state(monkeypatch):
    import routes.events as events

    monkeypatch.setattr(events, "RULELOCK_API_TOKEN", None)
    monkeypatch.setattr(events, "get_recent_review_events", lambda **kwargs: [])
    client = app.test_client()

    resp = client.get("/audit-log")

    assert resp.status_code == 200
    assert resp.get_json() == {"records": [], "count": 0}


def test_audit_log_filters_by_action(monkeypatch):
    import routes.events as events

    monkeypatch.setattr(events, "RULELOCK_API_TOKEN", None)
    monkeypatch.setattr(events, "get_recent_review_events", lambda **kwargs: _rows())
    client = app.test_client()

    resp = client.get("/audit-log?action=HOLD")

    data = resp.get_json()
    assert resp.status_code == 200
    assert data["count"] == 1
    assert data["records"][0]["action"] == "HOLD"
    assert data["records"][0]["rule_violated"] == "cod_refusal_rate"


def test_audit_log_searches_entries(monkeypatch):
    import routes.events as events

    monkeypatch.setattr(events, "RULELOCK_API_TOKEN", None)
    monkeypatch.setattr(events, "get_recent_review_events", lambda **kwargs: _rows())
    client = app.test_client()

    resp = client.get("/audit-log?search=rapid")

    data = resp.get_json()
    assert resp.status_code == 200
    assert data["count"] == 1
    assert data["records"][0]["action"] == "SUSPEND"


def test_audit_log_requires_auth_when_token_is_set(monkeypatch):
    import routes.events as events

    monkeypatch.setattr(events, "RULELOCK_API_TOKEN", "test-token")
    client = app.test_client()

    resp = client.get("/audit-log")

    assert resp.status_code == 401


def test_audit_log_rejects_invalid_token(monkeypatch):
    import routes.events as events

    monkeypatch.setattr(events, "RULELOCK_API_TOKEN", "test-token")
    client = app.test_client()

    resp = client.get("/audit-log", headers={"Authorization": "Bearer wrong-token"})

    assert resp.status_code == 401
