"""Configuration from environment variables (and an optional .env file). No secrets in code."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load_dotenv():
    p = ROOT / ".env"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")  # gemini | openai_compat | anthropic
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "")
LLM_JSON_MODE = os.getenv("LLM_JSON_MODE", "1") == "1"
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "90"))

PORT = int(os.getenv("PORT", "8000"))
DB_PATH = os.getenv("DB_PATH", str(ROOT / "data" / "lawyer.db"))
RETENTION_DAYS = int(os.getenv("RETENTION_DAYS", "30"))
MAX_INPUT_CHARS = int(os.getenv("MAX_INPUT_CHARS", "3000"))
RATE_LIMIT_PER_5MIN = int(os.getenv("RATE_LIMIT_PER_5MIN", "40"))
SUBSTANTIAL_AMOUNT_INR = int(os.getenv("SUBSTANTIAL_AMOUNT_INR", "200000"))
MAX_FOLLOWUP_ROUNDS = int(os.getenv("MAX_FOLLOWUP_ROUNDS", "3"))
