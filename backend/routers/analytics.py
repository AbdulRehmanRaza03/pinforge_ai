"""routers/analytics.py — Dashboard stats and overview."""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db_dep
from middleware.auth import get_current_user
from models import PinQueue, PinStatus, PostHistory, PinterestAccount, User

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/overview")
def overview(
    account_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db_dep),
):
    acct = db.query(PinterestAccount).filter(
        PinterestAccount.id == account_id, PinterestAccount.user_id == user.id
    ).first()
    if not acct:
        raise HTTPException(404, "Account not found.")

    now = datetime.utcnow()
    day_ago = now - timedelta(hours=24)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    def count_posted(since):
        return db.query(PostHistory).filter(
            PostHistory.account_id == account_id,
            PostHistory.status == PinStatus.POSTED,
            PostHistory.occurred_at >= since,
        ).count()

    def count_failed(since):
        return db.query(PostHistory).filter(
            PostHistory.account_id == account_id,
            PostHistory.status == PinStatus.FAILED,
            PostHistory.occurred_at >= since,
        ).count()

    queued = db.query(PinQueue).filter(
        PinQueue.account_id == account_id,
        PinQueue.status.in_([PinStatus.SCHEDULED, PinStatus.QUEUED]),
    ).count()

    # Daily breakdown last 7 days for chart
    daily = []
    for i in range(7, -1, -1):
        day_start = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0)
        day_end = day_start + timedelta(days=1)
        cnt = db.query(PostHistory).filter(
            PostHistory.account_id == account_id,
            PostHistory.status == PinStatus.POSTED,
            PostHistory.occurred_at >= day_start,
            PostHistory.occurred_at < day_end,
        ).count()
        daily.append({"date": day_start.strftime("%b %d"), "pins": cnt})

    return {
        "posted_today": count_posted(day_ago),
        "posted_week": count_posted(week_ago),
        "posted_month": count_posted(month_ago),
        "failed_week": count_failed(week_ago),
        "queued": queued,
        "daily_chart": daily,
        "from config": {
            "max_per_day": __import__("config").settings.MAX_PINS_PER_ACCOUNT_PER_DAY,
        },
    }
