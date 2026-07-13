"""
services/database_service.py
------------------------------
Data access helpers for conversation history, isolating routers/services
from raw SQLAlchemy queries.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from middleware.exceptions import ResourceNotFoundError
from models import Conversation, Message


class DatabaseService:
    """Encapsulates CRUD operations for conversations and messages."""

    @staticmethod
    def get_or_create_conversation(
        db: Session, conversation_id: Optional[str] = None, title: Optional[str] = None
    ) -> Conversation:
        if conversation_id:
            conversation = (
                db.query(Conversation).filter(Conversation.id == conversation_id).first()
            )
            if not conversation:
                raise ResourceNotFoundError(f"Conversation '{conversation_id}' not found")
            return conversation

        conversation = Conversation(title=title)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation

    @staticmethod
    def add_message(db: Session, conversation_id: str, role: str, content: str) -> Message:
        message = Message(conversation_id=conversation_id, role=role, content=content)
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    @staticmethod
    def get_conversation_history(db: Session, conversation_id: str) -> List[Message]:
        return (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .all()
        )
