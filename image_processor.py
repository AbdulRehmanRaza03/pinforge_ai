"""
image_processor.py
Resizes/optimizes uploaded images to Pinterest's recommended 2:3 ratio,
strips EXIF metadata (privacy), and saves a web-ready JPEG.
"""

import os
import io
import uuid
from PIL import Image, ImageOps

from config import Config
from utils import get_logger, hash_image_bytes

logger = get_logger("image_processor")


class ImageProcessor:
    def __init__(self):
        os.makedirs(Config.PROCESSED_DIR, exist_ok=True)

    def process(self, file_bytes: bytes, original_filename: str) -> dict:
        """
        Returns dict: {processed_path, content_hash, width, height}
        Resizes to Pinterest-recommended 1000x1500 (2:3), center-cropped,
        strips EXIF, re-encodes as optimized JPEG.
        """
        content_hash = hash_image_bytes(file_bytes)

        img = Image.open(io.BytesIO(file_bytes))
        img = ImageOps.exif_transpose(img)  # respect orientation, then we strip exif on save
        img = img.convert("RGB")

        target_w, target_h = Config.PIN_IMAGE_WIDTH, Config.PIN_IMAGE_HEIGHT
        img = ImageOps.fit(img, (target_w, target_h), method=Image.LANCZOS, centering=(0.5, 0.5))

        out_name = f"{uuid.uuid4().hex}.jpg"
        out_path = os.path.join(Config.PROCESSED_DIR, out_name)

        # Save without EXIF (Pillow omits it by default unless explicitly passed)
        img.save(out_path, format="JPEG", quality=88, optimize=True)

        return {
            "processed_path": out_path,
            "content_hash": content_hash,
            "width": target_w,
            "height": target_h,
        }

    @staticmethod
    def to_base64(processed_path: str) -> str:
        import base64
        with open(processed_path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    @staticmethod
    def validate_dimensions(file_bytes: bytes, min_width: int = 200, min_height: int = 300) -> bool:
        try:
            img = Image.open(io.BytesIO(file_bytes))
            return img.width >= min_width and img.height >= min_height
        except Exception as e:
            logger.warning("Image validation failed: %s", e)
            return False
