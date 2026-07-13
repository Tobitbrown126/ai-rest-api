"""
middleware/exceptions.py
-------------------------
Custom exception types and centralized exception handlers.

Registering these handlers on the FastAPI app ensures every error
response - whether from validation, application logic, or an
unexpected failure - is returned as a consistent, structured JSON
payload with a meaningful HTTP status code.
"""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from logging_config import logger


class AppException(Exception):
    """Base class for all application-specific exceptions."""

    def __init__(self, message: str, code: str = "APP_ERROR", status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class AIServiceError(AppException):
    """Raised when the upstream AI provider fails or returns an invalid response."""

    def __init__(self, message: str = "AI service failed to generate a response"):
        super().__init__(message, code="AI_SERVICE_ERROR", status_code=status.HTTP_502_BAD_GATEWAY)


class ResourceNotFoundError(AppException):
    """Raised when a requested resource (e.g. conversation) does not exist."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, code="NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)


class RateLimitExceededError(AppException):
    """Raised by the rate limiting middleware when a client exceeds their quota."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message, code="RATE_LIMIT_EXCEEDED", status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )


def _error_payload(code: str, message: str) -> dict:
    return {"success": False, "error": {"code": code, "message": message}}


def register_exception_handlers(app: FastAPI) -> None:
    """Attach all exception handlers to the given FastAPI application."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        logger.warning(
            "Application exception | path={} | code={} | message={}",
            request.url.path,
            exc.code,
            exc.message,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_payload(exc.code, exc.message),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors = exc.errors()
        logger.warning("Validation error | path={} | errors={}", request.url.path, errors)
        readable = "; ".join(
            f"{'.'.join(str(loc) for loc in e['loc'])}: {e['msg']}" for e in errors
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_error_payload("VALIDATION_ERROR", readable or "Invalid request payload"),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        logger.warning(
            "HTTP exception | path={} | status={} | detail={}",
            request.url.path,
            exc.status_code,
            exc.detail,
        )
        code = "UNAUTHORIZED" if exc.status_code == 401 else "HTTP_ERROR"
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_payload(code, str(exc.detail)),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception | path={}", request.url.path)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_payload("INTERNAL_SERVER_ERROR", "An unexpected error occurred"),
        )
