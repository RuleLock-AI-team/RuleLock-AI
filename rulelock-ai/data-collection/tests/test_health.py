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
    monkeypatch.setattr(events, "get_rulelock_setting", lambda: {"rulelock_enabled": True})
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
    data = resp.get_json()
    assert data["decision"] == "accept"
    assert data["payment_action"] == "capture_payment"
    assert data["cakely_order_status"] == "approved_for_payment"


def test_review_order_holds_when_rule_engine_is_unavailable(monkeypatch):
    import routes.events as events

    monkeypatch.setattr(events, "RULELOCK_API_TOKEN", None)
    monkeypatch.setattr(events, "get_rulelock_setting", lambda: {"rulelock_enabled": True})
    monkeypatch.setattr(events, "call_rule_engine", lambda payload: {"available": False, "passed": False, "reason": "offline"})
    monkeypatch.setattr(events, "call_anomaly_engine", lambda features: {"available": True, "raw_score": 0.2, "is_anomaly": False})
    monkeypatch.setattr(events, "call_enforcement_engine", lambda **kwargs: (_ for _ in ()).throw(AssertionError("enforcement should be skipped")))
    monkeypatch.setattr(events, "insert_event", lambda *args, **kwargs: [])
    client = app.test_client()
    resp = client.post(
        "/review-order",
        json={"order_id": 1001, "session_id": "session-1", "account_id": "account-1", "session_features": {"coupon_attempts_per_session": 0, "avg_seconds_between_requests": 0, "distinct_accounts_same_device": 1, "distinct_addresses_same_phone": 1}},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["decision"] == "hold"
    assert data["payment_action"] == "hold_payment"
    assert data["cakely_order_status"] == "review"


def test_review_order_bypasses_pipeline_when_toggle_is_disabled(monkeypatch):
    import routes.events as events

    monkeypatch.setattr(events, "RULELOCK_API_TOKEN", "test-token")
    monkeypatch.setattr(events, "call_rule_engine", lambda payload: (_ for _ in ()).throw(AssertionError("rule engine should be skipped")))
    monkeypatch.setattr(events, "call_anomaly_engine", lambda features: (_ for _ in ()).throw(AssertionError("anomaly engine should be skipped")))
    monkeypatch.setattr(events, "call_enforcement_engine", lambda **kwargs: (_ for _ in ()).throw(AssertionError("enforcement should be skipped")))
    monkeypatch.setattr(events, "insert_event", lambda *args, **kwargs: [])
    client = app.test_client()
    resp = client.post(
        "/review-order",
        headers={"Authorization": "Bearer test-token"},
        json={"order_id": 1001, "session_id": "session-1", "rulelock_enabled": False},
    )
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["rulelock_enabled"] is False
    assert data["decision"] == "accept"
    assert data["reason"] == "RuleLock disabled by Cakely owner setting"


def test_session_features_match_anomaly_contract(monkeypatch):
    import routes.events as events

    monkeypatch.setattr(events, "get_session_events", lambda session_id: [
        {
            "event_type": "ADD_TO_CART",
            "created_at": "2026-09-20T10:00:00Z",
            "user_id": 42,
            "metadata": {"session_id": session_id, "device_id": "device-1", "phone": "077"},
        },
        {
            "event_type": "APPLY_COUPON",
            "created_at": "2026-09-20T10:00:10Z",
            "user_id": 43,
            "metadata": {"session_id": session_id, "device_id": "device-1", "phone": "077", "address": "addr-1"},
        },
    ])
    features = events.session_features("session-1")
    assert features["coupon_attempts_per_session"] == 1
    assert features["avg_seconds_between_requests"] == 10
    assert features["distinct_accounts_same_device"] == 2
    assert features["distinct_addresses_same_phone"] == 1


def test_rulelock_toggle_endpoint_updates_shared_setting(monkeypatch):
    import routes.events as events

    monkeypatch.setattr(events, "RULELOCK_API_TOKEN", "test-token")
    monkeypatch.setattr(events, "set_rulelock_setting", lambda enabled: {"rulelock_enabled": enabled})
    client = app.test_client()
    resp = client.post(
        "/settings/rulelock",
        headers={"Authorization": "Bearer test-token"},
        json={"rulelock_enabled": "false"},
    )
    assert resp.status_code == 200
    assert resp.get_json()["rulelock_enabled"] is False
