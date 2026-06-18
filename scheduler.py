"""
scheduler.py
Safety-first scheduling engine. Enforces, on every single call:
  1. Hard daily pin cap per Pinterest account (Config.MAX_PINS_PER_ACCOUNT_PER_DAY)
  2. Randomized human-like delay between posts (Config.MIN/MAX_DELAY_MINUTES)
  3. Duplicate-content prevention (content_hash uniqueness per account)
  4. Every post is logged to PostHistory regardless of outcome
Runs via APScheduler BackgroundScheduler — started once from app.py.
"""

from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler

from database import get_session
from models import PinQueueItem, PinStatus, PostHistory, PinterestAccount
from pinterest_api import PinterestAPI, PinterestAPIError, token_is_expired
from image_processor import ImageProcessor
from utils import get_logger, next_schedule_time
from config import Config

logger = get_logger("scheduler")

_scheduler = BackgroundScheduler()
_started = False


def start_scheduler():
    global _started
    if not _started:
        _scheduler.add_job(process_due_queue_items, "interval", minutes=2, id="queue_processor", replace_existing=True)
        _scheduler.start()
        _started = True
        logger.info("Scheduler started: checking queue every 2 minutes.")


def shutdown_scheduler():
    global _started
    if _started:
        _scheduler.shutdown(wait=False)
        _started = False


# ---------- core safety checks ----------

def pins_posted_today(db, account_id: int) -> int:
    since = datetime.utcnow() - timedelta(hours=24)
    return (
        db.query(PostHistory)
        .filter(
            PostHistory.account_id == account_id,
            PostHistory.status == PinStatus.POSTED,
            PostHistory.occurred_at >= since,
        )
        .count()
    )


def is_duplicate_content(db, account_id: int, content_hash: str) -> bool:
    existing = (
        db.query(PinQueueItem)
        .filter(
            PinQueueItem.account_id == account_id,
            PinQueueItem.content_hash == content_hash,
            PinQueueItem.status == PinStatus.POSTED,
        )
        .first()
    )
    return existing is not None


# ---------- queue operations ----------

def enqueue_pin(db, account_id: int, image_path: str, title: str, description: str,
                 alt_text: str, hashtags: str, board_id: str, content_hash: str,
                 destination_link: str = None, schedule_after: datetime = None) -> PinQueueItem:
    """Add a pin to the queue with a randomized, safety-delayed schedule time."""
    last_scheduled = (
        db.query(PinQueueItem)
        .filter(PinQueueItem.account_id == account_id, PinQueueItem.status.in_([PinStatus.QUEUED, PinStatus.SCHEDULED]))
        .order_by(PinQueueItem.scheduled_for.desc())
        .first()
    )
    base_time = schedule_after or (last_scheduled.scheduled_for if last_scheduled else datetime.utcnow())
    scheduled_for = next_schedule_time(after=base_time)

    item = PinQueueItem(
        account_id=account_id,
        image_path=image_path,
        title=title,
        description=description,
        alt_text=alt_text,
        hashtags=hashtags,
        destination_link=destination_link,
        board_id=board_id,
        content_hash=content_hash,
        status=PinStatus.SCHEDULED,
        scheduled_for=scheduled_for,
    )
    db.add(item)
    db.flush()
    return item


def process_due_queue_items():
    """Background job: posts any SCHEDULED item whose time has come, respecting all safety rules."""
    with get_session() as db:
        due_items = (
            db.query(PinQueueItem)
            .filter(PinQueueItem.status == PinStatus.SCHEDULED, PinQueueItem.scheduled_for <= datetime.utcnow())
            .all()
        )
        for item in due_items:
            _post_single_item(db, item)


def _post_single_item(db, item: PinQueueItem):
    account = db.query(PinterestAccount).get(item.account_id)
    if not account or not account.is_active:
        item.status = PinStatus.FAILED
        item.error_message = "Pinterest account inactive or not found."
        _log_history(db, item, PinStatus.FAILED, item.error_message)
        return

    # Safety check 1: daily cap
    posted_today = pins_posted_today(db, account.id)
    if posted_today >= Config.MAX_PINS_PER_ACCOUNT_PER_DAY:
        item.status = PinStatus.SKIPPED_RATE_LIMIT
        _log_history(db, item, PinStatus.SKIPPED_RATE_LIMIT, f"Daily cap of {Config.MAX_PINS_PER_ACCOUNT_PER_DAY} reached.")
        logger.info("Account %s hit daily cap, item %s deferred.", account.id, item.id)
        return

    # Safety check 2: duplicate content
    if is_duplicate_content(db, account.id, item.content_hash):
        item.status = PinStatus.SKIPPED_DUPLICATE
        _log_history(db, item, PinStatus.SKIPPED_DUPLICATE, "Identical content already posted to this account.")
        return

    # Refresh token if needed
    if token_is_expired(account.token_expires_at):
        try:
            tok = PinterestAPI.refresh_access_token(account.refresh_token)
            account.access_token = tok["access_token"]
            account.token_expires_at = datetime.utcnow() + timedelta(seconds=tok.get("expires_in", 3600))
        except PinterestAPIError as e:
            item.status = PinStatus.FAILED
            item.error_message = f"Token refresh failed: {e}"
            _log_history(db, item, PinStatus.FAILED, item.error_message)
            return

    # Post it
    try:
        api = PinterestAPI(access_token=account.access_token)
        image_b64 = ImageProcessor.to_base64(item.image_path)
        full_description = item.description + (f" {item.hashtags}" if item.hashtags else "")
        result = api.create_pin(
            board_id=item.board_id,
            image_base64=image_b64,
            title=item.title,
            description=full_description,
            alt_text=item.alt_text,
            link=item.destination_link,
        )
        item.status = PinStatus.POSTED
        item.posted_at = datetime.utcnow()
        _log_history(db, item, PinStatus.POSTED, "Posted successfully.", pinterest_pin_id=result.get("id"))
        logger.info("Posted pin %s for account %s.", item.id, account.id)
    except PinterestAPIError as e:
        item.status = PinStatus.FAILED
        item.error_message = str(e)
        _log_history(db, item, PinStatus.FAILED, str(e))
        logger.error("Failed to post pin %s: %s", item.id, e)


def _log_history(db, item: PinQueueItem, status: PinStatus, detail: str, pinterest_pin_id: str = None):
    db.add(
        PostHistory(
            account_id=item.account_id,
            queue_item_id=item.id,
            pinterest_pin_id=pinterest_pin_id,
            title=item.title,
            board_id=item.board_id,
            status=status,
            detail=detail,
        )
    )


def get_queue_for_account(db, account_id: int):
    return (
        db.query(PinQueueItem)
        .filter(PinQueueItem.account_id == account_id)
        .order_by(PinQueueItem.scheduled_for.asc())
        .all()
    )


def get_history_for_account(db, account_id: int, limit: int = 100):
    return (
        db.query(PostHistory)
        .filter(PostHistory.account_id == account_id)
        .order_by(PostHistory.occurred_at.desc())
        .limit(limit)
        .all()
    )
