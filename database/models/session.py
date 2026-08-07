import uuid
from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import mapped_column
from ..base import Base

class Session(Base):
    __tablename__ = "sessions"
    
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "pin_code",
            name="uq_pins_user_id_pin_code",
        ),
        CheckConstraint(
            "expires_at > created_at",
            name="ck_session_expiry_after_creation",
        ),
        CheckConstraint(
            "revoked = false OR revoked_at IS NOT NULL",
            name="ck_revoked_requires_timestamp",
        ),
    )

    id = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    organization_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    device_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    session_token_hash = mapped_column(
        String(128),
        nullable=False,
    )

    authentication_method = mapped_column(
        String(32),
        nullable=True,
    )

    authentication_level = mapped_column(
        String(32),
        nullable=True,
    )

    ip_address = mapped_column(
        String(45),
        nullable=True,
    )

    user_agent = mapped_column(
        String(256),
        nullable=True,
    )

    created_at = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )

    last_activity_at = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    expires_at = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    revoked = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    revoked_at = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    revocation_reason = mapped_column(
        String(256),
        nullable=True,
    )