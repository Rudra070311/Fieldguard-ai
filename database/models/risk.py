from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from ..base import Base

class Risk(Base):
    __tablename__ = "risks"

    __table_args__ = (
        CheckConstraint(
            "risk_score >= 0 AND risk_score <= 1",
            name="ck_risk_score_range",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    session_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    device_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    risk_factors: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
    )

    risk_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    risk_level: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="low",
    )

    action: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
    )

    model_version: Mapped[Optional[str]] = mapped_column(
        String(32),
        nullable=True,
    )

    policy_version: Mapped[Optional[str]] = mapped_column(
        String(32),
        nullable=True,
    )

    embedding_version: Mapped[Optional[str]] = mapped_column(
        String(32),
        nullable=True,
    )

    explanation: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    factor_contributions: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
    )

    event_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )

    request_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
    )

    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )