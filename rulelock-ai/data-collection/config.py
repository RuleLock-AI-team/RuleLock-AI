import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_SECRET_KEY = os.environ.get("SUPABASE_SECRET_KEY", "")
RULELOCK_API_TOKEN = os.environ.get("RULELOCK_API_TOKEN") or None
RULELOCK_ALLOW_NO_AUTH = os.environ.get("RULELOCK_ALLOW_NO_AUTH", "0") == "1"
DASHBOARD_USER = os.environ.get("DASHBOARD_USER", "")
DASHBOARD_PASSWORD = os.environ.get("DASHBOARD_PASSWORD", "")
DASHBOARD_SESSION_SECRET = os.environ.get("DASHBOARD_SESSION_SECRET", "")
APP_ENV = (os.environ.get("APP_ENV") or os.environ.get("ENVIRONMENT") or os.environ.get("FLASK_ENV") or "").strip().lower()
IS_PRODUCTION = APP_ENV in {"production", "prod"} or os.environ.get("RENDER", "").lower() == "true"


def validate_auth_configuration(token=RULELOCK_API_TOKEN, production=IS_PRODUCTION):
    if production and not token:
        raise RuntimeError("RULELOCK_API_TOKEN is required in production")


validate_auth_configuration()
CAKELY_ORIGINS = [
	origin.strip().rstrip("/")
	for origin in os.environ.get(
		"CAKELY_ORIGINS",
		"https://rulelock-ai-team.github.io",
	).split(",")
	if origin.strip()
]
PORT = int(os.environ.get("PORT", "5001"))
