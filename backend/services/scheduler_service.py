"""
services/scheduler_service.py
Background scheduler: posts queued pins with safety checks every 2 minutes.
Enforces: daily cap, randomized delays, duplicate prevention, token refresh.
"""

import random
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from models import PinQueue, PinStatus, PostHistory, PinterestAccount
from services.pinterest_service import PinterestService, PinterestError, token_expired
from services.image_service import to_base64

_scheduler = BackgroundScheduler()
_running = False


def start():
    global _running
    if not _running:
        _scheduler.add_job(
            _process_queue, "interval", minutes=2,
            id="pin_queue_processor", replace_existing=True
        )
        _scheduler.start()
        _running = True


def stop():
    global _running
    if _running:
        _scheduler.shutdown(wait=False)
        _running = False


# ── Safety helpers ──────────────────────────────────────────────────────────

def pins_today(db: Session, account_id: int) -> int:
    since = datetime.utcnow() - timedelta(hours=24)
    return (
        db.query(PostHistory)
        .filter(
            PostHistory.account_id == account_id,
            PostHistory.status == PinStatus.POSTED,
            PostHistory.occurred_at >= since,
        ).count()
    )


def is_duplicate(db: Session, account_id: int, content_hash: str) -> bool:
    return (
        db.query(PinQueue)
        .filter(
            PinQueue.account_id == account_id,
            PinQueue.content_hash == content_hash,
            PinQueue.status == PinStatus.POSTED,
        ).first() is not None
    )


def safe_next_time(db: Session, account_id: int) -> datetime:
    """Schedule after last queued item + random human delay."""
    last = (
        db.query(PinQueue)
        .filter(
            PinQueue.account_id == account_id,
            PinQueue.status.in_([PinStatus.SCHEDULED, PinStatus.QUEUED]),
        )
        .order_by(PinQueue.scheduled_for.desc())
        .first()
    )
    base = last.scheduled_for if last and last.scheduled_for else datetime.utcnow()
    delay = random.randint(settings.MIN_DELAY_MINUTES, settings.MAX_DELAY_MINUTES)
    return base + timedelta(minutes=delay)


# ── Queue operations ────────────────────────────────────────────────────────

def add_to_queue(
    db: Session,
    account_id: int,
    image_path: str,
    image_filename: str,
    title: str,
    description: str,
    alt_text: str,
    hashtags: str,
    board_id: str,
    board_name: str,
    content_hash: str,
    destination_link: str = None,
) -> PinQueue:
    scheduled_for = safe_next_time(db, account_id)
    item = PinQueue(
        account_id=account_id,
        image_path=image_path,
        image_filename=image_filename,
        title=title,
        description=description,
        alt_text=alt_text,
        hashtags=hashtags,
        destination_link=destination_link,
        board_id=board_id,
        board_name=board_name,
        content_hash=content_hash,
        status=PinStatus.SCHEDULED,
        scheduled_for=scheduled_for,
    )
    db.add(item)
    db.flush()
    return item


# ── Scheduler job ───────────────────────────────────────────────────────────

def _process_queue():
    with get_db() as db:
        due = (
            db.query(PinQueue)
            .filter(
                PinQueue.status == PinStatus.SCHEDULED,
                PinQueue.scheduled_for <= datetime.utcnow(),
            ).all()
        )
        for item in due:
            _post_item(db, item)


def _post_item(db: Session, item: PinQueue):
    account = db.query(PinterestAccount).get(item.account_id)
    if not account or not account.is_active:
        _update(db, item, PinStatus.FAILED, "Account inactive.")
        return

    # Safety: daily cap
    if pins_today(db, account.id) >= settings.MAX_PINS_PER_ACCOUNT_PER_DAY:
        _update(db, item, PinStatus.RATE_LIMIT, f"Daily cap of {settings.MAX_PINS_PER_ACCOUNT_PER_DAY} reached. Deferred.")
        return

    # Safety: duplicate
    if is_duplicate(db, account.id, item.content_hash):
        _update(db, item, PinStatus.DUPLICATE, "Same content already posted to this account.")
        return

    # Refresh token if needed
    if token_expired(account.token_expires_at):
        try:
            tok = PinterestService.refresh_token(account.refresh_token)
            account.access_token = tok["access_token"]
            account.token_expires_at = datetime.utcnow() + timedelta(seconds=tok.get("expires_in", 3600))
        except PinterestError as e:
            _update(db, item, PinStatus.FAILED, f"Token refresh failed: {e}")
            return

    # Post
    try:
        api = PinterestService(account.access_token)
        b64 = to_base64(item.image_path)
        desc = item.description + (f" {item.hashtags}" if item.hashtags else "")
        result = api.create_pin(
            board_id=item.board_id,
            image_b64=b64,
            title=item.title,
            description=desc,
            alt_text=item.alt_text or "",
            link=item.destination_link,
        )
        item.status = PinStatus.POSTED
        item.posted_at = datetime.utcnow()
        _log(db, item, PinStatus.POSTED, "Posted successfully.", result.get("id"))
    except PinterestError as e:
        _update(db, item, PinStatus.FAILED, str(e))


def _update(db: Session, item: PinQueue, status: PinStatus, msg: str):
    item.status = status
    item.error_message = msg
    _log(db, item, status, msg)


def _log(db: Session, item: PinQueue, status: PinStatus, detail: str, pin_id: str = None):
    db.add(PostHistory(
        account_id=item.account_id,
        queue_item_id=item.id,
        pinterest_pin_id=pin_id,
        title=item.title,
        board_name=item.board_name,
        status=status,
        detail=detail,
    ))
