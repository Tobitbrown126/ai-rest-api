"""
auth.py
-------
Authentication utilities supporting two schemes:

1. API Key authentication  -> header: `X-API-Key: <key>`
2. Bearer Token (JWT) auth -> header: `Authorization: Bearer <token>`

Either scheme is sufficient to access protected routes. JWTs are issued
by the (demo) `/auth/token` flow is intentionally omitted from routers per
spec, but the encode/decode utilities are provided here and exercised in
tests; a minimal helper `create_access_token` is exposed for reuse.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Header, HTTPException, status
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer

from config import settings
from logging_config import logger

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
bearer_scheme = HTTPBearer(auto_error=False)


class AuthError(HTTPException):
    """Raised when authentication fails for any reason."""

    def __init__(self, detail: str = "Invalid or missing credentials"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


def create_access_token(subject: str, expires_minutes: Optional[int] = None) -> str:
    """Create a signed JWT for the given subject (e.g. a client/user ID)."""
    expire_minutes = expires_minutes or settings.JWT_EXPIRATION_MINUTES
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    payload = {"sub": subject, "exp": expire, "iat": datetime.now(timezone.utc)}
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT. Raises AuthError on failure."""
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthError("Token has expired")
    except jwt.InvalidTokenError:
        raise AuthError("Invalid token")


def verify_api_key(provided_key: Optional[str]) -> bool:
    """Validate a provided API key against the configured secret."""
    if not settings.API_KEY:
        # If no API key is configured, API key auth is effectively disabled.
        return False
    return provided_key is not None and provided_key == settings.API_KEY


async def require_auth(
    api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
    authorization: Optional[HTTPAuthorizationCredentials] = None,
) -> str:
    """
    Deprecated in favor of `dependencies.get_current_client`, kept for
    backward compatibility / direct import convenience.
    """
    raise NotImplementedError("Use dependencies.get_current_client instead")
