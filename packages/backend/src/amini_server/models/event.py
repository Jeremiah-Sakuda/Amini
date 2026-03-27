from sqlalchemy import Boolean, Float, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class RawEvent(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "raw_events"

    event_type: Mapped[str] = mapped_column(String(100), index=True)
    agent_id: Mapped[str] = mapped_column(String(255), index=True)
    session_id: Mapped[str] = mapped_column(String(255), index=True)
    decision_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    environment: Mapped[str] = mapped_column(String(50), default="development")
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    sdk_timestamp: Mapped[float] = mapped_column(Float)
    processed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
