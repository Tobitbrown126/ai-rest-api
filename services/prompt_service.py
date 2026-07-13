"""
services/prompt_service.py
-----------------------------
Business logic for the /prompt/improve, /prompt/optimize, and
/prompt/evaluate endpoints. Demonstrates using the AI itself as a
prompt-engineering assistant, with structured output for evaluation
scoring.
"""

from schemas import (
    PromptEvaluateRequest,
    PromptEvaluateResponse,
    PromptEvaluationScore,
    PromptImproveRequest,
    PromptImproveResponse,
    PromptOptimizeRequest,
    PromptOptimizeResponse,
)
from services.ai_service import AIService

IMPROVE_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "improved_prompt": {"type": "string"},
        "rationale": {"type": "string"},
    },
    "required": ["improved_prompt", "rationale"],
    "additionalProperties": False,
}

OPTIMIZE_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "optimized_prompt": {"type": "string"},
        "changes_made": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["optimized_prompt", "changes_made"],
    "additionalProperties": False,
}

EVALUATE_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "scores": {
            "type": "object",
            "properties": {
                "clarity": {"type": "integer", "minimum": 1, "maximum": 10},
                "specificity": {"type": "integer", "minimum": 1, "maximum": 10},
                "structure": {"type": "integer", "minimum": 1, "maximum": 10},
                "overall": {"type": "integer", "minimum": 1, "maximum": 10},
            },
            "required": ["clarity", "specificity", "structure", "overall"],
            "additionalProperties": False,
        },
        "strengths": {"type": "array", "items": {"type": "string"}},
        "weaknesses": {"type": "array", "items": {"type": "string"}},
        "suggestions": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["scores", "strengths", "weaknesses", "suggestions"],
    "additionalProperties": False,
}


class PromptService:
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service

    async def improve(self, request: PromptImproveRequest) -> PromptImproveResponse:
        system_prompt = (
            "You are a world-class prompt engineer. Rewrite prompts to be "
            "clearer, more specific, and more likely to produce the desired "
            "output from a large language model."
        )
        goal_line = f"Desired goal: {request.goal}\n" if request.goal else ""
        prompt = (
            f"{goal_line}Improve this prompt and return a JSON object with "
            f"'improved_prompt' and 'rationale':\n\n{request.prompt}"
        )

        result = await self.ai_service.generate_structured(
            prompt=prompt,
            json_schema=IMPROVE_JSON_SCHEMA,
            schema_name="prompt_improvement",
            system_prompt=system_prompt,
            temperature=0.5,
        )

        return PromptImproveResponse(
            original_prompt=request.prompt,
            improved_prompt=result["improved_prompt"],
            rationale=result["rationale"],
            model="openai-responses-api",
        )

    async def optimize(self, request: PromptOptimizeRequest) -> PromptOptimizeResponse:
        system_prompt = (
            "You are a prompt optimization specialist. Optimize prompts for "
            "the specified objective (e.g. clarity, brevity, structured output) "
            "while preserving the original intent."
        )
        target = f"Target model: {request.target_model}\n" if request.target_model else ""
        prompt = (
            f"{target}Optimize for: {request.optimize_for}\n"
            f"Return a JSON object with 'optimized_prompt' and 'changes_made' "
            f"(a list of short bullet strings describing each change):\n\n{request.prompt}"
        )

        result = await self.ai_service.generate_structured(
            prompt=prompt,
            json_schema=OPTIMIZE_JSON_SCHEMA,
            schema_name="prompt_optimization",
            system_prompt=system_prompt,
            temperature=0.5,
        )

        return PromptOptimizeResponse(
            original_prompt=request.prompt,
            optimized_prompt=result["optimized_prompt"],
            changes_made=result["changes_made"],
            model="openai-responses-api",
        )

    async def evaluate(self, request: PromptEvaluateRequest) -> PromptEvaluateResponse:
        system_prompt = (
            "You are a rigorous prompt quality evaluator. Score prompts "
            "objectively on clarity, specificity, and structure (1-10 each), "
            "then provide an overall score, strengths, weaknesses, and "
            "actionable suggestions for improvement."
        )
        prompt = (
            "Evaluate this prompt and return a JSON object matching the "
            f"required schema:\n\n{request.prompt}"
        )

        result = await self.ai_service.generate_structured(
            prompt=prompt,
            json_schema=EVALUATE_JSON_SCHEMA,
            schema_name="prompt_evaluation",
            system_prompt=system_prompt,
            temperature=0.2,
        )

        return PromptEvaluateResponse(
            scores=PromptEvaluationScore(**result["scores"]),
            strengths=result["strengths"],
            weaknesses=result["weaknesses"],
            suggestions=result["suggestions"],
            model="openai-responses-api",
        )
