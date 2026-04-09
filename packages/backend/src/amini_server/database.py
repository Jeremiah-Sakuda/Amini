from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .config import settings

_pool_kwargs: dict = {}
if not settings.database_url.startswith("sqlite"):
    _pool_kwargs = {
        "pool_size": settings.pool_size,
        "max_overflow": settings.max_overflow,
        "pool_recycle": settings.pool_recycle,
    }

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
    **_pool_kwargs,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
