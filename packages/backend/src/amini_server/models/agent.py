from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Agent(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "agents"

    agent_external_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), default="")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)

    # --- v2: Agent Registry fields ---
    framework: Mapped[str] = mapped_column(String(100), default="")
    provider: Mapped[str] = mapped_column(String(100), default="")
    risk_class: Mapped[str] = mapped_column(String(50), default="")
    tags: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    data_access_patterns: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    deployment_status: Mapped[str] = mapped_column(String(50), default="active")
    discovery_method: Mapped[str] = mapped_column(String(50), default="sdk")
    regulations: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    sessions: Mapped[list["AgentSession"]] = relationship(back_populates="agent")  # noqa: F821
