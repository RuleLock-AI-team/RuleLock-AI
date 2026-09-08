from flask import Blueprint, jsonify, request
from datetime import datetime

from catalog import DEFAULT_PRODUCTS
from db import get_coupon, get_products, get_session_events, insert_event
from services.forwarder import call_anomaly_engine, call_rule_engine

bp = Blueprint("events", __name__)

COUPONS = {
    "WELCOME10": {"type": "percent", "value": 10},
    "SAVE500": {"type": "flat", "value": 500},
}


def session_features(session_id):
    rows = get_session_events(session_id) or []
    span_seconds = 0
    if len(rows) >= 2:
        first = datetime.fromisoformat(rows[0]["created_at"].replace("Z", "+00:00"))
        last = datetime.fromisoformat(rows[-1]["created_at"].replace("Z", "+00:00"))
        span_seconds = (last - first).total_seconds()
    return {
        "session_id": session_id,
        "event_count": len(rows),
        "coupon_attempts": sum(row["event_type"] == "APPLY_COUPON" for row in rows),
        "checkout_count": sum(row["event_type"] == "CHECKOUT" for row in rows),
        "session_span_seconds": span_seconds,
    }


def _subtotal(items):
    products = get_products() or DEFAULT_PRODUCTS
    return sum(products[item["sku"]]["price"] * item["qty"] for item in items)


def _bigint(value):
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


@bp.post("/cart")
def cart():
    body = request.get_json(silent=True) or {}
    items = body.get("items", [])
    try:
        subtotal = _subtotal(items)
    except (KeyError, TypeError, ValueError):
        return jsonify(error="items must contain valid sku and qty values"), 400

    session_id = body.get("session_id")
    if session_id:
        insert_event("ADD_TO_CART", session_id, _bigint(body.get("user_id")), metadata={"items": items, "ip": request.remote_addr})
        return jsonify(status="logged", subtotal=subtotal), 201
    return jsonify(subtotal=subtotal), 200


@bp.post("/apply-coupon")
def apply_coupon():
    body = request.get_json(silent=True) or {}
    code = body.get("coupon_code", body.get("code"))
    subtotal = body.get("subtotal", 0)
    stored_coupon = get_coupon(code) if code else None
    if stored_coupon:
        coupon = {
            "type": "percent" if stored_coupon["discount_type"] == "PERCENTAGE" else "flat",
            "value": float(stored_coupon["discount_value"]),
            "minimum_order": float(stored_coupon["minimum_order"]),
            "max_discount": stored_coupon["max_discount"],
        }
    else:
        coupon = COUPONS.get(code)
    if not coupon:
        return jsonify(error="invalid coupon"), 400
    if subtotal < coupon.get("minimum_order", 0):
        return jsonify(error="minimum order amount not met"), 400

    discount = subtotal * coupon["value"] / 100 if coupon["type"] == "percent" else coupon["value"]
    if coupon.get("max_discount") is not None:
        discount = min(discount, float(coupon["max_discount"]))
    session_id = body.get("session_id")
    if session_id:
        insert_event("APPLY_COUPON", session_id, _bigint(body.get("user_id")), metadata={"coupon_code": code, "discount": discount})
        return jsonify(status="logged", subtotal=subtotal, discount=discount, total=subtotal - discount), 201
    return jsonify(subtotal=subtotal, discount=discount, total=subtotal - discount), 200


@bp.post("/checkout")
def checkout():
    body = request.get_json(silent=True) or {}
    session_id = body.get("session_id") or request.headers.get("X-Session-ID")
    order_id = body.get("order_id")
    if not session_id or not order_id:
        return jsonify(error="session_id and order_id are required"), 400
    numeric_order_id = _bigint(order_id)
    if numeric_order_id is None:
        return jsonify(error="order_id must be an existing numeric order id"), 400

    insert_event("CHECKOUT", session_id, _bigint(body.get("user_id")), numeric_order_id, {"order": body})
    insert_event("CHECKOUT_FORWARDED", session_id, _bigint(body.get("user_id")), numeric_order_id, {"reason": "order received"})

    rule_result = call_rule_engine(body)
    anomaly_result = call_anomaly_engine(session_features(session_id))
    insert_event(
        "PIPELINE_RESULT",
        session_id,
        _bigint(body.get("user_id")),
        numeric_order_id,
        {"rule_result": rule_result, "anomaly_result": anomaly_result},
    )
    return jsonify(order_id=order_id, rule_result=rule_result, anomaly_result=anomaly_result), 200
