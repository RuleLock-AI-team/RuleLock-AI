"""
RuleLock AI — Component 4: Automated Enforcement Engine (service wrapper)
Owner: Mishen
"""
from flask import Flask, request, jsonify
from decision import decide
from audit_log import record, all_entries

app = Flask(__name__)


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
    app.run(debug=True, port=5004)