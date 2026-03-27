import enum

from sqlalchemy import Enum, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ViolationSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PolicyViolation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "policy_violations"

    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("agent_sessions.id"), index=True
    )
    decision_node_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("decision_nodes.id"), nullable=True
    )
    policy_version_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("policy_versions.id"), index=True
    )
    severity: Mapped[ViolationSeverity] = mapped_column(
        Enum(ViolationSeverity), default=ViolationSeverity.MEDIUM
    )
    violation_type: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)
    evidence: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    session: Mapped["AgentSession"] = relationship(back_populates="violations")  # noqa: F821
    decision_node: Mapped["DecisionNode | None"] = relationship(back_populates="violations")  # noqa: F821
    policy_version: Mapped["PolicyVersion"] = relationship(back_populates="violations")  # noqa: F821
