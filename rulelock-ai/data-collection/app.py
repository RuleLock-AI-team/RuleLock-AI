"""
RuleLock AI — Component 1: Transaction Monitoring & Data Collection
Owner: Charuka

The demo storefront's checkout API. Every checkout event should end up
in Postgres (see schema.sql) so Components 2-4 have real data to work
against.
"""
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder="static", static_url_path="")

PRODUCTS = {
    "sku-1": {"name": "Wireless Mouse", "price": 2500},
    "sku-2": {"name": "USB-C Cable", "price": 800},
}

COUPONS = {
    "WELCOME10": {"type": "percent", "value": 10},
    "SAVE500": {"type": "flat", "value": 500},
}


@app.get("/health")
def health():
    return jsonify(status="ok"), 200


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/browse")
def browse():
    return jsonify(PRODUCTS)


@app.post("/cart")
def build_cart():
    items = request.json.get("items", [])
    subtotal = sum(PRODUCTS[i["sku"]]["price"] * i["qty"] for i in items)
    return jsonify(subtotal=subtotal)


@app.post("/apply-coupon")
def apply_coupon():
    """
    TODO (Charuka's real coursework):
    - Write every attempt to `discounts_applied`, successful or not —
      the rule engine and anomaly model both need full attempt history.
    - Call rule-engine's POST /validate before confirming the discount.
    """
    data = request.json
    code = data.get("code")
    subtotal = data.get("subtotal", 0)
    coupon = COUPONS.get(code)
    if not coupon:
        return jsonify(error="invalid coupon"), 400
    discount = subtotal * coupon["value"] / 100 if coupon["type"] == "percent" else coupon["value"]
    return jsonify(subtotal=subtotal, discount=discount, total=subtotal - discount)


@app.post("/checkout")
def checkout():
    """
    TODO (Charuka's real coursework):
    - Persist order, order_items, session, and (if COD) a pending
      delivery_outcomes row to Postgres.
    - Capture session_id/device_id in middleware, not per-route.
    - Call rule-engine's /validate, then anomaly-detection's /score,
      then enforcement-engine's /enforce, in that order, before
      returning a final status to the client.
    """
    import uuid
    order_id = str(uuid.uuid4())
    data = request.json
    return jsonify(order_id=order_id, status="placed", order=data), 201


if __name__ == "__main__":
    app.run(debug=True, port=5001)
