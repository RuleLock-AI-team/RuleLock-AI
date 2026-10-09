import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import db


def test_cross_session_queries_use_postgrest_metadata_filters(monkeypatch):
    captured = []
    monkeypatch.setattr(db, "_request", lambda table, **kwargs: captured.append((table, kwargs)) or [])
    db.get_device_events("device-1")
    db.get_phone_events("phone-hash-1")
    assert captured[0][1]["params"]["metadata->>device_id"] == "eq.device-1"
    assert captured[1][1]["params"]["metadata->>phone_hash"] == "eq.phone-hash-1"
