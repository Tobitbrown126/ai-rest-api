"""
routers/chat.py
-----------------
POST /chat - conversational AI endpoint with conversation persistence
and optional Server-Sent Events (SSE) streaming.
"""

import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_ai_service, get_current_client
from schemas import ChatRequest, ChatResponse
from services.ai_service import AIService
from services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post(
    "",
    response_model=ChatResponse,
    summary="Chat with the AI assistant",
    responses={401: {"description": "Missing or invalid credentials"}},
)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    ai_service: AIService = Depends(get_ai_service),
    client: str = Depends(get_current_client),
):
    """
    Send a message to the AI assistant.

    - Set `stream=true` to receive a Server-Sent Events stream of text deltas.
    - Provide `conversation_id` to continue an existing conversation with
      full context; omit it to start a new conversation.
    """
    service = ChatService(ai_service)

    if request.stream:
        async def event_generator():
            async for delta in service.chat_stream(db, request):
                yield f"data: {json.dumps({'delta': delta})}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    return await service.chat(db, request)
