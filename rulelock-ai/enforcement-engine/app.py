"""
RuleLock AI — Component 4: Automated Enforcement Engine (service wrapper)
Owner: Mishen
"""
import os

from flask import Flask, request, jsonify
from flask_cors import CORS
from decision import decide
from audit_log import record, all_entries

app = Flask(__name__)
CORS(
    app,
    origins=[origin.strip().rstrip("/") for origin in os.environ.get(
        "CAKELY_ORIGINS",
        "https://charukagimhan2020-hub.github.io,https://nimble-blancmange-3cb45c.netlify.app",
    ).split(",") if origin.strip()],
)


@app.get("/health")
def health():
    return jsonify(status="ok"), 200


@app.post("/enforce")
def enforce():
    data = request.json
    result = decide(
        order_id=data["order_id"],
        account_id=data.get("account_id", ""),
        rule_passed=data["rule_passed"],
        rule_reason=data.get("rule_reason", ""),
        anomaly_score=data["anomaly_score"],
        payment_method=data.get("payment_method", "PREPAID"),
        rule_code=data.get("rule_code"),
    )
    if result["decision"] != "none":
        record(data["order_id"], result["decision"], result["reason"])
    return jsonify(result)


@app.get("/audit-log")
def audit_log_view():
    return jsonify(all_entries())


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "5004")),
        debug=os.environ.get("FLASK_DEBUG", "0") == "1",
    )