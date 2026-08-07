from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    String,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql import func
import uuid
from ..base import Base

class Risk(Base):
    __tablename__ = "risks"
    
    id = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    organization_id = mapped_column(
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    
    session_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    
    device_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    
    risk_factors = mapped_column(
        JSONB,
        nullable=True,
    )
    
    risk_score = mapped_column(
        Float,
        __table_args__ = (
            CheckConstraint(
                "risk_score >= 0 AND risk_score <= 1",
                name="ck_risk_score_range",
            ),
        ),
        nullable=False,
        default=0.0,
    )

    risk_level = mapped_column(
        String(32),
        nullable=False,
        default="low",
    )
    
    action = mapped_column(
        String(128),
        nullable=True,
    )
    
    model_version = mapped_column(
        String(32),
        nullable=True,
    )
    
    policy_version = mapped_column(
        String(32),
        nullable=True,
    )
    
    embedding_version = mapped_column(
        String(32),
        nullable=True,
    )

    explanation = mapped_column(
        JSONB,
        nullable=False,    
    )
    
    factors_contribution = mapped_column(
        JSONB,
        nullable=True,    
    )
    
    event_type = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )
    
    request_id = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
    )
    
    ip_address = mapped_column(
        String(45),
        nullable=True,
    )
    
    created_at = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )
    