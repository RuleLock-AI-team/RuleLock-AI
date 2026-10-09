import os
import logging

from flask import Flask, jsonify
from flask_cors import CORS

from config import CAKELY_ORIGINS, IS_PRODUCTION, PORT
from db import check_supabase
from anomaly_scoring import MODEL_PATH, _get_model, is_model_loaded
from routes.events import bp as events_bp

app = Flask(__name__, static_folder=None)
logger = logging.getLogger(__name__)
CORS(app, origins=CAKELY_ORIGINS)
app.register_blueprint(events_bp)

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
