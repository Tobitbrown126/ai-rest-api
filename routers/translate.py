"""
routers/translate.py
----------------------
POST /translate - translate text between languages.
"""

from fastapi import APIRouter, Depends

from dependencies import get_ai_service, get_current_client
from schemas import TranslateRequest, TranslateResponse
from services.ai_service import AIService
from services.translation_service import TranslationService

router = APIRouter(prefix="/translate", tags=["Translation"])


@router.post(
    "",
    response_model=TranslateResponse,
    summary="Translate text",
    responses={401: {"description": "Missing or invalid credentials"}},
)
async def translate(
    request: TranslateRequest,
    ai_service: AIService = Depends(get_ai_service),
    client: str = Depends(get_current_client),
):
    service = TranslationService(ai_service)
    return await service.translate(request)
