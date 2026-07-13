"""
routers/email.py
------------------
POST /email - generate a professional email draft from key points.
"""

from fastapi import APIRouter, Depends

from dependencies import get_ai_service, get_current_client
from schemas import EmailRequest, EmailResponse
from services.ai_service import AIService
from services.email_service import EmailService

router = APIRouter(prefix="/email", tags=["Email"])


@router.post(
    "",
    response_model=EmailResponse,
    summary="Generate an email draft",
    responses={401: {"description": "Missing or invalid credentials"}},
)
async def generate_email(
    request: EmailRequest,
    ai_service: AIService = Depends(get_ai_service),
    client: str = Depends(get_current_client),
):
    service = EmailService(ai_service)
    return await service.generate_email(request)
