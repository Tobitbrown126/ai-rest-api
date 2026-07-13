"""
routers/health.py
-------------------
Public, unauthenticated endpoints:
    GET /          - basic welcome / discovery info
    GET /health    - liveness/readiness probe (checks DB connectivity)
    GET /version   - build/version metadata
"""

from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from schemas import HealthResponse, RootResponse, VersionResponse

router = APIRouter(tags=["System"])


@router.get("/", response_model=RootResponse, summary="API root")
async def root() -> RootResponse:
    return RootResponse(
        message=f"Welcome to {settings.APP_NAME}. See /docs for interactive API documentation.",
        docs_url="/docs",
        redoc_url="/redoc",
        version=settings.APP_VERSION,
    )


@router.get("/health", response_model=HealthResponse, summary="Health check")
async def health_check(db: Session = Depends(get_db)) -> HealthResponse:
    db_status = "ok"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unavailable"

    return HealthResponse(
        status="ok" if db_status == "ok" else "degraded",
        timestamp=datetime.utcnow(),
        environment=settings.ENVIRONMENT,
        database=db_status,
    )


@router.get("/version", response_model=VersionResponse, summary="Version info")
async def version() -> VersionResponse:
    return VersionResponse(app_name=settings.APP_NAME, version=settings.APP_VERSION)
