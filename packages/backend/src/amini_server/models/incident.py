import enum

from sqlalchemy import Enum, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class IncidentStatus(str, enum.Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    REMEDIATED = "remediated"
    CLOSED = "closed"
    FALSE_POSITIVE = "false_positive"


class IncidentSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Incident(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "incidents"

    title: Mapped[str] = mapped_column(String(500))
    status: Mapped[IncidentStatus] = mapped_column(
        Enum(IncidentStatus), default=IncidentStatus.OPEN
    )
    severity: Mapped[IncidentSeverity] = mapped_column(
        Enum(IncidentSeverity), default=IncidentSeverity.MEDIUM
    )

    # Links to the violation that triggered this incident
    violation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("policy_violations.id"), index=True
    )
    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("agent_sessions.id"), index=True
    )

    # Incident package data
    policy_name: Mapped[str] = mapped_column(String(255), default="")
    regulation: Mapped[str | None] = mapped_column(String(100), nullable=True)
    regulation_article: Mapped[str | None] = mapped_column(String(100), nullable=True)
    decision_chain_snapshot: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    affected_data_subjects: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    remediation_path: Mapped[str] = mapped_column(Text, default="")
    resolution_notes: Mapped[str] = mapped_column(Text, default="")

    violation: Mapped["PolicyViolation"] = relationship()  # noqa: F821
    session: Mapped["AgentSession"] = relationship()  # noqa: F821
