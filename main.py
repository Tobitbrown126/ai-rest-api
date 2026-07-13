"""
main.py
-------
Application entrypoint. Constructs the FastAPI app, wires up middleware,
exception handlers, routers, and startup/shutdown lifecycle hooks.

Run locally with:
    uvicorn main:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import init_db
from logging_config import configure_logging, logger
from middleware.authentication import AuthContextMiddleware
from middleware.exceptions import register_exception_handlers
from middleware.logging import RequestLoggingMiddleware
from middleware.rate_limit import RateLimitMiddleware
from routers import chat, code, email, health, prompt, summarize, translate


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- startup ---
    configure_logging()
    logger.info("Starting {} v{} [{}]", settings.APP_NAME, settings.APP_VERSION, settings.ENVIRONMENT)
    init_db()
    logger.info("Database initialized")
    yield
    # --- shutdown ---
    logger.info("Shutting down {}", settings.APP_NAME)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "A production-quality AI REST API built with FastAPI, exposing chat, "
        "translation, summarization, email generation, code assistance, and "
        "prompt engineering endpoints powered by the OpenAI Responses API."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# ----------------------------------------------------------------------
# Middleware (order matters: outermost added last is executed first)
# ----------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(AuthContextMiddleware)

# ----------------------------------------------------------------------
# Exception handlers
# ----------------------------------------------------------------------
register_exception_handlers(app)

# ----------------------------------------------------------------------
# Routers
# ----------------------------------------------------------------------
app.include_router(health.router)
app.include_router(chat.router)
app.include_router(translate.router)
app.include_router(summarize.router)
app.include_router(email.router)
app.include_router(code.router)
app.include_router(prompt.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=not settings.is_production,
    )
