import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.entities import Base


class TenantMixin:
    """Añade la clave tenant_id obligatoria a todas las tablas de negocio."""

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )


class CreatedAtMixin:
    """Marca de tiempo de creación en UTC."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class TimestampMixin(CreatedAtMixin):
    """Marcas de tiempo de creación y actualización en UTC."""

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


__all__ = ["Base", "CreatedAtMixin", "TenantMixin", "TimestampMixin"]
