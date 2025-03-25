from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.config import settings
from app.db.session import get_session

from app.routes.entries import router as entries_router
from app.routes.summary import router as summary_router

import logging

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages application startup and shutdown events."""
    # Startup: create tables
    logging.info("Starting up... Creating DB tables if needed.")
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    yield
    logging.info("Shutting down... Lifespan complete.")


app = FastAPI(
    title=settings.project_name,
    version="0.1.0",
    description="General Ledger API",
    lifespan=lifespan,
)

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
