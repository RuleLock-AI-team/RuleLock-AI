import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import app


def test_dashboard_summary_empty_state(monkeypatch):
    import routes.events as events

    monkeypatch.setattr(events, "RULELOCK_API_TOKEN", None)
    monkeypatch.setattr(events, "get_recent_review_events", lambda **kwargs: [])
    client = app.test_client()

    resp = client.get("/dashboard/summary")

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["threats_blocked"] == 0
    assert data["rule_violations"]["total"] == 0
    assert data["enforcement_feed"] == []


def test_dashboard_summary_counts_mixed_reviews(monkeypatch):
    import routes.events as events

    rows = [
        {
            "event_id": "evt-1",
            "created_at": "2026-09-20T10:00:00Z",
            "order_id": 1001,
            "metadata": {
                "session_id": "s1",
                "decision": "reject",
                "reason": "coupon stacked",
                "rule_result": {"rule_code": "coupon_usage"},
                "anomaly_result": {"is_anomaly": False, "raw_score": 0.1},
                "enforcement_result": {"decision": "void_discount"},
            },
        },
        {
            "event_id": "evt-2",
            "created_at": "2026-09-20T10:01:00Z",
            "order_id": 1002,
            "metadata": {
                "session_id": "s2",
                "decision": "hold",
                "reason": "COD risk",
                "rule_result": {"rule_code": "cod_refusal_rate"},
                "anomaly_result": {"is_anomaly": True, "raw_score": -0.2},
                "enforcement_result": {"decision": "hold_cod_order"},
            },
        },
        {
            "event_id": "evt-3",
            "created_at": "2026-09-20T10:02:00Z",
            "order_id": 1003,
            "metadata": {
                "session_id": "s3",
                "decision": "accept",
                "reason": "clean",
                "rule_result": {},
                "anomaly_result": {"is_anomaly": False, "raw_score": 0.2},
                "enforcement_result": {"decision": "none"},
            },
        },
    ]
    monkeypatch.setattr(events, "RULELOCK_API_TOKEN", None)
    monkeypatch.setattr(events, "get_recent_review_events", lambda **kwargs: rows)
    client = app.test_client()

    resp = client.get("/dashboard/summary")

    data = resp.get_json()
    assert resp.status_code == 200
    assert data["threats_blocked"] == 2
    assert data["rule_violations"] == {"total": 2, "coupon": 1, "cod": 1}
    assert data["anomaly_detections"] == 1
    assert data["discounts_voided"] == 1
    assert data["cod_orders_held"] == 1
    assert data["enforcement_feed"][0]["action"] == "VOID"


def test_dashboard_summary_requires_auth_when_token_is_set(monkeypatch):
    import routes.events as events

    monkeypatch.setattr(events, "RULELOCK_API_TOKEN", "test-token")
    client = app.test_client()

    resp = client.get("/dashboard/summary")

    assert resp.status_code == 401


def test_dashboard_summary_rejects_invalid_token(monkeypatch):
    import routes.events as events

    monkeypatch.setattr(events, "RULELOCK_API_TOKEN", "test-token")
    client = app.test_client()

    resp = client.get("/dashboard/summary", headers={"Authorization": "Bearer wrong-token"})

    assert resp.status_code == 401
