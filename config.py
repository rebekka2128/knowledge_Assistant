import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

WEB_BASE_URL = os.getenv("WEB_BASE_URL")
HEADLESS = os.getenv("HEADLESS","true").lower() == "true"
SLOW_MO= float(os.getenv("SLOW_MO", "0"))

API_BASE_URL = os.getenv("API_BASE_URL", (WEB_BASE_URL or "").rstrip("/"))
API_TIMEOUT_SECONDS = float(os.getenv("API_TIMEOUT_SECONDS", "15"))