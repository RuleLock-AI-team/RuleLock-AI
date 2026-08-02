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


@app.post("/score")
def score():
    """
    TODO (Nihara): this returns IsolationForest's raw decision_function
    score (lower = more anomalous). Evaluate with precision/recall/FPR
    per the proposal and calibrate a real threshold before wiring this
    into the enforcement engine.
    """
    session = request.json
    features = session_to_features(session)
    model = get_model()
    raw_score = model.decision_function(features)[0]
    return jsonify(raw_score=float(raw_score))


if __name__ == "__main__":
    app.run(debug=True, port=5003)
