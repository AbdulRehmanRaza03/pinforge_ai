"""
services/ai_service.py
AI-powered pin content generation. Supports Gemini (default/free), OpenAI, DeepSeek.
User can plug in their own API key via settings.
"""

import base64
import json
import re
import requests

from config import settings


SYSTEM_PROMPT = """You are a Pinterest SEO expert and copywriter.
Generate Pinterest-optimized pin content from the given product/topic details.
Output ONLY valid JSON, no markdown fences, exactly this structure:
{
  "title": "...",
  "description": "...",
  "hashtags": ["#tag1", "#tag2", ...],
  "alt_text": "..."
}
Rules:
- title: max 100 chars, keyword-rich, compelling, no clickbait
- description: max 500 chars, natural, 2-3 keywords, soft CTA at end
- hashtags: 5-8 relevant tags, no spaces in each tag
- alt_text: max 500 chars, accessibility-focused, factual visual description
Make it feel human-written, not AI-generated."""


class AIError(Exception):
    pass


def generate_pin_content(
    product_description: str,
    keywords: str = "",
    image_bytes: bytes = None,
    provider: str = None,
    api_key: str = None,
) -> dict:
    """Route to correct AI provider. Returns parsed content dict."""
    p = (provider or settings.DEFAULT_AI_PROVIDER).lower()
    key = api_key or (settings.GEMINI_API_KEY if p == "gemini" else settings.OPENAI_API_KEY)

    if not key:
        raise AIError(f"No API key for provider '{p}'. Add it in Settings.")

    if p == "gemini":
        raw = _gemini(key, product_description, keywords, image_bytes)
    elif p == "openai":
        raw = _openai(key, product_description, keywords, image_bytes)
    elif p == "deepseek":
        raw = _deepseek(key, product_description, keywords)
    else:
        raise AIError(f"Unknown provider: {p}")

    return _parse(raw, product_description)


# ── Gemini ──────────────────────────────────────────────────────────────────

def _gemini(api_key: str, desc: str, keywords: str, image_bytes: bytes = None) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    parts = []
    if image_bytes:
        parts.append({"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(image_bytes).decode()}})
    parts.append({"text": f"{SYSTEM_PROMPT}\n\nProduct: {desc}\nKeywords: {keywords or 'none'}\n\nGenerate JSON now:"})
    body = {"contents": [{"parts": parts}], "generationConfig": {"maxOutputTokens": 600, "temperature": 0.7}}
    r = requests.post(url, json=body, timeout=30)
    if r.status_code != 200:
        raise AIError(f"Gemini error {r.status_code}: {r.text}")
    return r.json()["candidates"][0]["content"]["parts"][0]["text"]


# ── OpenAI ──────────────────────────────────────────────────────────────────

def _openai(api_key: str, desc: str, keywords: str, image_bytes: bytes = None) -> str:
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    user_parts = []
    if image_bytes:
        b64 = base64.b64encode(image_bytes).decode()
        user_parts.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}})
    user_parts.append({"type": "text", "text": f"Product: {desc}\nKeywords: {keywords or 'none'}\n\nGenerate JSON now:"})
    messages.append({"role": "user", "content": user_parts})
    body = {"model": "gpt-4o-mini", "messages": messages, "max_tokens": 600}
    r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=body, timeout=30)
    if r.status_code != 200:
        raise AIError(f"OpenAI error {r.status_code}: {r.text}")
    return r.json()["choices"][0]["message"]["content"]


# ── DeepSeek ────────────────────────────────────────────────────────────────

def _deepseek(api_key: str, desc: str, keywords: str) -> str:
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Product: {desc}\nKeywords: {keywords or 'none'}\n\nGenerate JSON now:"},
        ],
        "max_tokens": 600,
    }
    r = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=body, timeout=30)
    if r.status_code != 200:
        raise AIError(f"DeepSeek error {r.status_code}: {r.text}")
    return r.json()["choices"][0]["message"]["content"]


# ── Parser ──────────────────────────────────────────────────────────────────

def _parse(raw: str, fallback: str) -> dict:
    clean = re.sub(r"```json|```", "", raw).strip()
    try:
        data = json.loads(clean)
        return {
            "title": str(data.get("title", ""))[:100],
            "description": str(data.get("description", ""))[:500],
            "hashtags": " ".join(data.get("hashtags", [])[:8]),
            "alt_text": str(data.get("alt_text", ""))[:500],
        }
    except (json.JSONDecodeError, KeyError):
        return {"title": fallback[:100], "description": fallback[:500], "hashtags": "", "alt_text": fallback[:500]}
