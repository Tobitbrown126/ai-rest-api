"""
tests/conftest.py
-------------------
Shared pytest fixtures.

Uses an isolated in-memory SQLite database per test session and mocks
the AIService so the test suite never makes real network calls to
OpenAI, keeping tests fast, deterministic, and free.
"""

from typing import Any, AsyncGenerator, Dict, List, Optional
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import settings
from database import Base, get_db
from dependencies import get_ai_service
from main import app

settings.API_KEY = "test-api-key"
settings.JWT_SECRET_KEY = "test-secret"

TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


class FakeAIService:
    """A stand-in for AIService that returns canned, deterministic output."""

    default_model = "gpt-4.1-mini-test"

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_output_tokens: int = 1024,
        model: Optional[str] = None,
        previous_response_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        return {
            "text": f"[fake-response to]: {prompt[:50]}",
            "model": self.default_model,
            "response_id": "resp_fake_123",
            "usage": {"input_tokens": 10, "output_tokens": 10, "total_tokens": 20},
        }

    async def generate_structured(
        self,
        prompt: str,
        json_schema: Dict[str, Any],
        schema_name: str = "structured_response",
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        # Return plausible fake data based on the schema's expected keys
        props = json_schema.get("properties", {})
        fake: Dict[str, Any] = {}
        for key, spec in props.items():
            fake[key] = self._fake_value_for(spec)
        return fake

    def _fake_value_for(self, spec: Dict[str, Any]) -> Any:
        spec_type = spec.get("type")
        if spec_type == "string":
            return "fake string value"
        if spec_type == "integer":
            return 7
        if spec_type == "array":
            item_spec = spec.get("items", {})
            if item_spec.get("type") == "object":
                return [
                    {
                        k: self._fake_value_for(v)
                        for k, v in item_spec.get("properties", {}).items()
                    }
                ]
            return ["fake item"]
        if spec_type == "object":
            return {
                k: self._fake_value_for(v) for k, v in spec.get("properties", {}).items()
            }
        return "fake"

    async def stream_text(self, *args, **kwargs) -> AsyncGenerator[str, None]:
        for chunk in ["Hello", " ", "world"]:
            yield chunk

    async def call_with_tools(
        self, prompt: str, tools: List[Dict[str, Any]], **kwargs
    ) -> Dict[str, Any]:
        return {"type": "text", "text": "fake tool response", "response_id": "resp_fake_456"}


def override_get_ai_service():
    return FakeAIService()


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_ai_service] = override_get_ai_service


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture()
def auth_headers() -> Dict[str, str]:
    return {"X-API-Key": settings.API_KEY}
