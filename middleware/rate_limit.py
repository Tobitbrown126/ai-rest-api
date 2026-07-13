"""
middleware/rate_limit.py
--------------------------
A simple, dependency-free rate limiting middleware using a fixed-window
counter per client IP, stored in-process.

For multi-instance production deployments, replace the in-memory store
with Redis (the interface is intentionally small to make that swap easy).
"""

import time
from collections import defaultdict, deque
from typing import Deque, Dict

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from config import settings
from logging_config import logger


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Sliding-window rate limiter: each client (identified by IP address)
    may make at most `RATE_LIMIT_REQUESTS` requests per
    `RATE_LIMIT_WINDOW_SECONDS` seconds.
    """

    EXEMPT_PATHS = {"/", "/health", "/version", "/docs", "/redoc", "/openapi.json"}

    def __init__(self, app):
        super().__init__(app)
        self._requests: Dict[str, Deque[float]] = defaultdict(deque)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)

        client_id = request.client.host if request.client else "unknown"
        now = time.time()
        window_start = now - settings.RATE_LIMIT_WINDOW_SECONDS

        timestamps = self._requests[client_id]
        while timestamps and timestamps[0] < window_start:
            timestamps.popleft()

        if len(timestamps) >= settings.RATE_LIMIT_REQUESTS:
            logger.warning("Rate limit exceeded | client={}", client_id)
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": (
                            f"Rate limit of {settings.RATE_LIMIT_REQUESTS} requests per "
                            f"{settings.RATE_LIMIT_WINDOW_SECONDS}s exceeded. Please retry later."
                        ),
                    },
                },
                headers={"Retry-After": str(settings.RATE_LIMIT_WINDOW_SECONDS)},
            )

        timestamps.append(now)
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_REQUESTS)
        response.headers["X-RateLimit-Remaining"] = str(
            max(0, settings.RATE_LIMIT_REQUESTS - len(timestamps))
        )
        return response
