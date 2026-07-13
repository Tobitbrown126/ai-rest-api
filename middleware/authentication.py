"""
middleware/authentication.py
------------------------------
Note: Primary authentication enforcement happens per-route via the
`get_current_client` FastAPI dependency (see dependencies.py), which is
the idiomatic FastAPI approach and integrates cleanly with OpenAPI docs
(showing the lock icon + auth schemes in Swagger UI).

This module provides a lightweight ASGI middleware that attaches a
`request.state.authenticated` flag based on presence of credentials,
purely for logging/observability purposes. It does NOT block requests -
actual enforcement remains in the dependency layer so that public routes
(/, /health, /version) stay accessible.
"""

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class AuthContextMiddleware(BaseHTTPMiddleware):
    """Annotates each request with whether auth credentials were presented."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        has_api_key = "x-api-key" in request.headers
        has_bearer = request.headers.get("authorization", "").lower().startswith("bearer ")
        request.state.authenticated = has_api_key or has_bearer
        request.state.auth_method = (
            "api_key" if has_api_key else "bearer" if has_bearer else "none"
        )
        return await call_next(request)
