import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import app
import app as backend
import pytest
import routes.events as event_routes


@pytest.fixture(autouse=True)
def audit_insert_stub(monkeypatch):
    monkeypatch.setattr(event_routes, "insert_audit_log", lambda *args, **kwargs: [])


def test_health():
    client = app.test_client()
    resp = client.get("/health")
    assert resp.status_code == 200


def test_ready_requires_loaded_model_and_supabase(monkeypatch):
    monkeypatch.setattr(backend, "is_model_loaded", lambda: True)
    monkeypatch.setattr(backend, "check_supabase", lambda: [])
    response = app.test_client().get("/ready")
    assert response.status_code == 200
    assert response.get_json()["ready"] is True

    monkeypatch.setattr(backend, "check_supabase", lambda: (_ for _ in ()).throw(RuntimeError("offline")))
    response = app.test_client().get("/ready")
    assert response.status_code == 503
    assert response.get_json()["checks"]["supabase_reachable"] is False


def test_legacy_storefront_endpoints_are_removed():
    client = app.test_client()
    assert client.get("/browse").status_code == 404
    assert client.post("/cart").status_code == 404
    assert client.post("/apply-coupon").status_code == 404
    assert client.post("/checkout").status_code == 404


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
    monkeypatch.setattr(events, "get_review_event", lambda order_id, event_type="RULELOCK_REVIEW": None)
    monkeypatch.setattr(events, "session_features", lambda *args: {})
    monkeypatch.setattr(events, "call_rule_engine", lambda payload: {"available": True, "passed": True, "failures": []})
    monkeypatch.setattr(events, "call_anomaly_engine", lambda features: {"available": True, "raw_score": 0.2, "is_anomaly": False})
    monkeypatch.setattr(events, "call_enforcement_engine", lambda **kwargs: {"available": True, "decision": "accept"})
    recorded_event_types = []
    monkeypatch.setattr(events, "insert_review_record", lambda event_type, *args, **kwargs: recorded_event_types.append(event_type) or [])
    client = app.test_client()
    resp = client.post(
        "/review-order",
        headers={"Authorization": "Bearer test-token"},
        json={"order_id": 1001, "session_id": "session-1", "account_id": "account-1", "payment_method": "CARD", "items": [{"sku": "sku-1", "name": "Mouse", "size": "1", "quantity": 1, "unit_price": 2500}], "subtotal": 2500, "total": 2500},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["decision"] == "accept"
    assert data["payment_action"] == "capture_payment"
    assert data["customer_message"]
    assert data["rulelock_enabled"] is True
    assert data["account_action"] is None
    assert recorded_event_types == ["RULELOCK_REVIEW"]


def test_review_order_holds_when_rule_engine_is_unavailable(monkeypatch):
    import routes.events as events

    monkeypatch.setattr(events, "RULELOCK_API_TOKEN", None)
    monkeypatch.setattr(events, "RULELOCK_ALLOW_NO_AUTH", True)
    monkeypatch.setattr(events, "get_rulelock_setting", lambda: {"rulelock_enabled": True})
    monkeypatch.setattr(events, "get_review_event", lambda order_id, event_type="RULELOCK_REVIEW": None)
    monkeypatch.setattr(events, "session_features", lambda *args: {})
    monkeypatch.setattr(events, "call_rule_engine", lambda payload: {"available": False, "passed": False, "reason": "offline"})
    monkeypatch.setattr(events, "call_anomaly_engine", lambda features: {"available": True, "raw_score": 0.2, "is_anomaly": False})
    monkeypatch.setattr(events, "call_enforcement_engine", lambda **kwargs: (_ for _ in ()).throw(AssertionError("enforcement should be skipped")))
    monkeypatch.setattr(events, "insert_review_record", lambda *args, **kwargs: [])
    client = app.test_client()
    resp = client.post(
        "/review-order",
        json={"order_id": 1001, "session_id": "session-1", "account_id": "account-1", "items": [], "subtotal": 1000, "total": 1000},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["decision"] == "hold"
    assert data["payment_action"] == "hold_payment"
    assert data["rulelock_enabled"] is True


def test_review_order_always_reviews_when_cakely_toggle_is_disabled(monkeypatch):
    import routes.events as events

    monkeypatch.setattr(events, "RULELOCK_API_TOKEN", "test-token")
    monkeypatch.setattr(events, "get_review_event", lambda order_id, event_type="RULELOCK_REVIEW": None)
    monkeypatch.setattr(events, "session_features", lambda *args: {})
    monkeypatch.setattr(events, "call_rule_engine", lambda payload: {"available": True, "passed": True, "failures": []})
    monkeypatch.setattr(events, "call_anomaly_engine", lambda features: {"available": True, "raw_score": 0.2, "is_anomaly": False})
    monkeypatch.setattr(events, "call_enforcement_engine", lambda **kwargs: {"available": True, "decision": "accept"})
    monkeypatch.setattr(events, "insert_review_record", lambda *args, **kwargs: [])
    client = app.test_client()
    resp = client.post(
        "/review-order",
        headers={"Authorization": "Bearer test-token"},
        json={"order_id": 1001, "session_id": "session-1", "rulelock_enabled": False},
    )
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["rulelock_enabled"] is True
    assert data["decision"] == "accept"
    assert data["reason"] == "order passed RuleLock checks"


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
    monkeypatch.setattr(events, "get_device_events", lambda device_id: [
        {"user_id": 42, "metadata": {"account_id": "a1"}},
        {"user_id": 43, "metadata": {"account_id": "a2"}},
    ])
    monkeypatch.setattr(events, "get_phone_events", lambda phone_hash: [])
    features = events.session_features("session-1")
    assert features["coupon_attempts_per_session"] == 1
    assert features["avg_seconds_between_requests"] == 30
    assert features["distinct_accounts_same_device"] == 2
    assert features["distinct_addresses_same_phone"] == 1


def test_review_order_returns_stored_result_on_retry(monkeypatch):
    import routes.events as events

    stored = {"decision": "hold", "payment_action": "hold_payment", "reason": "internal",
              "customer_message": "Your order needs a quick review before it can continue.",
              "account_action": None, "rule_result": {}, "anomaly_result": {},
              "enforcement_result": {}, "rulelock_enabled": True, "order_id": 1234}
    monkeypatch.setattr(events, "RULELOCK_API_TOKEN", None)
    monkeypatch.setattr(events, "RULELOCK_ALLOW_NO_AUTH", True)
    monkeypatch.setattr(events, "get_review_event", lambda order_id, event_type="RULELOCK_REVIEW": {"metadata": stored})
    monkeypatch.setattr(events, "call_rule_engine", lambda payload: (_ for _ in ()).throw(AssertionError("must use stored result")))
    client = app.test_client()
    response = client.post("/review-order", json={"order_id": 1234})
    assert response.status_code == 200
    assert response.get_json()["decision"] == "hold"
    assert response.get_json()["reason"] == "internal"
    assert response.get_json()["customer_message"] == stored["customer_message"]


def test_simulation_review_uses_simulation_event_variant(monkeypatch):
    import routes.events as events

    event_types = []
    queried_types = []
    monkeypatch.setattr(events, "RULELOCK_API_TOKEN", "test-token")
    monkeypatch.setattr(events, "get_review_event", lambda order_id, event_type="RULELOCK_REVIEW": queried_types.append(event_type) or None)
    monkeypatch.setattr(events, "session_features", lambda *args: {})
    monkeypatch.setattr(events, "call_rule_engine", lambda payload: {"passed": True, "failures": []})
    monkeypatch.setattr(events, "call_anomaly_engine", lambda features: {"raw_score": 0.2, "is_anomaly": False})
    monkeypatch.setattr(events, "call_enforcement_engine", lambda **kwargs: {"decision": "accept"})
    monkeypatch.setattr(events, "insert_review_record", lambda event_type, *args, **kwargs: event_types.append(event_type) or [])
    response = app.test_client().post("/review-order", headers={"Authorization": "Bearer test-token"},
                                      json={"order_id": 1236, "simulation": True})
    assert response.status_code == 200
    assert queried_types == ["RULELOCK_SIMULATION"]
    assert event_types == ["RULELOCK_SIMULATION"]


def test_review_order_storage_failure_returns_controlled_hold(monkeypatch):
    import routes.events as events

    monkeypatch.setattr(events, "RULELOCK_API_TOKEN", None)
    monkeypatch.setattr(events, "RULELOCK_ALLOW_NO_AUTH", True)
    monkeypatch.setattr(events, "get_review_event", lambda order_id, event_type="RULELOCK_REVIEW": None)
    monkeypatch.setattr(events, "session_features", lambda *args: {})
    monkeypatch.setattr(events, "call_rule_engine", lambda payload: {"passed": True, "failures": []})
    monkeypatch.setattr(events, "call_anomaly_engine", lambda features: {"raw_score": 0.2, "is_anomaly": False})
    monkeypatch.setattr(events, "call_enforcement_engine", lambda **kwargs: {"decision": "accept"})
    monkeypatch.setattr(events, "insert_review_record", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("db down")))
    response = app.test_client().post("/review-order", json={"order_id": 1235})
    assert response.status_code == 200
    assert response.get_json()["decision"] == "hold"


def test_pipeline_info_exposes_model_metadata(monkeypatch):
    import anomaly_scoring

    expected = {"trained_at": "2026-10-03T00:00:00+00:00", "sklearn_version": "test", "thresholds": {"hold": -0.06, "reject": -0.1}}
    monkeypatch.setattr(anomaly_scoring, "model_metadata", lambda: expected)
    response = app.test_client().get("/pipeline/info")
    assert response.status_code == 200
    data = response.get_json()
    assert data["trained_at"] == expected["trained_at"]
    assert data["thresholds"] == expected["thresholds"]
    assert data["features"]
    assert data["rule_thresholds"]["max_coupons_per_session"] >= 1


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



