import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import app


def test_health():
    client = app.test_client()
    resp = client.get("/health")
    assert resp.status_code == 200


def test_browse_returns_products():
    client = app.test_client()
    resp = client.get("/browse")
    assert resp.status_code == 200
    assert "sku-1" in resp.get_json()


def test_review_order_rejects_invalid_token(monkeypatch):
    import routes.events as events

    monkeypatch.setattr(events, "RULELOCK_API_TOKEN", "test-token")
    client = app.test_client()
    resp = client.post("/review-order", json={"order_id": 1001, "session_id": "session-1"})
    assert resp.status_code == 401


def test_review_order_accepts_clean_order(monkeypatch):
    import routes.events as events

    monkeypatch.setattr(events, "RULELOCK_API_TOKEN", "test-token")
    monkeypatch.setattr(events, "call_rule_engine", lambda payload: {"available": True, "passed": True, "failures": []})
    monkeypatch.setattr(events, "call_anomaly_engine", lambda features: {"available": True, "raw_score": 0.2, "is_anomaly": False})
    monkeypatch.setattr(events, "call_enforcement_engine", lambda **kwargs: {"available": True, "decision": "none"})
    monkeypatch.setattr(events, "insert_event", lambda *args, **kwargs: [])
    client = app.test_client()
    resp = client.post(
        "/review-order",
        headers={"Authorization": "Bearer test-token"},
        json={"order_id": 1001, "session_id": "session-1", "account_id": "account-1", "session_features": {"coupon_attempts_per_session": 0, "avg_seconds_between_requests": 0, "distinct_accounts_same_device": 1, "distinct_addresses_same_phone": 1}},
    )
    assert resp.status_code == 200
    assert resp.get_json()["decision"] == "accept"


def test_review_order_holds_when_rule_engine_is_unavailable(monkeypatch):
    import routes.events as events

    monkeypatch.setattr(events, "RULELOCK_API_TOKEN", None)
    monkeypatch.setattr(events, "call_rule_engine", lambda payload: {"available": False, "passed": False, "reason": "offline"})
    monkeypatch.setattr(events, "call_anomaly_engine", lambda features: {"available": True, "raw_score": 0.2, "is_anomaly": False})
    monkeypatch.setattr(events, "call_enforcement_engine", lambda **kwargs: {"available": True, "decision": "none"})
    monkeypatch.setattr(events, "insert_event", lambda *args, **kwargs: [])
    client = app.test_client()
    resp = client.post(
        "/review-order",
        json={"order_id": 1001, "session_id": "session-1", "account_id": "account-1", "session_features": {"coupon_attempts_per_session": 0, "avg_seconds_between_requests": 0, "distinct_accounts_same_device": 1, "distinct_addresses_same_phone": 1}},
    )
    assert resp.status_code == 200
    assert resp.get_json()["decision"] == "hold"
