import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_SECRET_KEY = os.environ.get("SUPABASE_SECRET_KEY", "")
RULELOCK_API_TOKEN = os.environ.get("RULELOCK_API_TOKEN") or None
CAKELY_ORIGINS = [
	origin.strip().rstrip("/")
	for origin in os.environ.get(
		"CAKELY_ORIGINS",
		"https://charukagimhan2020-hub.github.io,https://nimble-blancmange-3cb45c.netlify.app",
	).split(",")
	if origin.strip()
]
PORT = int(os.environ.get("PORT", "5001"))
