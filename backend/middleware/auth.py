"""middleware/auth.py — Verify Supabase JWT tokens on every protected route."""

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from config import settings
from database import get_db_dep
from models import User
from sqlalchemy.orm import Session

bearer_scheme = HTTPBearer()


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db_dep),
) -> User:
    """Decode Supabase JWT → find/create local User row."""
    token = creds.credentials
    try:
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired.")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {e}")

    supabase_uid = payload.get("sub")
    email = payload.get("email", "")
    if not supabase_uid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No sub in token.")

    user = db.query(User).filter(User.supabase_uid == supabase_uid).first()
    if not user:
        # Auto-create on first login
        user = User(supabase_uid=supabase_uid, email=email)
        db.add(user)
        db.flush()

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled.")

    return user
