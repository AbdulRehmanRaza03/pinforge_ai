"""config.py — All settings via environment variables. Zero hardcoded secrets."""

import os
from dotenv import load_dotenv

load_dotenv()


def _int(key: str, default: int) -> int:
    try:
        return int(os.getenv(key, default))
    except (TypeError, ValueError):
        return default


class Settings:
    APP_NAME = "PinForge AI"
    ENV = os.getenv("ENV", "development")
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

    # Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")  # server-side only
    SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "")

    # Database (Supabase Postgres connection string)
    DATABASE_URL = os.getenv("DATABASE_URL", "")

    # Pinterest API v5 (official only)
    PINTEREST_APP_ID = os.getenv("PINTEREST_APP_ID", "")
    PINTEREST_APP_SECRET = os.getenv("PINTEREST_APP_SECRET", "")
    PINTEREST_REDIRECT_URI = os.getenv("PINTEREST_REDIRECT_URI", "http://localhost:8000/api/accounts/callback")
    PINTEREST_API_BASE = "https://api.pinterest.com/v5"
    PINTEREST_SCOPES = "boards:read,boards:write,pins:read,pins:write,user_accounts:read"

    # AI — Gemini primary, others optional via user settings
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    DEFAULT_AI_PROVIDER = os.getenv("DEFAULT_AI_PROVIDER", "gemini")  # gemini | openai | deepseek

    # Safety limits (hard-capped — cannot be overridden higher)
    MAX_PINS_PER_ACCOUNT_PER_DAY = min(_int("MAX_PINS_PER_ACCOUNT_PER_DAY", 15), 15)
    MIN_DELAY_MINUTES = max(_int("MIN_DELAY_MINUTES", 15), 15)
    MAX_DELAY_MINUTES = min(_int("MAX_DELAY_MINUTES", 60), 120)

    # Image
    PIN_WIDTH = 1000
    PIN_HEIGHT = 1500
    MAX_UPLOAD_MB = 20
    ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp"}

    # Storage
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "static/uploads")
    PROCESSED_DIR = os.getenv("PROCESSED_DIR", "static/processed")

    @classmethod
    def missing(cls) -> list[str]:
        required = [
            ("SUPABASE_URL", cls.SUPABASE_URL),
            ("SUPABASE_SERVICE_KEY", cls.SUPABASE_SERVICE_KEY),
            ("SUPABASE_JWT_SECRET", cls.SUPABASE_JWT_SECRET),
            ("DATABASE_URL", cls.DATABASE_URL),
            ("PINTEREST_APP_ID", cls.PINTEREST_APP_ID),
            ("PINTEREST_APP_SECRET", cls.PINTEREST_APP_SECRET),
        ]
        return [k for k, v in required if not v]


settings = Settings()
