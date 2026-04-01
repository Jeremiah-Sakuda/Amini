import enum

from sqlalchemy import Enum, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ReportStatus(str, enum.Enum):
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class AuditReport(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "audit_reports"

    title: Mapped[str] = mapped_column(String(500))
    report_type: Mapped[str] = mapped_column(String(100))
    framework: Mapped[str] = mapped_column(String(100))
    status: Mapped[ReportStatus] = mapped_column(
        Enum(ReportStatus), default=ReportStatus.GENERATING
    )
    period_start: Mapped[str] = mapped_column(String(20))
    period_end: Mapped[str] = mapped_column(String(20))
    agent_ids: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    content: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    summary: Mapped[str] = mapped_column(Text, default="")
    gap_analysis: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    generated_by: Mapped[str] = mapped_column(String(255), default="system")
