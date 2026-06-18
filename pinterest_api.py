"""
pinterest_api.py
Thin wrapper around the OFFICIAL Pinterest API v5 (OAuth2 only).
No scraping. No headless browsers. No unofficial endpoints.
Docs: https://developers.pinterest.com/docs/api/v5/
"""

import base64
import requests
from datetime import datetime, timedelta

from config import Config
from utils import get_logger

logger = get_logger("pinterest_api")


class PinterestAPIError(Exception):
    pass


class PinterestAPI:
    """
    Wraps Pinterest API v5 OAuth2 flow + the handful of endpoints PinForge AI needs:
    boards (list/create) and pins (create). All requests use the user's own
    access token obtained via the standard OAuth2 authorization-code flow.
    """

    def __init__(self, access_token: str = None):
        self.access_token = access_token

    # ---------- OAuth2 flow ----------

    @staticmethod
    def get_authorization_url(state: str) -> str:
        """Build the URL the user is sent to on Pinterest to grant access."""
        params = (
            f"?client_id={Config.PINTEREST_APP_ID}"
            f"&redirect_uri={Config.PINTEREST_REDIRECT_URI}"
            f"&response_type=code"
            f"&scope={Config.PINTEREST_SCOPES}"
            f"&state={state}"
        )
        return Config.PINTEREST_OAUTH_AUTHORIZE_URL + params

    @staticmethod
    def exchange_code_for_token(auth_code: str) -> dict:
        """Exchange the authorization code (callback ?code=...) for tokens."""
        basic = base64.b64encode(
            f"{Config.PINTEREST_APP_ID}:{Config.PINTEREST_APP_SECRET}".encode()
        ).decode()
        headers = {
            "Authorization": f"Basic {basic}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": Config.PINTEREST_REDIRECT_URI,
        }
        resp = requests.post(Config.PINTEREST_OAUTH_TOKEN_URL, headers=headers, data=data, timeout=20)
        if resp.status_code != 200:
            logger.error("Token exchange failed: %s", resp.text)
            raise PinterestAPIError(f"Token exchange failed: {resp.text}")
        return resp.json()

    @staticmethod
    def refresh_access_token(refresh_token: str) -> dict:
        basic = base64.b64encode(
            f"{Config.PINTEREST_APP_ID}:{Config.PINTEREST_APP_SECRET}".encode()
        ).decode()
        headers = {
            "Authorization": f"Basic {basic}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {"grant_type": "refresh_token", "refresh_token": refresh_token}
        resp = requests.post(Config.PINTEREST_OAUTH_TOKEN_URL, headers=headers, data=data, timeout=20)
        if resp.status_code != 200:
            raise PinterestAPIError(f"Token refresh failed: {resp.text}")
        return resp.json()

    # ---------- helpers ----------

    def _headers(self) -> dict:
        if not self.access_token:
            raise PinterestAPIError("No access token set on PinterestAPI instance.")
        return {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}

    def _request(self, method: str, path: str, **kwargs) -> dict:
        url = f"{Config.PINTEREST_API_BASE}{path}"
        resp = requests.request(method, url, headers=self._headers(), timeout=30, **kwargs)
        if resp.status_code == 429:
            raise PinterestAPIError("Pinterest API rate limit hit (HTTP 429). Back off and retry later.")
        if resp.status_code >= 400:
            logger.error("Pinterest API error %s: %s", resp.status_code, resp.text)
            raise PinterestAPIError(f"Pinterest API error {resp.status_code}: {resp.text}")
        return resp.json() if resp.text else {}

    # ---------- account ----------

    def get_user_account(self) -> dict:
        return self._request("GET", "/user_account")

    # ---------- boards ----------

    def list_boards(self, page_size: int = 25) -> list:
        data = self._request("GET", f"/boards?page_size={page_size}")
        return data.get("items", [])

    def create_board(self, name: str, description: str = "") -> dict:
        payload = {"name": name[:180], "description": description[:500], "privacy": "PUBLIC"}
        return self._request("POST", "/boards", json=payload)

    # ---------- pins ----------

    def create_pin(
        self,
        board_id: str,
        image_url: str = None,
        image_base64: str = None,
        title: str = "",
        description: str = "",
        alt_text: str = "",
        link: str = None,
    ) -> dict:
        """
        Create a pin on the given board. Provide EITHER a public image_url OR
        image_base64 (raw base64 string, no data: prefix) — Pinterest v5 supports both.
        """
        if not image_url and not image_base64:
            raise PinterestAPIError("create_pin requires image_url or image_base64.")

        media_source = (
            {"source_type": "image_url", "url": image_url}
            if image_url
            else {"source_type": "image_base64", "content_type": "image/jpeg", "data": image_base64}
        )

        payload = {
            "board_id": board_id,
            "title": title[:100],
            "description": description[:500],
            "alt_text": alt_text[:500] if alt_text else "",
            "media_source": media_source,
        }
        if link:
            payload["link"] = link

        return self._request("POST", "/pins", json=payload)

    def get_pin_analytics_summary(self, pin_id: str) -> dict:
        """Basic analytics — requires the user_accounts:read scope and an active campaign or org account."""
        try:
            return self._request(
                "GET",
                f"/pins/{pin_id}/analytics?metric_types=IMPRESSION,SAVE_ALL_TIME,PIN_CLICK",
            )
        except PinterestAPIError as e:
            logger.warning("Analytics fetch failed for pin %s: %s", pin_id, e)
            return {}


def token_is_expired(expires_at: datetime) -> bool:
    if not expires_at:
        return False
    return datetime.utcnow() >= (expires_at - timedelta(minutes=5))
