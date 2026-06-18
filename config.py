"""
config.py
Central configuration. ALL secrets come from environment variables (.env).
Never hardcode credentials here.
"""

import os
from dotenv import load_dotenv

load_dotenv()


def _get_int(key: str, default: int) -> int:
    try:
        return int(os.getenv(key, default))
    except (TypeError, ValueError):
        return default


class Config:
    # --- App ---
    APP_NAME = "PinForge AI"
    SECRET_KEY = os.getenv("SECRET_KEY", "")
    ENV = os.getenv("ENV", "development")  # development | production

    # --- Database ---
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///pinforge.db")

    # --- Pinterest OAuth2 (Pinterest API v5) ---
    PINTEREST_APP_ID = os.getenv("PINTEREST_APP_ID", "")
    PINTEREST_APP_SECRET = os.getenv("PINTEREST_APP_SECRET", "")
    PINTEREST_REDIRECT_URI = os.getenv("PINTEREST_REDIRECT_URI", "http://localhost:8501")
    PINTEREST_API_BASE = "https://api.pinterest.com/v5"
    PINTEREST_OAUTH_AUTHORIZE_URL = "https://www.pinterest.com/oauth/"
    PINTEREST_OAUTH_TOKEN_URL = "https://api.pinterest.com/v5/oauth/token"
    # Scopes needed for board/pin creation + read
    PINTEREST_SCOPES = "boards:read,boards:write,pins:read,pins:write,user_accounts:read"

    # --- AI content generation (Anthropic Claude) ---
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    AI_MODEL = os.getenv("AI_MODEL", "claude-sonnet-4-6")

    # --- Safety / Rate limiting (HARD CAPS, do not bypass) ---
    MAX_PINS_PER_ACCOUNT_PER_DAY = min(_get_int("MAX_PINS_PER_ACCOUNT_PER_DAY", 15), 15)
    MIN_DELAY_MINUTES = max(_get_int("MIN_DELAY_MINUTES", 15), 15)
    MAX_DELAY_MINUTES = min(_get_int("MAX_DELAY_MINUTES", 60), 120)

    # --- Image processing ---
    PIN_IMAGE_WIDTH = 1000
    PIN_IMAGE_HEIGHT = 1500  # Pinterest recommended 2:3 ratio
    ALLOWED_IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp"}
    MAX_UPLOAD_MB = 20

    # --- Storage ---
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "static/uploads")
    PROCESSED_DIR = os.getenv("PROCESSED_DIR", "static/processed")

    @classmethod
    def validate(cls) -> list:
        """Return list of missing-required-config warnings (does not raise)."""
        warnings = []
        if not cls.PINTEREST_APP_ID or not cls.PINTEREST_APP_SECRET:
            warnings.append("Pinterest app credentials not set (PINTEREST_APP_ID / PINTEREST_APP_SECRET).")
        if not cls.ANTHROPIC_API_KEY:
            warnings.append("ANTHROPIC_API_KEY not set — AI content generation disabled.")
        if not cls.SECRET_KEY:
            warnings.append("SECRET_KEY not set — use a long random value in production.")
        return warnings
