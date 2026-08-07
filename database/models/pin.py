import uuid
from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    String,
    CheckConstraint,
    func,
    Integer,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import mapped_column
from ..base import Base

class Pin(Base):
    __tablename__ = "pins"

    __table_args__ = (
        CheckConstraint(
            "failed_attempts >= 0",
            name="ck_pin_failed_attempts_nonnegative",
        )
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

    pin_hash = mapped_column(
        String(128),
        nullable=False,
    )
    
    hash_algorithm = mapped_column(
        String(32),
        nullable=False,
    )

    hash_version = mapped_column(
        String(32),
        nullable=False,
    )

    failed_attempts = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    locked_until = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )

    updated_at = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    last_verified_at = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    last_changed_at = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    active = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )