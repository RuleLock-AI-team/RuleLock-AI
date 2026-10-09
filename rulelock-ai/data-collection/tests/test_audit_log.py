import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import app


def _row(audit_id=3, action="HOLD", reason="COD refusal rate"):
    return {
        "audit_id": audit_id, "event_id": f"evt-{audit_id}", "event_type": "RULELOCK_REVIEW",
        "created_at": "2026-10-03T10:00:00Z", "order_id": 1002, "action": action,
        "decision": "hold", "reason": reason, "rule_code": "cod_refusal_rate", "anomaly_score": -0.2,
        "order_reference": "CK-1002", "account_id": "acct-2", "payment_method": "COD", "total": 1200,
    }


def test_audit_log_reads_database_page_and_returns_cursor(monkeypatch):
    import routes.events as events

    called = {}
    monkeypatch.setattr(events, "RULELOCK_API_TOKEN", None)
    monkeypatch.setattr(events, "RULELOCK_ALLOW_NO_AUTH", True)
    monkeypatch.setattr(events, "get_audit_log", lambda **kwargs: called.update(kwargs) or [_row(3), _row(2), _row(1)])
    response = app.test_client().get("/audit-log?action=HOLD&search=COD&limit=2")
    data = response.get_json()
    assert response.status_code == 200
    assert called["action"] == "HOLD"
    assert called["search"] == "COD"
    assert data["count"] == 2
    assert data["next_cursor"] == 2
    assert data["records"][0]["action"] == "HOLD"
    assert data["records"][0]["order_reference"] == "CK-1002"


def test_audit_log_empty_state(monkeypatch):
    import routes.events as events

    monkeypatch.setattr(events, "RULELOCK_API_TOKEN", None)
    monkeypatch.setattr(events, "RULELOCK_ALLOW_NO_AUTH", True)
    monkeypatch.setattr(events, "get_audit_log", lambda **kwargs: [])
    response = app.test_client().get("/audit-log")
    assert response.status_code == 200
    assert response.get_json() == {"records": [], "count": 0, "next_cursor": None}


def test_audit_rows_fill_missing_reference_from_cakely_orders(monkeypatch):
    import routes.events as events
    monkeypatch.setattr(events, "RULELOCK_API_TOKEN", None)
    monkeypatch.setattr(events, "RULELOCK_ALLOW_NO_AUTH", True)
    row = _row()
    row["order_reference"] = None
    monkeypatch.setattr(events, "get_audit_log", lambda **kwargs: [row])
    monkeypatch.setattr(events, "get_order_references", lambda ids: {"1002": "CK-1002"})
    monkeypatch.setattr(events, "get_usernames", lambda ids: {})
    response = app.test_client().get("/audit-log")
    assert response.get_json()["records"][0]["order_reference"] == "CK-1002"


def test_audit_log_requires_auth_when_token_is_set(monkeypatch):
    import routes.events as events
    monkeypatch.setattr(events, "RULELOCK_API_TOKEN", "test-token")
    assert app.test_client().get("/audit-log").status_code == 401


def test_audit_log_rejects_invalid_token(monkeypatch):
    import routes.events as events
    monkeypatch.setattr(events, "RULELOCK_API_TOKEN", "test-token")
    response = app.test_client().get("/audit-log", headers={"Authorization": "Bearer wrong-token"})
    assert response.status_code == 401


def test_audit_detail_accepts_cakely_order_reference(monkeypatch):
    import routes.events as events
    monkeypatch.setattr(events, "RULELOCK_API_TOKEN", None)
    monkeypatch.setattr(events, "RULELOCK_ALLOW_NO_AUTH", True)
    monkeypatch.setattr(events, "get_order_id_by_reference", lambda reference: 1002 if reference == "CK-1002" else None)
    monkeypatch.setattr(events, "get_review_event", lambda order_id: {
        "order_id": order_id, "user_id": None,
        "metadata": {"order_reference": "CK-1002", "decision": "hold", "pipeline": {"c1_data_collection": {"account": {}}}},
    })
    response = app.test_client().get("/audit-log/CK-1002")
    assert response.status_code == 200
    assert response.get_json()["order_reference"] == "CK-1002"
    assert response.get_json()["order_id"] == 1002
