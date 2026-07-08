"""models.py — SQLAlchemy ORM models for PinForge AI."""

import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text,
    ForeignKey, Enum, UniqueConstraint
)
from sqlalchemy.orm import relationship
from database import Base


class PinStatus(str, enum.Enum):
    QUEUED      = "queued"
    SCHEDULED   = "scheduled"
    POSTED      = "posted"
    FAILED      = "failed"
    DUPLICATE   = "duplicate"
    RATE_LIMIT  = "rate_limit"


class AIProvider(str, enum.Enum):
    GEMINI   = "gemini"
    OPENAI   = "openai"
    DEEPSEEK = "deepseek"


class User(Base):
    """Synced with Supabase Auth. supabase_uid is the Supabase user UUID."""
    __tablename__ = "users"
    id            = Column(Integer, primary_key=True)
    supabase_uid  = Column(String(64), unique=True, nullable=False, index=True)
    email         = Column(String(255), unique=True, nullable=False)
    full_name     = Column(String(255), nullable=True)
    ai_provider   = Column(Enum(AIProvider), default=AIProvider.GEMINI)
    gemini_key    = Column(Text, nullable=True)   # user's own key (encrypted ideally)
    openai_key    = Column(Text, nullable=True)
    created_at    = Column(DateTime, default=datetime.utcnow)
    is_active     = Column(Boolean, default=True)

    accounts  = relationship("PinterestAccount", back_populates="user", cascade="all, delete-orphan")


class PinterestAccount(Base):
    """One Pinterest business account per OAuth connection."""
    __tablename__ = "pinterest_accounts"
    id                  = Column(Integer, primary_key=True)
    user_id             = Column(Integer, ForeignKey("users.id"), nullable=False)
    pinterest_user_id   = Column(String(64), nullable=False)
    username            = Column(String(255), nullable=True)
    display_name        = Column(String(255), nullable=True)
    profile_image       = Column(String(500), nullable=True)
    access_token        = Column(Text, nullable=False)
    refresh_token       = Column(Text, nullable=True)
    token_expires_at    = Column(DateTime, nullable=True)
    connected_at        = Column(DateTime, default=datetime.utcnow)
    is_active           = Column(Boolean, default=True)

    user       = relationship("User", back_populates="accounts")
    queue      = relationship("PinQueue", back_populates="account", cascade="all, delete-orphan")
    history    = relationship("PostHistory", back_populates="account", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("user_id", "pinterest_user_id", name="uq_user_pinterest"),)


class Board(Base):
    """Cached Pinterest board list per account."""
    __tablename__ = "boards"
    id                  = Column(Integer, primary_key=True)
    account_id          = Column(Integer, ForeignKey("pinterest_accounts.id"), nullable=False)
    pinterest_board_id  = Column(String(64), nullable=False)
    name                = Column(String(255), nullable=False)
    pin_count           = Column(Integer, default=0)
    cached_at           = Column(DateTime, default=datetime.utcnow)


class PinQueue(Base):
    """A pin waiting to be posted. Core unit for the scheduler."""
    __tablename__ = "pin_queue"
    id                = Column(Integer, primary_key=True)
    account_id        = Column(Integer, ForeignKey("pinterest_accounts.id"), nullable=False)
    image_path        = Column(String(512), nullable=False)
    image_filename    = Column(String(255), nullable=True)
    title             = Column(String(100), nullable=False)
    description       = Column(Text, nullable=False)
    alt_text          = Column(String(500), nullable=True)
    hashtags          = Column(String(500), nullable=True)
    destination_link  = Column(String(1000), nullable=True)
    board_id          = Column(String(64), nullable=False)
    board_name        = Column(String(255), nullable=True)
    content_hash      = Column(String(64), nullable=False, index=True)
    status            = Column(Enum(PinStatus), default=PinStatus.SCHEDULED)
    scheduled_for     = Column(DateTime, nullable=True)
    posted_at         = Column(DateTime, nullable=True)
    error_message     = Column(Text, nullable=True)
    created_at        = Column(DateTime, default=datetime.utcnow)

    account = relationship("PinterestAccount", back_populates="queue")


class PostHistory(Base):
    """Immutable audit log of every posting attempt."""
    __tablename__ = "post_history"
    id                = Column(Integer, primary_key=True)
    account_id        = Column(Integer, ForeignKey("pinterest_accounts.id"), nullable=False)
    queue_item_id     = Column(Integer, ForeignKey("pin_queue.id"), nullable=True)
    pinterest_pin_id  = Column(String(64), nullable=True)
    title             = Column(String(100), nullable=True)
    board_name        = Column(String(255), nullable=True)
    status            = Column(Enum(PinStatus), nullable=False)
    detail            = Column(Text, nullable=True)
    occurred_at       = Column(DateTime, default=datetime.utcnow)

    account = relationship("PinterestAccount", back_populates="history")
