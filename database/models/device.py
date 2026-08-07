from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, mapped_column
from sqlalchemy.sql import func
import uuid
from models import Base

class Device(Base):
    __tablename__ = "devices"

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

    device_identifier = mapped_column(
        String(128),
        nullable=False,
        index=True,
    )

    platform = mapped_column(
        String(32),
        nullable=True,
    )

    os_name = mapped_column(
        String(64),
        nullable=True,
    )

    browser = mapped_column(
        String(64),
        nullable=True,
    )

    trust_score = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    trusted = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    revoked = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    first_seen_at = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    last_seen_at = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    trusted_until = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    user = relationship(
        "User",
        back_populates="devices",
    )