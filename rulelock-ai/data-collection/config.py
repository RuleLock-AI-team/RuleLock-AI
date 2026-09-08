import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_SECRET_KEY = os.environ.get("SUPABASE_SECRET_KEY", "")
RULE_ENGINE_URL = os.environ.get("RULE_ENGINE_URL") or None
ANOMALY_ENGINE_URL = os.environ.get("ANOMALY_ENGINE_URL") or None
PORT = int(os.environ.get("PORT", "5001"))
