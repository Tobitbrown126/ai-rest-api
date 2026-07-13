"""
middleware/logging.py
----------------------
ASGI middleware that logs every incoming request and outgoing response,
including execution time, and persists a lightweight usage record to the
database for auditing/analytics purposes.
"""

import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from database import SessionLocal
from logging_config import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs request method/path, response status, and execution time for
    every request. Also writes a row to `api_usage_logs` for endpoints
    that aren't the docs/openapi routes, to keep the log table focused
    on meaningful API traffic.
    """

    SKIP_PATHS = {"/docs", "/redoc", "/openapi.json", "/favicon.ico"}

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        start_time = time.perf_counter()

        logger.bind(request_id=request_id).info(
            "Incoming request | method={} | path={} | client={}",
            request.method,
            request.url.path,
            request.client.host if request.client else "unknown",
        )

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.bind(request_id=request_id).exception(
                "Request failed | method={} | path={} | duration_ms={:.2f}",
                request.method,
                request.url.path,
                duration_ms,
            )
            raise

        duration_ms = (time.perf_counter() - start_time) * 1000
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-Ms"] = f"{duration_ms:.2f}"

        logger.bind(request_id=request_id).info(
            "Outgoing response | method={} | path={} | status={} | duration_ms={:.2f}",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )

        if request.url.path not in self.SKIP_PATHS:
            self._persist_usage_log(request, response, duration_ms, request_id)

        return response

    @staticmethod
    def _persist_usage_log(
        request: Request, response: Response, duration_ms: float, request_id: str
    ) -> None:
        """Best-effort write of a usage log row; never raises to the caller."""
        try:
            from models import ApiUsageLog

            db = SessionLocal()
            try:
                db.add(
                    ApiUsageLog(
                        endpoint=request.url.path,
                        method=request.method,
                        status_code=response.status_code,
                        execution_time_ms=duration_ms,
                        client_host=request.client.host if request.client else None,
                        request_id=request_id,
                    )
                )
                db.commit()
            finally:
                db.close()
        except Exception:
            logger.exception("Failed to persist API usage log")
