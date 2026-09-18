import requests
import uuid

from config import SUPABASE_SECRET_KEY, SUPABASE_URL


def _request(table, method="post", params=None, payload=None):
    if not SUPABASE_URL or not SUPABASE_SECRET_KEY:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SECRET_KEY must be configured")

    response = requests.request(
        method,
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers={
            "apikey": SUPABASE_SECRET_KEY,
            "Authorization": f"Bearer {SUPABASE_SECRET_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        },
        params=params,
        json=payload,
        timeout=5,
    )
    response.raise_for_status()
    return response.json() if response.content else []


def insert_event(event_type, session_id, user_id=None, order_id=None, metadata=None):
    return _request(
        "transaction_events",
        payload={
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "user_id": user_id,
            "order_id": order_id,
            "metadata": {"session_id": session_id, **(metadata or {})},
        },
    )


def get_products():
    """Read active products from the existing Cakely catalog."""
    try:
        rows = _request(
            "products",
            method="get",
            params={
                "select": "id,name,base_price,active",
                "active": "eq.true",
                "order": "id.asc",
            },
        )
    except (RuntimeError, requests.RequestException):
        return {}
    return {
        f"sku-{row['id']}": {
            "name": row["name"],
            "price": float(row["base_price"]),
        }
        for row in rows
    }


def get_coupon(code):
    """Read one active coupon from the existing Cakely catalog."""
    try:
        rows = _request(
            "coupons",
            method="get",
            params={
                "select": "code,discount_type,discount_value,minimum_order,max_discount,active",
                "code": f"eq.{code}",
                "active": "eq.true",
                "limit": "1",
            },
        )
    except (RuntimeError, requests.RequestException):
        return None
    return rows[0] if rows else None


def get_session_events(session_id):
    return _request(
        "transaction_events",
        method="get",
        params={"select": "event_type,created_at,metadata", "metadata->>session_id": f"eq.{session_id}", "order": "created_at.asc"},
    )
