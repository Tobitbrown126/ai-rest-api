"""
routers/summarize.py
----------------------
POST /summarize - summarize a block of text.
"""

from fastapi import APIRouter, Depends

from dependencies import get_ai_service, get_current_client
from schemas import SummarizeRequest, SummarizeResponse
from services.ai_service import AIService
from services.summary_service import SummaryService

router = APIRouter(prefix="/summarize", tags=["Summarization"])


@router.post(
    "",
    response_model=SummarizeResponse,
    summary="Summarize text",
    responses={401: {"description": "Missing or invalid credentials"}},
)
async def summarize(
    request: SummarizeRequest,
    ai_service: AIService = Depends(get_ai_service),
    client: str = Depends(get_current_client),
):
    service = SummaryService(ai_service)
    return await service.summarize(request)
