"""services/pinterest_service.py — Official Pinterest API v5. OAuth2 only. No scraping."""

import base64
from datetime import datetime, timedelta

import requests

from config import settings


class PinterestError(Exception):
    pass


class PinterestService:
    BASE = settings.PINTEREST_API_BASE

    def __init__(self, access_token: str):
        self.token = access_token

    # ── OAuth ──────────────────────────────────────────────────────────────
    @staticmethod
    def build_auth_url(state: str) -> str:
        return (
            f"https://www.pinterest.com/oauth/"
            f"?client_id={settings.PINTEREST_APP_ID}"
            f"&redirect_uri={settings.PINTEREST_REDIRECT_URI}"
            f"&response_type=code"
            f"&scope={settings.PINTEREST_SCOPES}"
            f"&state={state}"
        )

    @staticmethod
    def exchange_code(code: str) -> dict:
        basic = base64.b64encode(
            f"{settings.PINTEREST_APP_ID}:{settings.PINTEREST_APP_SECRET}".encode()
        ).decode()
        resp = requests.post(
            "https://api.pinterest.com/v5/oauth/token",
            headers={"Authorization": f"Basic {basic}", "Content-Type": "application/x-www-form-urlencoded"},
            data={"grant_type": "authorization_code", "code": code, "redirect_uri": settings.PINTEREST_REDIRECT_URI},
            timeout=20,
        )
        if resp.status_code != 200:
            raise PinterestError(f"Token exchange failed: {resp.text}")
        return resp.json()

    @staticmethod
    def refresh_token(refresh_token: str) -> dict:
        basic = base64.b64encode(
            f"{settings.PINTEREST_APP_ID}:{settings.PINTEREST_APP_SECRET}".encode()
        ).decode()
        resp = requests.post(
            "https://api.pinterest.com/v5/oauth/token",
            headers={"Authorization": f"Basic {basic}", "Content-Type": "application/x-www-form-urlencoded"},
            data={"grant_type": "refresh_token", "refresh_token": refresh_token},
            timeout=20,
        )
        if resp.status_code != 200:
            raise PinterestError(f"Token refresh failed: {resp.text}")
        return resp.json()

    # ── Internal ───────────────────────────────────────────────────────────
    def _headers(self):
        return {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

    def _get(self, path: str, params: dict = None) -> dict:
        r = requests.get(f"{self.BASE}{path}", headers=self._headers(), params=params, timeout=30)
        self._raise(r)
        return r.json()

    def _post(self, path: str, payload: dict) -> dict:
        r = requests.post(f"{self.BASE}{path}", headers=self._headers(), json=payload, timeout=30)
        self._raise(r)
        return r.json()

    @staticmethod
    def _raise(resp: requests.Response):
        if resp.status_code == 429:
            raise PinterestError("Pinterest rate limit hit (HTTP 429). Try later.")
        if resp.status_code >= 400:
            raise PinterestError(f"Pinterest API {resp.status_code}: {resp.text}")

    # ── Account ────────────────────────────────────────────────────────────
    def get_account(self) -> dict:
        return self._get("/user_account")

    # ── Boards ─────────────────────────────────────────────────────────────
    def list_boards(self) -> list:
        return self._get("/boards", {"page_size": 50}).get("items", [])

    def create_board(self, name: str, description: str = "") -> dict:
        return self._post("/boards", {"name": name[:180], "description": description[:500], "privacy": "PUBLIC"})

    # ── Pins ───────────────────────────────────────────────────────────────
    def create_pin(
        self,
        board_id: str,
        image_b64: str,
        title: str,
        description: str,
        alt_text: str = "",
        link: str = None,
    ) -> dict:
        payload = {
            "board_id": board_id,
            "title": title[:100],
            "description": description[:500],
            "alt_text": alt_text[:500] if alt_text else "",
            "media_source": {
                "source_type": "image_base64",
                "content_type": "image/jpeg",
                "data": image_b64,
            },
        }
        if link:
            payload["link"] = link
        return self._post("/pins", payload)


def token_expired(expires_at: datetime | None) -> bool:
    if not expires_at:
        return False
    return datetime.utcnow() >= (expires_at - timedelta(minutes=5))
