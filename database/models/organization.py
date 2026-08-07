import uuid
from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import mapped_column
from ..base import Base

class Organization(Base):
    __tablename__ = "organizations"

    __table_args__ = (
        UniqueConstraint(
            "slug",
            name="uq_organizations_slug",
        ),
    )

    id = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name = mapped_column(
        String(160),
        nullable=False,
    )

    slug = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    owner_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    active = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    plan = mapped_column(
        String(32),
        nullable=False,
        default="free",
        server_default="free",
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