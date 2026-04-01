from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import async_session_factory, engine
from .models.base import Base
from .routers import decisions, health, ingest, policies, sessions, violations
from .routers import incidents, registry, regulations, reports


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup for dev
    if settings.debug:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        # Seed regulatory templates
        async with async_session_factory() as db:
            from .services.regulation_service import seed_regulations
            await seed_regulations(db)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Amini API",
        description="Compliance infrastructure for agentic AI",
        version="0.2.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # v1 routers
    app.include_router(health.router)
    app.include_router(ingest.router)
    app.include_router(sessions.router)
    app.include_router(decisions.router)
    app.include_router(policies.router)
    app.include_router(violations.router)

    # v2 routers
    app.include_router(registry.router)
    app.include_router(regulations.router)
    app.include_router(incidents.router)
    app.include_router(reports.router)

    return app


app = create_app()
