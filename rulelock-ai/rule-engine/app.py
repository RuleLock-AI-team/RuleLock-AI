"""
RuleLock AI — Component 2: Business Rule Validation Engine (service wrapper)
Owner: Sadini
"""
import os

from flask import Flask, request, jsonify
from flask_cors import CORS
from rules import validate_transaction

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


@app.post("/validate")
def validate():
    """TODO: wire to validate_transaction() once it's implemented."""
    transaction = request.json
    result = validate_transaction(transaction)
    return jsonify(result)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "5002")),
        debug=os.environ.get("FLASK_DEBUG", "0") == "1",
    )
