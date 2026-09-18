"""
RuleLock AI — Component 2: Business Rule Validation Engine (service wrapper)
Owner: Sadini
"""
import os

from flask import Flask, request, jsonify
from rules import validate_transaction

app = Flask(__name__)


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
