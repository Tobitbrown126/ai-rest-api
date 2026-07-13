"""
services/translation_service.py
----------------------------------
Business logic for the /translate endpoint.
"""

from schemas import TranslateRequest, TranslateResponse
from services.ai_service import AIService

SYSTEM_PROMPT = (
    "You are a professional translator. Translate the user's text accurately, "
    "preserving tone, meaning, and formatting. Respond with ONLY the translated "
    "text and nothing else - no explanations, no quotes, no preamble."
)


class TranslationService:
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service

    async def translate(self, request: TranslateRequest) -> TranslateResponse:
        prompt = (
            f"Source language: {request.source_language}\n"
            f"Target language: {request.target_language}\n"
            f"Text to translate:\n{request.text}"
        )

        result = await self.ai_service.generate_text(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            temperature=0.3,
            max_output_tokens=2048,
        )

        return TranslateResponse(
            original_text=request.text,
            translated_text=result["text"].strip(),
            source_language=request.source_language or "auto",
            target_language=request.target_language,
            model=result["model"],
        )
