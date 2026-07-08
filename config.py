"""
config.py
Central configuration. ALL secrets come from environment variables (.env) or Streamlit secrets.
Never hardcode credentials here.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Try to import Streamlit secrets for Cloud deployment; fall back to env vars
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False


def _get_secret(key: str, default: str = "") -> str:
    """Get value from Streamlit secrets (Cloud) or environment variables (local)."""
    if HAS_STREAMLIT:
        try:
            return st.secrets.get(key, os.getenv(key, default))
        except Exception:
            return os.getenv(key, default)
    return os.getenv(key, default)


def _get_int(key: str, default: int) -> int:
    try:
        val = _get_secret(key, str(default))
        return int(val)
    except (TypeError, ValueError):
        return default


class Config:
    # --- App ---
    APP_NAME = "PinForge AI"
    SECRET_KEY = _get_secret("SECRET_KEY", "")
    ENV = _get_secret("ENV", "development")  # development | production

    # --- Database ---
    DATABASE_URL = _get_secret("DATABASE_URL", "sqlite:///pinforge.db")

    # --- Pinterest OAuth2 (Pinterest API v5) ---
    PINTEREST_APP_ID = _get_secret("PINTEREST_APP_ID", "")
    PINTEREST_APP_SECRET = _get_secret("PINTEREST_APP_SECRET", "")
    PINTEREST_REDIRECT_URI = _get_secret("PINTEREST_REDIRECT_URI", "http://localhost:8501")
    PINTEREST_API_BASE = "https://api.pinterest.com/v5"
    PINTEREST_OAUTH_AUTHORIZE_URL = "https://www.pinterest.com/oauth/"
    PINTEREST_OAUTH_TOKEN_URL = "https://api.pinterest.com/v5/oauth/token"
    # Scopes needed for board/pin creation + read
    PINTEREST_SCOPES = "boards:read,boards:write,pins:read,pins:write,user_accounts:read"

    # --- AI content generation (Anthropic Claude) ---
    ANTHROPIC_API_KEY = _get_secret("ANTHROPIC_API_KEY", "")
    AI_MODEL = _get_secret("AI_MODEL", "claude-sonnet-4-6")

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
    UPLOAD_DIR = _get_secret("UPLOAD_DIR", "static/uploads")
    PROCESSED_DIR = _get_secret("PROCESSED_DIR", "static/processed")

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
