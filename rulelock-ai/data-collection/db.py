import requests
import uuid
import logging
from datetime import datetime, timedelta, timezone

from config import SUPABASE_SECRET_KEY, SUPABASE_URL

logger = logging.getLogger(__name__)


def _request(table, method="post", params=None, payload=None, headers=None):
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
            **(headers or {}),
        },
        params=params,
        json=payload,
        timeout=5,
    )
    response.raise_for_status()
    return response.json() if response.content else []


def get_products():
    """Read active products from the existing Cakely catalog."""
    try:
        rows = _request(
            "products",
            method="get",
            params={
                "select": "id,name,base_price,active,sizes",
                "active": "eq.true",
                "order": "id.asc",
            },
        )
    except (RuntimeError, requests.RequestException):
        # Older Cakely schemas may not have a sizes column yet.
        try:
            rows = _request(
                "products", method="get",
                params={"select": "id,name,base_price,active", "active": "eq.true", "order": "id.asc"},
            )
        except (RuntimeError, requests.RequestException):
            logger.exception("Could not load product catalog")
            raise
    return {
        f"sku-{row['id']}": {
            "name": row["name"],
            "price": float(row["base_price"]),
            "sizes": row.get("sizes"),
        }
        for row in rows
    }


def get_account_profile(user_id):
    """Load the live account identity and completed-order count."""
    if user_id is None:
        raise ValueError("user_id is required")
    rows = _request("users", method="get", params={
        "select": "id,username,created_at", "id": f"eq.{user_id}", "limit": "1",
    })
    if not rows:
        return {"user_id": user_id, "username": None, "account_age_days": 0, "completed_orders": 0}
    user = rows[0]
    created = datetime.fromisoformat(str(user["created_at"]).replace("Z", "+00:00"))
    if created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)
    age_days = max(0, (datetime.now(timezone.utc) - created).days)
    completed = _count_rows("orders", {"user_id": f"eq.{user_id}", "status": "eq.COMPLETED"})
    return {"user_id": user_id, "username": user.get("username"),
            "account_age_days": age_days, "completed_orders": completed}


def get_usernames(user_ids):
    ids = [str(value) for value in user_ids if value is not None]
    if not ids:
        return {}
    rows = _request("users", method="get", params={
        "select": "id,username", "id": f"in.({','.join(ids)})", "limit": str(len(ids)),
    })
    return {str(row["id"]): row.get("username") for row in rows}


def get_cod_history(user_id, exclude_order_id=None):
    """Return prior COD order totals and customer-caused bad outcomes."""
    if user_id is None:
        raise ValueError("user_id is required")
    params = {"select": "id,status,cancelled_by", "user_id": f"eq.{user_id}",
              "payment_method": "eq.COD", "limit": "10000"}
    if exclude_order_id is not None:
        params["id"] = f"neq.{exclude_order_id}"
    rows = _request("orders", method="get", params=params)
    bad = sum(1 for row in rows if row.get("status") == "REFUSED" or
              (row.get("status") == "CANCELLED" and row.get("cancelled_by") == "CUSTOMER"))
    return {"total": len(rows), "bad": bad}


def get_order_reference(order_id):
    """Look up Cakely's human-readable order number from the shared orders table."""
    rows = _request("orders", method="get", params={
        "select": "order_number", "id": f"eq.{order_id}", "limit": "1",
    })
    return str(rows[0]["order_number"]) if rows and rows[0].get("order_number") else None


def get_order_references(order_ids):
    ids = [str(value) for value in order_ids if value is not None]
    if not ids:
        return {}
    rows = _request("orders", method="get", params={
        "select": "id,order_number", "id": f"in.({','.join(ids)})", "limit": str(len(ids)),
    })
    return {str(row["id"]): str(row["order_number"]) for row in rows if row.get("order_number")}


def get_order_id_by_reference(order_reference):
    rows = _request("orders", method="get", params={
        "select": "id", "order_number": f"eq.{order_reference}", "limit": "1",
    })
    return rows[0].get("id") if rows else None


def get_session_events(session_id):
    return _request(
        "transaction_events",
        method="get",
        params={"select": "event_type,created_at,user_id,metadata", "metadata->>session_id": f"eq.{session_id}", "order": "created_at.asc", "limit": "1000"},
    )


def _get_metadata_events(field, value, hours=24, event_type=None, select="event_type,user_id,order_id,metadata"):
    if not value:
        return []
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    params = {"select": select, f"metadata->>{field}": f"eq.{value}",
              "created_at": f"gte.{since.isoformat()}", "order": "created_at.desc", "limit": "1000"}
    if event_type:
        params["event_type"] = f"eq.{event_type}"
    return _request("transaction_events", method="get", params=params)


def get_device_events(device_id, hours=24):
    return _get_metadata_events("device_id", device_id, hours=hours)


def get_phone_events(phone_hash, hours=24):
    return _get_metadata_events("phone_hash", phone_hash, hours=hours)


def get_coupon_review_count(account_id, hours=24):
    rows = _get_metadata_events("account_id", account_id, hours=hours,
                                event_type="RULELOCK_REVIEW", select="event_id,metadata")
    return sum(bool((row.get("metadata") or {}).get("coupons_applied")) for row in rows)


def get_review_event(order_id, event_type="RULELOCK_REVIEW"):
    rows = _request("transaction_events", method="get", params={
        "select": "event_id,event_type,created_at,user_id,order_id,metadata",
        "event_type": f"eq.{event_type}", "order_id": f"eq.{order_id}",
        "order": "created_at.desc", "limit": "1",
    })
    return rows[0] if rows else None


def check_supabase():
    """Perform a small authenticated read for the readiness endpoint."""
    return _request("transaction_events", method="get", params={"select": "event_id", "limit": "1"})


def get_recent_review_events(hours=24, limit=200):
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    return _request(
        "transaction_events",
        method="get",
        params={
            "select": "event_id,event_type,created_at,user_id,order_id,metadata",
            "event_type": "eq.RULELOCK_REVIEW",
            "created_at": f"gte.{since.isoformat()}",
            "order": "created_at.desc",
            "limit": str(limit),
        },
    )


def _audit_payload(event_id, event_type, order_id, metadata):
    rule = metadata.get("rule_result") or {}
    anomaly = metadata.get("anomaly_result") or {}
    decision = metadata.get("decision", "hold")
    action = {"accept": "PASS", "hold": "HOLD", "reject": "REJECT", "void_discount": "VOID"}.get(decision, "HOLD")
    payload = {
        "event_id": str(event_id),
        "event_type": event_type,
        "order_id": order_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "decision": decision,
        "reason": str(metadata.get("reason", ""))[:1000],
        "order_reference": metadata.get("order_reference"),
        "account_id": str(metadata.get("account_id"))[:200] if metadata.get("account_id") is not None else None,
        "payment_method": str(metadata.get("payment_method", ""))[:40],
        "total": metadata.get("total"),
        "rule_code": rule.get("rule_code"),
        "anomaly_score": anomaly.get("raw_score"),
    }
    if payload["order_reference"] is not None:
        payload["order_reference"] = str(payload["order_reference"])[:200]
    return payload


def insert_audit_log(event_id, event_type, order_id, metadata):
    """Insert an immutable, minimal audit row; repeated inserts are harmless."""
    return _request("rulelock_audit_log", params={"on_conflict": "event_id"}, payload=_audit_payload(event_id, event_type, order_id, metadata),
                    headers={"Prefer": "resolution=ignore-duplicates,return=representation"})


def insert_review_record(event_type, session_id, user_id, order_id, metadata, event_id):
    """Atomically write the transaction event and its immutable audit row."""
    event = {
        "event_id": str(event_id), "event_type": event_type, "user_id": user_id,
        "order_id": order_id, "metadata": {"session_id": session_id, **(metadata or {})},
    }
    audit = _audit_payload(event_id, event_type, order_id, metadata or {})
    return _request("rpc/record_rulelock_review", payload={"p_event": event, "p_audit": audit})


def get_audit_log(action=None, search=None, cursor=None, limit=50, start=None, end=None):
    """Filter and paginate in PostgREST before rows are limited."""
    params = {
        "select": "audit_id,event_id,event_type,created_at,order_id,action,decision,reason,rule_code,anomaly_score,order_reference,account_id,payment_method,total",
        "event_type": "eq.RULELOCK_REVIEW",
        "order": "audit_id.desc",
        "limit": str(limit + 1),
    }
    if action and action != "ALL":
        params["action"] = f"eq.{action}"
    if cursor is not None:
        params["audit_id"] = f"lt.{int(cursor)}"
    if start is not None or end is not None:
        clauses = []
        if start is not None:
            clauses.append(f"created_at.gte.{start.isoformat()}")
        if end is not None:
            clauses.append(f"created_at.lt.{end.isoformat()}")
        params["and"] = f"({','.join(clauses)})"
    if search:
        term = "".join(ch for ch in search[:80] if ch.isalnum() or ch in " -_./")
        if term:
            escaped = term.replace("*", "")
            clauses = [f"{field}.ilike.*{escaped}*" for field in ("order_reference", "account_id", "rule_code", "reason")]
            if escaped.isdigit():
                clauses.append(f"order_id.eq.{escaped}")
            params["or"] = f"({','.join(clauses)})"
    return _request("rulelock_audit_log", method="get", params=params)


def _count_rows(table, params):
    if not SUPABASE_URL or not SUPABASE_SECRET_KEY:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SECRET_KEY must be configured")
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers={"apikey": SUPABASE_SECRET_KEY, "Authorization": f"Bearer {SUPABASE_SECRET_KEY}", "Prefer": "count=exact", "Range": "0-0"},
        params={**params, "select": "*"}, timeout=5,
    )
    response.raise_for_status()
    content_range = response.headers.get("Content-Range", "*/0")
    return int(content_range.rsplit("/", 1)[-1])


def count_audit_events(start, end, blocked_only=False):
    params = {"event_type": "eq.RULELOCK_REVIEW", "and": f"(created_at.gte.{start.isoformat()},created_at.lt.{end.isoformat()})"}
    if blocked_only:
        params["decision"] = "in.(hold,reject)"
    return _count_rows("rulelock_audit_log", params)


def count_transaction_events(event_type, start, end):
    return _count_rows("transaction_events", {
        "event_type": f"eq.{event_type}",
        "and": f"(created_at.gte.{start.isoformat()},created_at.lt.{end.isoformat()})",
    })


def get_rulelock_setting():
    """Read Cakely's owner toggle when the shared settings table exists."""
    try:
        rows = _request(
            "platform_settings",
            method="get",
            params={"select": "id,rulelock_enabled,updated_at", "order": "id.asc", "limit": "1"},
        )
    except (RuntimeError, requests.RequestException):
        logger.exception("Could not read RuleLock setting")
        return None
    return rows[0] if rows else None


def set_rulelock_setting(enabled: bool):
    """Update Cakely's owner toggle in the shared settings table."""
    setting = get_rulelock_setting()
    method = "patch" if setting else "post"
    params = {"id": f"eq.{setting['id']}"} if setting else None
    payload = {"rulelock_enabled": bool(enabled)}
    rows = _request("platform_settings", method=method, params=params, payload=payload)
    return rows[0] if rows else {"rulelock_enabled": bool(enabled)}
