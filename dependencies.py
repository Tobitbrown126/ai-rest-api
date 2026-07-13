"""
dependencies.py
----------------
Reusable FastAPI dependencies (dependency injection providers).

These are imported by routers via `Depends(...)` to obtain database
sessions, enforce authentication, and access shared services without
routers needing to know how those objects are constructed.
"""

from typing import Optional

from fastapi import Depends, Security
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from auth import AuthError, decode_access_token, verify_api_key
from database import get_db
from services.ai_service import AIService

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_client(
    api_key: Optional[str] = Security(_api_key_header),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(_bearer_scheme),
) -> str:
    """
    Enforce authentication on protected routes.

    Accepts EITHER:
      - a valid `X-API-Key` header, or
      - a valid `Authorization: Bearer <jwt>` header

    Returns an identifier string for the authenticated client, used for
    logging/auditing purposes.
    """
    # Try API key first
    if api_key and verify_api_key(api_key):
        return "api-key-client"

    # Fall back to bearer JWT
    if credentials and credentials.scheme.lower() == "bearer":
        payload = decode_access_token(credentials.credentials)
        subject = payload.get("sub")
        if subject:
            return f"jwt:{subject}"

    raise AuthError("Missing or invalid credentials. Provide X-API-Key or Bearer token.")


def get_db_session() -> Session:
    """Thin re-export of the database session dependency for router use."""
    yield from get_db()


_ai_service_singleton: Optional[AIService] = None


def get_ai_service() -> AIService:
    """
    Provide a shared AIService instance.

    A singleton is used because the underlying OpenAI client is
    thread-safe and stateless per-request; recreating it on every
    request would be wasteful.
    """
    global _ai_service_singleton
    if _ai_service_singleton is None:
        _ai_service_singleton = AIService()
    return _ai_service_singleton
