"""
services/chat_service.py
--------------------------
Business logic for the /chat endpoint: manages conversation persistence
and delegates text generation to AIService, using prior turns as
conversation context.
"""

from datetime import datetime
from typing import AsyncGenerator

from sqlalchemy.orm import Session

from schemas import ChatRequest, ChatResponse
from services.ai_service import AIService
from services.database_service import DatabaseService

DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful, concise, and accurate AI assistant embedded in a "
    "production REST API. Answer clearly and avoid unnecessary verbosity."
)


class ChatService:
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service

    def _build_context_prompt(self, db: Session, conversation_id: str, latest_message: str) -> str:
        """Concatenate prior conversation turns with the latest message to
        give the model conversational context (used when not relying on
        provider-side `previous_response_id` chaining)."""
        history = DatabaseService.get_conversation_history(db, conversation_id)
        if not history:
            return latest_message

        lines = []
        for msg in history:
            lines.append(f"{msg.role.upper()}: {msg.content}")
        lines.append(f"USER: {latest_message}")
        return "\n".join(lines)

    async def chat(self, db: Session, request: ChatRequest) -> ChatResponse:
        conversation = DatabaseService.get_or_create_conversation(
            db, conversation_id=request.conversation_id
        )

        context_prompt = self._build_context_prompt(db, conversation.id, request.message)

        result = await self.ai_service.generate_text(
            prompt=context_prompt,
            system_prompt=request.system_prompt or DEFAULT_SYSTEM_PROMPT,
            temperature=request.temperature,
            max_output_tokens=request.max_output_tokens,
        )

        DatabaseService.add_message(db, conversation.id, "user", request.message)
        DatabaseService.add_message(db, conversation.id, "assistant", result["text"])

        return ChatResponse(
            conversation_id=conversation.id,
            reply=result["text"],
            model=result["model"],
            usage=result.get("usage"),
            created_at=datetime.utcnow(),
        )

    async def chat_stream(
        self, db: Session, request: ChatRequest
    ) -> AsyncGenerator[str, None]:
        """Yields text chunks for SSE streaming; persists the full reply once complete."""
        conversation = DatabaseService.get_or_create_conversation(
            db, conversation_id=request.conversation_id
        )
        context_prompt = self._build_context_prompt(db, conversation.id, request.message)

        full_reply_parts = []
        async for delta in self.ai_service.stream_text(
            prompt=context_prompt,
            system_prompt=request.system_prompt or DEFAULT_SYSTEM_PROMPT,
            temperature=request.temperature,
            max_output_tokens=request.max_output_tokens,
        ):
            full_reply_parts.append(delta)
            yield delta

        DatabaseService.add_message(db, conversation.id, "user", request.message)
        DatabaseService.add_message(
            db, conversation.id, "assistant", "".join(full_reply_parts)
        )
