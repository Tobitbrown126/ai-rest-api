"""
services/email_service.py
----------------------------
Business logic for the /email endpoint. Uses structured output to
reliably separate the generated subject line from the body.
"""

from schemas import EmailRequest, EmailResponse
from services.ai_service import AIService

SYSTEM_PROMPT = (
    "You are an expert professional email writer. Given key points and a "
    "desired tone, draft a clear, well-structured email. Always return a "
    "concise, compelling subject line separate from the body."
)

EMAIL_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "subject": {"type": "string"},
        "body": {"type": "string"},
    },
    "required": ["subject", "body"],
    "additionalProperties": False,
}


class EmailService:
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service

    async def generate_email(self, request: EmailRequest) -> EmailResponse:
        points = "\n".join(f"- {point}" for point in request.key_points)
        recipient = request.recipient_name or "the recipient"
        sender = request.sender_name or "the sender"

        prompt = (
            f"Draft an email with the following details:\n"
            f"Subject hint: {request.subject_hint}\n"
            f"Tone: {request.tone.value}\n"
            f"Recipient: {recipient}\n"
            f"Sender: {sender}\n"
            f"Key points to include:\n{points}\n\n"
            f"Return a JSON object with 'subject' and 'body' fields. "
            f"Sign the email as {sender}."
        )

        result = await self.ai_service.generate_structured(
            prompt=prompt,
            json_schema=EMAIL_JSON_SCHEMA,
            schema_name="email_draft",
            system_prompt=SYSTEM_PROMPT,
            temperature=0.6,
        )

        return EmailResponse(
            subject=result["subject"],
            body=result["body"],
            tone=request.tone.value,
            model="openai-responses-api",
        )
