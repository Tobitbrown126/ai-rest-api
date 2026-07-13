"""
services/code_service.py
---------------------------
Business logic for the /code/* endpoints: explain, review, and refactor.
"""

from schemas import (
    CodeExplainRequest,
    CodeExplainResponse,
    CodeIssue,
    CodeRefactorRequest,
    CodeRefactorResponse,
    CodeReviewRequest,
    CodeReviewResponse,
)
from services.ai_service import AIService

REVIEW_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "issues": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "severity": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
                    "description": {"type": "string"},
                    "suggestion": {"type": "string"},
                },
                "required": ["severity", "description", "suggestion"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["summary", "issues"],
    "additionalProperties": False,
}

REFACTOR_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "refactored_code": {"type": "string"},
        "explanation_of_changes": {"type": "string"},
    },
    "required": ["refactored_code", "explanation_of_changes"],
    "additionalProperties": False,
}


class CodeService:
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service

    async def explain(self, request: CodeExplainRequest) -> CodeExplainResponse:
        system_prompt = (
            "You are a senior software engineer who writes exceptionally clear "
            "code explanations for other developers. Explain what the code does, "
            "how it works, and call out any notable patterns or caveats."
        )
        prompt = f"Language: {request.language.value}\n\nExplain this code:\n\n{request.code}"

        result = await self.ai_service.generate_text(
            prompt=prompt, system_prompt=system_prompt, temperature=0.3, max_output_tokens=1500
        )

        return CodeExplainResponse(
            explanation=result["text"].strip(),
            language=request.language.value,
            model=result["model"],
        )

    async def review(self, request: CodeReviewRequest) -> CodeReviewResponse:
        system_prompt = (
            "You are a principal engineer performing a rigorous code review. "
            "Identify concrete issues (bugs, security vulnerabilities, performance "
            "problems, readability concerns) with actionable suggestions. Be "
            "specific and avoid vague generalities."
        )
        focus = (
            f"Focus especially on: {', '.join(request.focus_areas)}."
            if request.focus_areas
            else ""
        )
        prompt = (
            f"Language: {request.language.value}\n{focus}\n\n"
            f"Review this code and return a JSON object with 'summary' and 'issues':\n\n"
            f"{request.code}"
        )

        result = await self.ai_service.generate_structured(
            prompt=prompt,
            json_schema=REVIEW_JSON_SCHEMA,
            schema_name="code_review",
            system_prompt=system_prompt,
            temperature=0.2,
        )

        issues = [CodeIssue(**issue) for issue in result.get("issues", [])]
        return CodeReviewResponse(
            summary=result["summary"],
            issues=issues,
            language=request.language.value,
            model="openai-responses-api",
        )

    async def refactor(self, request: CodeRefactorRequest) -> CodeRefactorResponse:
        system_prompt = (
            "You are a senior software engineer specializing in clean code and "
            "refactoring. Improve the given code while preserving its exact "
            "external behavior. Explain the rationale for each meaningful change."
        )
        goals = (
            f"Refactoring goals: {', '.join(request.goals)}."
            if request.goals
            else "General goals: improve readability, maintainability, and idiomatic style."
        )
        prompt = (
            f"Language: {request.language.value}\n{goals}\n\n"
            f"Refactor this code and return a JSON object with 'refactored_code' "
            f"and 'explanation_of_changes':\n\n{request.code}"
        )

        result = await self.ai_service.generate_structured(
            prompt=prompt,
            json_schema=REFACTOR_JSON_SCHEMA,
            schema_name="code_refactor",
            system_prompt=system_prompt,
            temperature=0.3,
        )

        return CodeRefactorResponse(
            refactored_code=result["refactored_code"],
            explanation_of_changes=result["explanation_of_changes"],
            language=request.language.value,
            model="openai-responses-api",
        )
