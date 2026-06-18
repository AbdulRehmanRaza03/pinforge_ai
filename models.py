"""
models.py
SQLAlchemy ORM models for PinForge AI.
"""

import enum
from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum, UniqueConstraint
)
from sqlalchemy.orm import relationship

from database import Base


class PinStatus(str, enum.Enum):
    QUEUED = "queued"
    SCHEDULED = "scheduled"
    POSTED = "posted"
    FAILED = "failed"
    SKIPPED_DUPLICATE = "skipped_duplicate"
    SKIPPED_RATE_LIMIT = "skipped_rate_limit"


class User(Base):
    """App-level user account (local auth). Owns one or more Pinterest accounts."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    pinterest_accounts = relationship(
        "PinterestAccount", back_populates="user", cascade="all, delete-orphan"
    )


class PinterestAccount(Base):
    """One connected Pinterest business account (OAuth2 tokens) per user."""
    __tablename__ = "pinterest_accounts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    pinterest_user_id = Column(String(64), nullable=False)
    username = Column(String(255), nullable=True)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime, nullable=True)

    connected_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="pinterest_accounts")
    queue_items = relationship(
        "PinQueueItem", back_populates="account", cascade="all, delete-orphan"
    )
    history = relationship(
        "PostHistory", back_populates="account", cascade="all, delete-orphan"
    )

    __table_args__ = (UniqueConstraint("user_id", "pinterest_user_id", name="uq_user_pinterest_account"),)


class Board(Base):
    """Cached Pinterest board metadata (avoids refetching every render)."""
    __tablename__ = "boards"

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("pinterest_accounts.id"), nullable=False)
    pinterest_board_id = Column(String(64), nullable=False)
    name = Column(String(255), nullable=False)
    cached_at = Column(DateTime, default=datetime.utcnow)


class PinQueueItem(Base):
    """A pin waiting to be (or already) posted. Core unit the scheduler operates on."""
    __tablename__ = "pin_queue"

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("pinterest_accounts.id"), nullable=False)

    image_path = Column(String(512), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    alt_text = Column(String(500), nullable=True)
    hashtags = Column(String(500), nullable=True)
    destination_link = Column(String(1000), nullable=True)

    board_id = Column(String(64), nullable=False)  # pinterest board id
    content_hash = Column(String(64), nullable=False, index=True)  # dup detection

    status = Column(Enum(PinStatus), default=PinStatus.QUEUED, nullable=False)
    scheduled_for = Column(DateTime, nullable=True)
    posted_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    account = relationship("PinterestAccount", back_populates="queue_items")


class PostHistory(Base):
    """Immutable log of every post attempt, for analytics + audit trail."""
    __tablename__ = "post_history"

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("pinterest_accounts.id"), nullable=False)
    queue_item_id = Column(Integer, ForeignKey("pin_queue.id"), nullable=True)

    pinterest_pin_id = Column(String(64), nullable=True)
    title = Column(String(100), nullable=True)
    board_id = Column(String(64), nullable=True)
    status = Column(Enum(PinStatus), nullable=False)
    detail = Column(Text, nullable=True)
    occurred_at = Column(DateTime, default=datetime.utcnow)

    account = relationship("PinterestAccount", back_populates="history")
