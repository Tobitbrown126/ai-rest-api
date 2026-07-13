"""
services/summary_service.py
------------------------------
Business logic for the /summarize endpoint.
"""

from schemas import SummarizeRequest, SummarizeResponse, SummaryLength
from services.ai_service import AIService

_LENGTH_GUIDANCE = {
    SummaryLength.short: "in 1-2 concise sentences",
    SummaryLength.medium: "in a short paragraph (3-5 sentences)",
    SummaryLength.long: "in a detailed multi-paragraph summary covering all key points",
}


class SummaryService:
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service

    async def summarize(self, request: SummarizeRequest) -> SummarizeResponse:
        length_instruction = _LENGTH_GUIDANCE[request.length]
        format_instruction = (
            "Format the summary as bullet points." if request.bullet_points else ""
        )

        system_prompt = (
            "You are an expert summarizer. Produce accurate, faithful summaries "
            "that preserve the key facts and intent of the source text without "
            "adding information that isn't present."
        )

        prompt = (
            f"Summarize the following text {length_instruction}. {format_instruction}\n\n"
            f"TEXT:\n{request.text}"
        )

        result = await self.ai_service.generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.4,
            max_output_tokens=1500,
        )

        summary_text = result["text"].strip()
        return SummarizeResponse(
            summary=summary_text,
            original_length_chars=len(request.text),
            summary_length_chars=len(summary_text),
            model=result["model"],
        )
