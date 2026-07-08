"""routers/pins.py — Image upload, AI content generation, queue management."""

import hashlib
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from database import get_db_dep
from middleware.auth import get_current_user
from models import PinQueue, PinStatus, PostHistory, User, PinterestAccount
from services import ai_service, image_service
from services.scheduler_service import add_to_queue

router = APIRouter(prefix="/api/pins", tags=["pins"])


@router.post("/generate-content")
async def generate_content(
    product_description: str = Form(...),
    keywords: str = Form(""),
    ai_provider: str = Form("gemini"),
    image: Optional[UploadFile] = File(None),
    user: User = Depends(get_current_user),
):
    image_bytes = await image.read() if image else None
    # Use user's own key if set, else fall back to server key
    api_key = (
        user.gemini_key if ai_provider == "gemini" and user.gemini_key
        else user.openai_key if ai_provider == "openai" and user.openai_key
        else None
    )
    try:
        content = ai_service.generate_pin_content(
            product_description=product_description,
            keywords=keywords,
            image_bytes=image_bytes,
            provider=ai_provider,
            api_key=api_key,
        )
        return content
    except ai_service.AIError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/queue")
async def add_pin_to_queue(
    account_id: int = Form(...),
    board_id: str = Form(...),
    board_name: str = Form(""),
    title: str = Form(...),
    description: str = Form(...),
    alt_text: str = Form(""),
    hashtags: str = Form(""),
    destination_link: str = Form(""),
    image: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db_dep),
):
    # Verify account belongs to user
    acct = db.query(PinterestAccount).filter(
        PinterestAccount.id == account_id,
        PinterestAccount.user_id == user.id,
    ).first()
    if not acct:
        raise HTTPException(status_code=404, detail="Pinterest account not found.")

    file_bytes = await image.read()
    err = image_service.validate_upload(file_bytes, image.filename)
    if err:
        raise HTTPException(status_code=400, detail=err)

    processed = image_service.process_image(file_bytes, image.filename)
    content_hash = hashlib.sha256(
        (title.lower().strip() + "|" + description.lower().strip()).encode()
    ).hexdigest()

    item = add_to_queue(
        db=db,
        account_id=account_id,
        image_path=processed["processed_path"],
        image_filename=processed["filename"],
        title=title[:100],
        description=description[:500],
        alt_text=alt_text[:500],
        hashtags=hashtags,
        board_id=board_id,
        board_name=board_name,
        content_hash=content_hash,
        destination_link=destination_link or None,
    )
    return {
        "id": item.id,
        "status": item.status.value,
        "scheduled_for": item.scheduled_for.isoformat() if item.scheduled_for else None,
        "title": item.title,
    }


@router.get("/queue")
def get_queue(
    account_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db_dep),
):
    # Verify account belongs to user
    acct = db.query(PinterestAccount).filter(
        PinterestAccount.id == account_id,
        PinterestAccount.user_id == user.id,
    ).first()
    if not acct:
        raise HTTPException(status_code=404, detail="Account not found.")

    items = (
        db.query(PinQueue)
        .filter(PinQueue.account_id == account_id)
        .order_by(PinQueue.scheduled_for.asc())
        .all()
    )
    return [
        {
            "id": i.id,
            "title": i.title,
            "description": i.description,
            "board_name": i.board_name,
            "status": i.status.value,
            "scheduled_for": i.scheduled_for.isoformat() if i.scheduled_for else None,
            "posted_at": i.posted_at.isoformat() if i.posted_at else None,
            "destination_link": i.destination_link,
            "error_message": i.error_message,
            "image_filename": i.image_filename,
        }
        for i in items
    ]


@router.delete("/queue/{item_id}")
def remove_from_queue(
    item_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db_dep),
):
    item = db.query(PinQueue).join(PinterestAccount).filter(
        PinQueue.id == item_id,
        PinterestAccount.user_id == user.id,
        PinQueue.status.in_([PinStatus.SCHEDULED, PinStatus.QUEUED]),
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Queue item not found or already processed.")
    db.delete(item)
    return {"message": "Removed from queue."}


@router.get("/history")
def get_history(
    account_id: int,
    limit: int = 50,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db_dep),
):
    acct = db.query(PinterestAccount).filter(
        PinterestAccount.id == account_id,
        PinterestAccount.user_id == user.id,
    ).first()
    if not acct:
        raise HTTPException(status_code=404, detail="Account not found.")

    rows = (
        db.query(PostHistory)
        .filter(PostHistory.account_id == account_id)
        .order_by(PostHistory.occurred_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": r.id,
            "title": r.title,
            "board_name": r.board_name,
            "status": r.status.value,
            "detail": r.detail,
            "pinterest_pin_id": r.pinterest_pin_id,
            "occurred_at": r.occurred_at.isoformat(),
        }
        for r in rows
    ]
