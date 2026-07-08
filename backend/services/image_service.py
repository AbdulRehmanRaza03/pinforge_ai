"""services/image_service.py — Pillow image prep: 2:3 crop, EXIF strip, hash."""

import base64
import hashlib
import io
import os
import uuid

from PIL import Image, ImageOps

from config import settings


class ImageError(Exception):
    pass


def process_image(file_bytes: bytes, original_name: str) -> dict:
    """
    Returns: {processed_path, content_hash, width, height, filename}
    Crops to 1000x1500 (Pinterest 2:3), strips EXIF, saves optimized JPEG.
    """
    os.makedirs(settings.PROCESSED_DIR, exist_ok=True)

    content_hash = hashlib.sha256(file_bytes).hexdigest()

    try:
        img = Image.open(io.BytesIO(file_bytes))
    except Exception as e:
        raise ImageError(f"Cannot open image: {e}")

    img = ImageOps.exif_transpose(img).convert("RGB")
    img = ImageOps.fit(img, (settings.PIN_WIDTH, settings.PIN_HEIGHT), method=Image.LANCZOS)

    fname = f"{uuid.uuid4().hex}.jpg"
    out_path = os.path.join(settings.PROCESSED_DIR, fname)
    img.save(out_path, format="JPEG", quality=88, optimize=True)

    return {
        "processed_path": out_path,
        "content_hash": content_hash,
        "width": settings.PIN_WIDTH,
        "height": settings.PIN_HEIGHT,
        "filename": fname,
    }


def to_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def validate_upload(file_bytes: bytes, filename: str) -> str | None:
    """Returns error string or None if valid."""
    ext = os.path.splitext(filename.lower())[1]
    if ext not in settings.ALLOWED_EXT:
        return f"File type '{ext}' not allowed. Use: {', '.join(settings.ALLOWED_EXT)}"
    if len(file_bytes) > settings.MAX_UPLOAD_MB * 1024 * 1024:
        return f"File too large. Max {settings.MAX_UPLOAD_MB}MB."
    try:
        Image.open(io.BytesIO(file_bytes)).verify()
    except Exception:
        return "File is not a valid image."
    return None
