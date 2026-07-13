"""
models.py
---------
SQLAlchemy ORM models representing the persistence layer.

Tables:
    - conversations: logical grouping of chat turns (a "session")
    - messages: individual chat messages linked to a conversation
    - api_usage_logs: one row per API request, used for auditing,
      analytics, and rate-limit diagnostics
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class Conversation(Base):
    """Represents a single conversation thread (a sequence of chat turns)."""

    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    title: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    messages: Mapped[list["Message"]] = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )


class Message(Base):
    """A single message (user or assistant) within a conversation."""

    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    conversation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("conversations.id"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # user | assistant | system
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")


class ApiUsageLog(Base):
    """Records metadata about every API request for auditing/analytics."""

    __tablename__ = "api_usage_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    endpoint: Mapped[str] = mapped_column(String(255), nullable=False)
    method: Mapped[str] = mapped_column(String(10), nullable=False)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    execution_time_ms: Mapped[float] = mapped_column(Float, nullable=False)
    client_host: Mapped[str] = mapped_column(String(64), nullable=True)
    request_id: Mapped[str] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
