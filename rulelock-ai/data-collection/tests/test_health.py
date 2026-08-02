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
