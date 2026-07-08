"""routers/settings_router.py — User profile and AI key settings."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db_dep
from middleware.auth import get_current_user
from models import AIProvider, User

router = APIRouter(prefix="/api/settings", tags=["settings"])


class SettingsUpdate(BaseModel):
    full_name: str | None = None
    ai_provider: str | None = None
    gemini_key: str | None = None
    openai_key: str | None = None


@router.get("/")
def get_settings(user: User = Depends(get_current_user)):
    return {
        "email": user.email,
        "full_name": user.full_name,
        "ai_provider": user.ai_provider.value if user.ai_provider else "gemini",
        "has_gemini_key": bool(user.gemini_key),
        "has_openai_key": bool(user.openai_key),
    }


@router.patch("/")
def update_settings(
    payload: SettingsUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db_dep),
):
    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.ai_provider:
        try:
            user.ai_provider = AIProvider(payload.ai_provider)
        except ValueError:
            pass
    if payload.gemini_key is not None:
        user.gemini_key = payload.gemini_key or None
    if payload.openai_key is not None:
        user.openai_key = payload.openai_key or None
    return {"message": "Settings updated."}
