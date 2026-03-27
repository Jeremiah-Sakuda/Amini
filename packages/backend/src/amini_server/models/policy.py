import enum

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class PolicyTier(str, enum.Enum):
    DETERMINISTIC = "deterministic"
    SEMANTIC = "semantic"


class PolicyEnforcement(str, enum.Enum):
    BLOCK = "block"
    WARN = "warn"
    LOG_ONLY = "log_only"
    ALERT_ONLY = "alert_only"


class Policy(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "policies"

    name: Mapped[str] = mapped_column(String(255), unique=True)
    description: Mapped[str] = mapped_column(Text, default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    versions: Mapped[list["PolicyVersion"]] = relationship(
        back_populates="policy", order_by="PolicyVersion.version_number"
    )


class PolicyVersion(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "policy_versions"

    policy_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("policies.id"), index=True
    )
    version_number: Mapped[int] = mapped_column(Integer, default=1)
    yaml_content: Mapped[str] = mapped_column(Text)
    parsed_rule: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    scope: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    tier: Mapped[PolicyTier] = mapped_column(Enum(PolicyTier), default=PolicyTier.DETERMINISTIC)
    enforcement: Mapped[PolicyEnforcement] = mapped_column(
        Enum(PolicyEnforcement), default=PolicyEnforcement.LOG_ONLY
    )
    severity: Mapped[str] = mapped_column(String(20), default="medium")
    message: Mapped[str] = mapped_column(Text, default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    policy: Mapped["Policy"] = relationship(back_populates="versions")
    violations: Mapped[list["PolicyViolation"]] = relationship(back_populates="policy_version")  # noqa: F821
