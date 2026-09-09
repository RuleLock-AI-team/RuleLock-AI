"""
RuleLock AI — Component 3: scoring API
Owner: Nihara

Wraps the trained Isolation Forest as a service the enforcement engine
calls for a real-time anomaly score.
"""
import os
import joblib
from flask import Flask, request, jsonify
from features import session_to_features

app = Flask(__name__)

MODEL_PATH = os.environ.get("MODEL_PATH", "model.joblib")
_model = None


def get_model():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model


@app.get("/health")
def health():
    return jsonify(status="ok"), 200


THRESHOLD = float(os.environ.get("ANOMALY_THRESHOLD", "-0.06"))

@app.post("/score")
def score():
    session = request.json
    features = session_to_features(session)
    model = get_model()
    raw_score = model.decision_function(features)[0]
    return jsonify(
        raw_score=float(raw_score),
        is_anomaly=bool(raw_score < THRESHOLD)
    )


if __name__ == "__main__":
    app.run(debug=True, port=5003)
