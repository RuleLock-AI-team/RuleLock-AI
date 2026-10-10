import os
import logging

from flask import Flask, jsonify, request, make_response
from flask_cors import CORS

from config import CAKELY_ORIGINS, DASHBOARD_PASSWORD, DASHBOARD_SESSION_SECRET, DASHBOARD_USER, IS_PRODUCTION, PORT
from db import check_supabase
from anomaly_scoring import MODEL_PATH, _get_model, is_model_loaded
from routes.events import bp as events_bp

app = Flask(__name__, static_folder=None)
logger = logging.getLogger(__name__)
CORS(app, origins=CAKELY_ORIGINS, supports_credentials=True)
app.register_blueprint(events_bp)


@app.post("/login")
def dashboard_login():
    credentials = request.get_json(silent=True) or {}
    if not DASHBOARD_USER or not DASHBOARD_PASSWORD or not DASHBOARD_SESSION_SECRET:
        return jsonify(error="dashboard login is not configured"), 503
    if credentials.get("username") != DASHBOARD_USER or credentials.get("password") != DASHBOARD_PASSWORD:
        return jsonify(error="invalid username or password"), 401
    from routes.events import dashboard_cookie
    response = make_response(jsonify(authenticated=True))
    response.set_cookie(
        "rulelock_dashboard_session",
        dashboard_cookie(),
        max_age=4 * 60 * 60,
        httponly=True,
        secure=True,
        samesite="None",
    )
    return response


@app.post("/logout")
def dashboard_logout():
    response = make_response(jsonify(authenticated=False))
    response.set_cookie("rulelock_dashboard_session", "", max_age=0, httponly=True, secure=True, samesite="None")
    return response

if os.path.isfile(MODEL_PATH):
    _get_model()
elif IS_PRODUCTION:
    raise RuntimeError("anomaly model is required in production")


@app.get("/health")
def health():
    return jsonify(status="ok"), 200


@app.get("/ready")
def ready():
    checks = {"model_loaded": is_model_loaded(), "supabase_reachable": False}
    try:
        check_supabase()
        checks["supabase_reachable"] = True
    except Exception:
        logger.exception("Supabase readiness check failed")
    is_ready = all(checks.values())
    return jsonify(ready=is_ready, checks=checks), 200 if is_ready else 503


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=PORT,
        debug=False,
    )
