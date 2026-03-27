from sqlalchemy import Boolean, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class DecisionNode(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "decision_nodes"

    # --- Metadata tier (always stored) ---
    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("agent_sessions.id"), index=True
    )
    decision_external_id: Mapped[str] = mapped_column(String(255), index=True)
    decision_type: Mapped[str] = mapped_column(String(100), default="generic")
    sequence_number: Mapped[int] = mapped_column(Integer, default=0)
    parent_decision_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("decision_nodes.id"), nullable=True
    )
    action_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    has_error: Mapped[bool] = mapped_column(Boolean, default=False)
    policy_summary: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # --- Payload tier (configurable storage) ---
    input_context: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    reasoning_trace: Mapped[str | None] = mapped_column(Text, nullable=True)
    action_detail: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    output: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    side_effects: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Relationships
    session: Mapped["AgentSession"] = relationship(back_populates="decisions")  # noqa: F821
    parent: Mapped["DecisionNode | None"] = relationship(
        remote_side="DecisionNode.id", backref="children"
    )
    violations: Mapped[list["PolicyViolation"]] = relationship(back_populates="decision_node")  # noqa: F821
