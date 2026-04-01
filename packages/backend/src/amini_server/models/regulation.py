import enum

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ComplianceStatus(str, enum.Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NOT_ASSESSED = "not_assessed"


class Regulation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "regulations"

    name: Mapped[str] = mapped_column(String(255), unique=True)
    short_code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    version: Mapped[str] = mapped_column(String(50), default="1.0")
    jurisdiction: Mapped[str] = mapped_column(String(100), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    effective_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    requirements: Mapped[list["RegulatoryRequirement"]] = relationship(
        back_populates="regulation", cascade="all, delete-orphan"
    )


class RegulatoryRequirement(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "regulatory_requirements"

    regulation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("regulations.id"), index=True
    )
    article: Mapped[str] = mapped_column(String(50))
    section: Mapped[str] = mapped_column(String(100), default="")
    title: Mapped[str] = mapped_column(String(500), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    evidence_types: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    applies_to_risk_class: Mapped[str | None] = mapped_column(String(50), nullable=True)
    review_cadence_days: Mapped[int] = mapped_column(Integer, default=90)

    regulation: Mapped["Regulation"] = relationship(back_populates="requirements")
    mappings: Mapped[list["ComplianceMapping"]] = relationship(
        back_populates="requirement", cascade="all, delete-orphan"
    )


class ComplianceMapping(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "compliance_mappings"

    agent_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("agents.id"), index=True
    )
    requirement_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("regulatory_requirements.id"), index=True
    )
    status: Mapped[ComplianceStatus] = mapped_column(
        Enum(ComplianceStatus), default=ComplianceStatus.NOT_ASSESSED
    )
    evidence: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="")
    last_reviewed: Mapped[str | None] = mapped_column(String(20), nullable=True)
    next_review_due: Mapped[str | None] = mapped_column(String(20), nullable=True)

    requirement: Mapped["RegulatoryRequirement"] = relationship(back_populates="mappings")
