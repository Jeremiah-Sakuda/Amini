from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import engine
from .models.base import Base
from .routers import decisions, health, ingest, policies, sessions, violations


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup for dev
    if settings.debug:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Amini API",
        description="Agentic workflow auditor — trust infrastructure for AI agents",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(ingest.router)
    app.include_router(sessions.router)
    app.include_router(decisions.router)
    app.include_router(policies.router)
    app.include_router(violations.router)

    return app


app = create_app()
