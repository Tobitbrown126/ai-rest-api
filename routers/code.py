"""
routers/code.py
-----------------
POST /code/explain   - explain a snippet of code in plain English
POST /code/review    - structured code review with issues/severity
POST /code/refactor  - refactor code toward stated goals
"""

from fastapi import APIRouter, Depends

from dependencies import get_ai_service, get_current_client
from schemas import (
    CodeExplainRequest,
    CodeExplainResponse,
    CodeRefactorRequest,
    CodeRefactorResponse,
    CodeReviewRequest,
    CodeReviewResponse,
)
from services.ai_service import AIService
from services.code_service import CodeService

router = APIRouter(prefix="/code", tags=["Code Assistance"])


@router.post(
    "/explain",
    response_model=CodeExplainResponse,
    summary="Explain a code snippet",
    responses={401: {"description": "Missing or invalid credentials"}},
)
async def explain_code(
    request: CodeExplainRequest,
    ai_service: AIService = Depends(get_ai_service),
    client: str = Depends(get_current_client),
):
    service = CodeService(ai_service)
    return await service.explain(request)


@router.post(
    "/review",
    response_model=CodeReviewResponse,
    summary="Review a code snippet",
    responses={401: {"description": "Missing or invalid credentials"}},
)
async def review_code(
    request: CodeReviewRequest,
    ai_service: AIService = Depends(get_ai_service),
    client: str = Depends(get_current_client),
):
    service = CodeService(ai_service)
    return await service.review(request)


@router.post(
    "/refactor",
    response_model=CodeRefactorResponse,
    summary="Refactor a code snippet",
    responses={401: {"description": "Missing or invalid credentials"}},
)
async def refactor_code(
    request: CodeRefactorRequest,
    ai_service: AIService = Depends(get_ai_service),
    client: str = Depends(get_current_client),
):
    service = CodeService(ai_service)
    return await service.refactor(request)
