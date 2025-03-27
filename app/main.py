from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.config import settings
from app.db.session import get_session, engine

from app.routes.accounts import router as accounts_router
from app.routes.entries import router as entries_router
from app.routes.summary import router as summary_router

import logging
from app.utils.logger import setup_logging

import sentry_sdk
from sentry_sdk.scrubber import EventScrubber
from sentry_sdk.integrations.starlette import StarletteIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration

setup_logging()  # Optional: setup_logging("DEBUG")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages application startup and shutdown events."""
    yield
    await engine.dispose()  # Close all pooled connections
    logging.info("Shutting down... Lifespan complete.")


if settings.sentry_dsn:
    logger.info("Type of DSN: %s", type(settings.sentry_dsn))
    logger.info("Length of DSN: %d", len(settings.sentry_dsn))
    sentry_sdk.init(
        dsn=settings.sentry_dsn.strip().strip('"'),
        traces_sample_rate=1.0,
        environment="development",
        send_default_pii=False,
        event_scrubber=EventScrubber(),
        integrations=[
            StarletteIntegration(
                transaction_style="endpoint",
                failed_request_status_codes={403, *range(500, 599)},
                http_methods_to_capture=("GET",),
            ),
            FastApiIntegration(
                transaction_style="endpoint",
                failed_request_status_codes={403, *range(500, 599)},
                http_methods_to_capture=("GET",),
            ),
        ],
    )


app = FastAPI(
    title=settings.project_name,
    version="0.1.0",
    description="General Ledger API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(accounts_router, prefix="/api")
app.include_router(entries_router, prefix="/api")
app.include_router(summary_router, prefix="/api")


@app.get("/healthz", tags=["Health"])
async def healthcheck():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/test-db", tags=["Health"])
async def test_db(session: AsyncSession = Depends(get_session)):
    """Test database connection."""
    try:
        result = await session.execute(text("SELECT version();"))
        version = result.scalar()
        return {"message": "Database connected", "version": version}
    except Exception as e:
        return {"error": f"Failed to connect to database: {str(e)}"}


@app.get(
    "/sentry-debug",
    tags=["Sentry Debugging"],
    summary="Test Sentry.io integration",
    description="Only works if SENTRY_DSN specified in .env file",
)
async def trigger_error():
    """Check if Sentry.io integration is working (only works with SENTRY_DSN specified in .env)"""
    division_by_zero = 1 / 0
