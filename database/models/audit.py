import uuid
from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import mapped_column
from ..base import Base

class Audit(Base):
    __tablename__ = "audit_events"

    id = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    event_type = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )

    action = mapped_column(
        String(128),
        nullable=False,
    )

    result = mapped_column(
        String(32),
        nullable=False,
        index=True,
    )

    ip_address = mapped_column(
        String(45),
        nullable=True,
    )

    user_agent = mapped_column(
        String(512),
        nullable=True,
    )

    metadata = mapped_column(
        JSONB,
        nullable=True,
    )

    created_at = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )