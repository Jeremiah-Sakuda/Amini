import enum

from sqlalchemy import Enum, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class SessionStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ERROR = "error"
    TIMEOUT = "timeout"
    HUMAN_HANDOFF = "human_handoff"


class AgentSession(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "agent_sessions"

    agent_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("agents.id"), index=True
    )
    session_external_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    environment: Mapped[str] = mapped_column(String(50), default="development")
    status: Mapped[SessionStatus] = mapped_column(
        Enum(SessionStatus), default=SessionStatus.ACTIVE
    )
    user_context: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    audit_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    terminal_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    agent: Mapped["Agent"] = relationship(back_populates="sessions")  # noqa: F821
    decisions: Mapped[list["DecisionNode"]] = relationship(back_populates="session")  # noqa: F821
    violations: Mapped[list["PolicyViolation"]] = relationship(back_populates="session")  # noqa: F821
