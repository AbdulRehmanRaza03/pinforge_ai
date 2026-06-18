"""
ai_engine.py
AI-powered Pinterest content generation (title, description, hashtags, alt text)
using the Anthropic Claude API. Pure text generation from a user-supplied product
description — no scraping, no third-party content lifted from elsewhere.
"""

import json
import base64
import requests

from config import Config
from utils import get_logger, sanitize_title, sanitize_description

logger = get_logger("ai_engine")

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"

SYSTEM_PROMPT = """You are an expert Pinterest SEO copywriter. Given a product/topic
description (and optionally an image), generate Pinterest-optimized pin content.
Respond with ONLY valid JSON, no markdown fences, no preamble, matching exactly:
{"title": "...", "description": "...", "hashtags": ["#tag1", "#tag2", ...], "alt_text": "..."}
Rules:
- title: <= 100 characters, keyword-rich, compelling, no clickbait/false claims.
- description: <= 500 characters, natural sentences, include 2-3 relevant keywords, end with soft CTA.
- hashtags: 5-8 relevant hashtags, no spaces, no banned/spammy terms.
- alt_text: <= 500 characters, accessibility-focused factual description of the image/product.
"""


class AIEngineError(Exception):
    pass


class AIContentGenerator:
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or Config.ANTHROPIC_API_KEY
        self.model = model or Config.AI_MODEL

    def _call_claude(self, user_content) -> str:
        if not self.api_key:
            raise AIEngineError("ANTHROPIC_API_KEY not configured.")

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        body = {
            "model": self.model,
            "max_tokens": 600,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": user_content}],
        }
        resp = requests.post(ANTHROPIC_API_URL, headers=headers, json=body, timeout=30)
        if resp.status_code != 200:
            logger.error("Anthropic API error: %s", resp.text)
            raise AIEngineError(f"AI generation failed: {resp.text}")

        data = resp.json()
        text_blocks = [b["text"] for b in data.get("content", []) if b.get("type") == "text"]
        return "".join(text_blocks).strip()

    def generate_pin_content(self, product_description: str, image_bytes: bytes = None, keywords: str = "") -> dict:
        """
        Generate title/description/hashtags/alt_text.
        If image_bytes provided, sends the image to Claude for visual grounding.
        """
        prompt_text = (
            f"Product/topic description: {product_description}\n"
            f"Target keywords (optional): {keywords or 'none provided'}\n"
            f"Generate the Pinterest pin content JSON now."
        )

        if image_bytes:
            b64 = base64.b64encode(image_bytes).decode()
            user_content = [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": b64}},
                {"type": "text", "text": prompt_text},
            ]
        else:
            user_content = prompt_text

        raw = self._call_claude(user_content)
        raw_clean = raw.replace("```json", "").replace("```", "").strip()

        try:
            parsed = json.loads(raw_clean)
        except json.JSONDecodeError:
            logger.warning("AI returned non-JSON, falling back to plain text.")
            parsed = {
                "title": product_description[:100],
                "description": product_description[:500],
                "hashtags": [],
                "alt_text": product_description[:500],
            }

        return {
            "title": sanitize_title(parsed.get("title", "")),
            "description": sanitize_description(parsed.get("description", "")),
            "hashtags": " ".join(parsed.get("hashtags", [])[:8]),
            "alt_text": (parsed.get("alt_text", "") or "")[:500],
        }
