"""
utils.py
Shared helper functions: hashing, randomized safety delays, logging, validation.
"""

import hashlib
import logging
import os
import random
import re
from datetime import datetime, timedelta

from config import Config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def hash_image_bytes(image_bytes: bytes) -> str:
    """SHA-256 hash of raw image bytes — used for duplicate-content detection."""
    return hashlib.sha256(image_bytes).hexdigest()


def hash_content(title: str, description: str) -> str:
    """Hash of title+description text, combined with image hash for full dup check."""
    normalized = (title.strip().lower() + "|" + description.strip().lower())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def random_safety_delay_minutes() -> int:
    """
    Random delay between MIN_DELAY_MINUTES and MAX_DELAY_MINUTES (config-capped).
    Mimics natural human posting cadence — never post pins back-to-back.
    """
    return random.randint(Config.MIN_DELAY_MINUTES, Config.MAX_DELAY_MINUTES)


def next_schedule_time(after: datetime = None) -> datetime:
    base = after or datetime.utcnow()
    return base + timedelta(minutes=random_safety_delay_minutes())


def validate_image_extension(filename: str) -> bool:
    ext = os.path.splitext(filename.lower())[1]
    return ext in Config.ALLOWED_IMAGE_EXT


def validate_file_size(size_bytes: int) -> bool:
    return size_bytes <= Config.MAX_UPLOAD_MB * 1024 * 1024


def sanitize_title(title: str) -> str:
    """Pinterest pin titles: max 100 chars, strip newlines/control chars."""
    title = re.sub(r"[\r\n\t]", " ", title).strip()
    return title[:100]


def sanitize_description(desc: str) -> str:
    """Pinterest descriptions: max 500 chars."""
    desc = re.sub(r"[\r\n]+", " ", desc).strip()
    return desc[:500]


def ensure_dirs():
    os.makedirs(Config.UPLOAD_DIR, exist_ok=True)
    os.makedirs(Config.PROCESSED_DIR, exist_ok=True)


def is_valid_email(email: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))
