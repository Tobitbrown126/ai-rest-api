"""
services/ai_service.py
------------------------
Core wrapper around the OpenAI Responses API.

This is the single place in the codebase that talks to OpenAI directly.
Every other service (chat, translation, summarization, email, code,
prompt engineering) builds on top of the primitives exposed here:

    - generate_text(...)          simple text-in / text-out
    - generate_structured(...)    JSON-schema-constrained structured output
    - stream_text(...)            async generator yielding text deltas
    - call_with_tools(...)        function calling / tool use

All methods are async and use `httpx`-backed async OpenAI client so they
integrate cleanly with FastAPI's async request handlers.
"""

import json
from typing import Any, AsyncGenerator, Dict, List, Optional

from openai import AsyncOpenAI

from config import settings
from logging_config import logger
from middleware.exceptions import AIServiceError


class AIService:
    """Thin, well-typed wrapper around the OpenAI Responses API."""

    def __init__(self) -> None:
        if not settings.OPENAI_API_KEY:
            logger.warning(
                "OPENAI_API_KEY is not set. AI endpoints will fail until it is configured."
            )
        self._client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY or "missing-key",
            timeout=settings.OPENAI_TIMEOUT_SECONDS,
        )
        self.default_model = settings.OPENAI_MODEL

    # ------------------------------------------------------------------
    # Simple text generation
    # ------------------------------------------------------------------
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_output_tokens: int = 1024,
        model: Optional[str] = None,
        previous_response_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a single text response using the Responses API.

        Returns a dict with `text`, `model`, `response_id`, and `usage`.
        `previous_response_id` allows chaining turns for conversation
        context without the caller needing to resend full history.
        """
        try:
            input_items: List[Dict[str, Any]] = []
            if system_prompt:
                input_items.append({"role": "system", "content": system_prompt})
            input_items.append({"role": "user", "content": prompt})

            response = await self._client.responses.create(
                model=model or self.default_model,
                input=input_items,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                previous_response_id=previous_response_id,
            )

            return {
                "text": response.output_text,
                "model": response.model,
                "response_id": response.id,
                "usage": self._serialize_usage(response),
            }
        except Exception as exc:  # noqa: BLE001
            logger.exception("AIService.generate_text failed")
            raise AIServiceError(f"Failed to generate AI response: {exc}") from exc

    # ------------------------------------------------------------------
    # Structured / JSON output
    # ------------------------------------------------------------------
    async def generate_structured(
        self,
        prompt: str,
        json_schema: Dict[str, Any],
        schema_name: str = "structured_response",
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a response constrained to the given JSON schema, using the
        Responses API's structured output ("json_schema") format. Returns
        the parsed dict.
        """
        try:
            input_items: List[Dict[str, Any]] = []
            if system_prompt:
                input_items.append({"role": "system", "content": system_prompt})
            input_items.append({"role": "user", "content": prompt})

            response = await self._client.responses.create(
                model=model or self.default_model,
                input=input_items,
                temperature=temperature,
                text={
                    "format": {
                        "type": "json_schema",
                        "name": schema_name,
                        "schema": json_schema,
                        "strict": True,
                    }
                },
            )

            raw_text = response.output_text
            parsed = json.loads(raw_text)
            return parsed
        except json.JSONDecodeError as exc:
            logger.exception("Failed to parse structured AI output as JSON")
            raise AIServiceError("AI returned malformed structured output") from exc
        except Exception as exc:  # noqa: BLE001
            logger.exception("AIService.generate_structured failed")
            raise AIServiceError(f"Failed to generate structured AI response: {exc}") from exc

    # ------------------------------------------------------------------
    # Streaming
    # ------------------------------------------------------------------
    async def stream_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_output_tokens: int = 1024,
        model: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Async generator yielding incremental text deltas as they are
        produced by the model, suitable for Server-Sent Events (SSE).
        """
        try:
            input_items: List[Dict[str, Any]] = []
            if system_prompt:
                input_items.append({"role": "system", "content": system_prompt})
            input_items.append({"role": "user", "content": prompt})

            async with self._client.responses.stream(
                model=model or self.default_model,
                input=input_items,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
            ) as stream:
                async for event in stream:
                    if event.type == "response.output_text.delta":
                        yield event.delta
                    elif event.type == "response.error":
                        logger.error("Streaming error event: {}", event)
                        raise AIServiceError("Streaming response failed")
        except Exception as exc:  # noqa: BLE001
            logger.exception("AIService.stream_text failed")
            raise AIServiceError(f"Failed to stream AI response: {exc}") from exc

    # ------------------------------------------------------------------
    # Function calling / tool use
    # ------------------------------------------------------------------
    async def call_with_tools(
        self,
        prompt: str,
        tools: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.3,
    ) -> Dict[str, Any]:
        """
        Send a prompt along with a set of callable tool definitions.

        Returns a dict containing either:
          - {"type": "tool_calls", "tool_calls": [...]} if the model
            decided to call one or more tools, or
          - {"type": "text", "text": "..."} if the model answered directly.
        """
        try:
            input_items: List[Dict[str, Any]] = []
            if system_prompt:
                input_items.append({"role": "system", "content": system_prompt})
            input_items.append({"role": "user", "content": prompt})

            response = await self._client.responses.create(
                model=model or self.default_model,
                input=input_items,
                tools=tools,
                temperature=temperature,
            )

            tool_calls = [
                {
                    "id": item.id,
                    "name": item.name,
                    "arguments": json.loads(item.arguments) if item.arguments else {},
                }
                for item in response.output
                if getattr(item, "type", None) == "function_call"
            ]

            if tool_calls:
                return {"type": "tool_calls", "tool_calls": tool_calls, "response_id": response.id}

            return {
                "type": "text",
                "text": response.output_text,
                "response_id": response.id,
            }
        except Exception as exc:  # noqa: BLE001
            logger.exception("AIService.call_with_tools failed")
            raise AIServiceError(f"Failed to process tool-calling request: {exc}") from exc

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _serialize_usage(response: Any) -> Optional[Dict[str, Any]]:
        usage = getattr(response, "usage", None)
        if usage is None:
            return None
        try:
            return usage.model_dump()
        except AttributeError:
            return dict(usage)
