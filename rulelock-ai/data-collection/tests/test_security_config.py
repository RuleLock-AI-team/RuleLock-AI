import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config
import routes.events as events
from app import app


def test_production_requires_token_and_local_dev_may_start_without_one():
    try:
        config.validate_auth_configuration(token=None, production=True)
    except RuntimeError as exc:
        assert "RULELOCK_API_TOKEN" in str(exc)
    else:
        raise AssertionError("production without a token must fail startup")
    try:
        config.validate_auth_configuration(token=None, production=True)
    except RuntimeError:
        pass
    else:
        raise AssertionError("local override must never allow production startup without a token")
    config.validate_auth_configuration(token=None, production=False)


def test_backend_auth_fails_closed_without_token_or_override(monkeypatch):
    monkeypatch.setattr(events, "RULELOCK_API_TOKEN", None)
    monkeypatch.setattr(events, "RULELOCK_ALLOW_NO_AUTH", False)
    assert app.test_client().get("/audit-log").status_code == 401


def test_backend_local_override_is_explicit(monkeypatch):
    monkeypatch.setattr(events, "RULELOCK_API_TOKEN", None)
    monkeypatch.setattr(events, "RULELOCK_ALLOW_NO_AUTH", True)
    monkeypatch.setattr(events, "get_audit_log", lambda **kwargs: [])
    assert app.test_client().get("/audit-log").status_code == 200
