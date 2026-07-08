"""routers/accounts.py — Pinterest account connect/disconnect/list."""

import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from database import get_db_dep
from middleware.auth import get_current_user
from models import User, PinterestAccount
from services.pinterest_service import PinterestService, PinterestError

router = APIRouter(prefix="/api/accounts", tags=["accounts"])

# Temp in-memory store for OAuth state (use Redis in high-scale prod)
_oauth_states: dict[str, int] = {}  # state -> user_id


@router.get("/auth-url")
def get_auth_url(
    user: User = Depends(get_current_user),
):
    state = uuid.uuid4().hex
    _oauth_states[state] = user.id
    return {"url": PinterestService.build_auth_url(state)}


@router.get("/callback")
def oauth_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: Session = Depends(get_db_dep),
):
    """Pinterest redirects here after user approves. Exchanges code → stores tokens → redirects to dashboard."""
    from config import settings

    user_id = _oauth_states.pop(state, None)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid OAuth state.")

    try:
        tok = PinterestService.exchange_code(code)
        api = PinterestService(tok["access_token"])
        info = api.get_account()
    except PinterestError as e:
        return RedirectResponse(f"{settings.FRONTEND_URL}/dashboard/accounts?error={str(e)}")

    pinterest_uid = info.get("username", "unknown")
    existing = (
        db.query(PinterestAccount)
        .filter(PinterestAccount.user_id == user_id, PinterestAccount.pinterest_user_id == pinterest_uid)
        .first()
    )
    expires_at = datetime.utcnow() + timedelta(seconds=tok.get("expires_in", 3600))
    if existing:
        existing.access_token = tok["access_token"]
        existing.refresh_token = tok.get("refresh_token", existing.refresh_token)
        existing.token_expires_at = expires_at
        existing.is_active = True
    else:
        db.add(PinterestAccount(
            user_id=user_id,
            pinterest_user_id=pinterest_uid,
            username=info.get("username"),
            display_name=info.get("business_name") or info.get("username"),
            profile_image=info.get("profile_image", {}).get("medium") if info.get("profile_image") else None,
            access_token=tok["access_token"],
            refresh_token=tok.get("refresh_token"),
            token_expires_at=expires_at,
        ))
    db.commit()
    return RedirectResponse(f"{settings.FRONTEND_URL}/dashboard/accounts?connected=1")


@router.get("/")
def list_accounts(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db_dep),
):
    accounts = db.query(PinterestAccount).filter(
        PinterestAccount.user_id == user.id,
        PinterestAccount.is_active == True,  # noqa
    ).all()
    return [
        {
            "id": a.id,
            "username": a.username,
            "display_name": a.display_name,
            "profile_image": a.profile_image,
            "connected_at": a.connected_at.isoformat(),
        }
        for a in accounts
    ]


@router.delete("/{account_id}")
def disconnect_account(
    account_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db_dep),
):
    acct = db.query(PinterestAccount).filter(
        PinterestAccount.id == account_id,
        PinterestAccount.user_id == user.id,
    ).first()
    if not acct:
        raise HTTPException(status_code=404, detail="Account not found.")
    acct.is_active = False
    return {"message": "Disconnected."}


@router.get("/{account_id}/boards")
def get_boards(
    account_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db_dep),
):
    acct = db.query(PinterestAccount).filter(
        PinterestAccount.id == account_id,
        PinterestAccount.user_id == user.id,
    ).first()
    if not acct:
        raise HTTPException(status_code=404, detail="Account not found.")
    try:
        api = PinterestService(acct.access_token)
        boards = api.list_boards()
        return boards
    except PinterestError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{account_id}/boards")
def create_board(
    account_id: int,
    payload: dict,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db_dep),
):
    acct = db.query(PinterestAccount).filter(
        PinterestAccount.id == account_id,
        PinterestAccount.user_id == user.id,
    ).first()
    if not acct:
        raise HTTPException(status_code=404, detail="Account not found.")
    try:
        api = PinterestService(acct.access_token)
        board = api.create_board(payload.get("name", "New Board"), payload.get("description", ""))
        return board
    except PinterestError as e:
        raise HTTPException(status_code=400, detail=str(e))
