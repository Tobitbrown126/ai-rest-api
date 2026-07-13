"""
routers/prompt.py
-------------------
POST /prompt/improve   - rewrite a prompt to be clearer and more effective
POST /prompt/optimize  - optimize a prompt for a specific objective
POST /prompt/evaluate  - score a prompt's quality with structured feedback
"""

from fastapi import APIRouter, Depends

from dependencies import get_ai_service, get_current_client
from schemas import (
    PromptEvaluateRequest,
    PromptEvaluateResponse,
    PromptImproveRequest,
    PromptImproveResponse,
    PromptOptimizeRequest,
    PromptOptimizeResponse,
)
from services.ai_service import AIService
from services.prompt_service import PromptService

router = APIRouter(prefix="/prompt", tags=["Prompt Engineering"])


@router.post(
    "/improve",
    response_model=PromptImproveResponse,
    summary="Improve a prompt",
    responses={401: {"description": "Missing or invalid credentials"}},
)
async def improve_prompt(
    request: PromptImproveRequest,
    ai_service: AIService = Depends(get_ai_service),
    client: str = Depends(get_current_client),
):
    service = PromptService(ai_service)
    return await service.improve(request)


@router.post(
    "/optimize",
    response_model=PromptOptimizeResponse,
    summary="Optimize a prompt for a specific objective",
    responses={401: {"description": "Missing or invalid credentials"}},
)
async def optimize_prompt(
    request: PromptOptimizeRequest,
    ai_service: AIService = Depends(get_ai_service),
    client: str = Depends(get_current_client),
):
    service = PromptService(ai_service)
    return await service.optimize(request)


@router.post(
    "/evaluate",
    response_model=PromptEvaluateResponse,
    summary="Evaluate prompt quality",
    responses={401: {"description": "Missing or invalid credentials"}},
)
async def evaluate_prompt(
    request: PromptEvaluateRequest,
    ai_service: AIService = Depends(get_ai_service),
    client: str = Depends(get_current_client),
):
    service = PromptService(ai_service)
    return await service.evaluate(request)
