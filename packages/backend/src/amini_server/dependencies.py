from collections.abc import AsyncGenerator

from fastapi import Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .database import async_session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session


async def verify_api_key(authorization: str = Header(default="")) -> str:
    """Validate the Bearer token against configured API keys."""
    if not settings.api_keys:
        return ""

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = authorization.removeprefix("Bearer ").strip()
    if token not in settings.api_keys:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return token
