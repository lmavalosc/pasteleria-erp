from decimal import Decimal, InvalidOperation
from math import ceil
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.core.errors import DomainError, DomainException
from app.schemas.common import PageMeta


def parse_money(value: str) -> Decimal:
    """
    Convierte un string decimal a Decimal cuantizado a 2 decimales.
    Lanza DomainError 422 si el formato es inválido.
    """
    try:
        return Decimal(value).quantize(Decimal("0.01"))
    except InvalidOperation as exc:
        raise DomainError(
            status_code=422,
            title="Valor monetario inválido",
            detail=f"No se pudo interpretar el valor '{value}' como decimal.",
            code="INVALID_MONETARY_VALUE",
        ) from exc


def decimal_to_str(value: Decimal) -> str:
    """
    Serializa Decimal a string formateado a 2 decimales exactos.
    """
    return str(value.quantize(Decimal("0.01")))


def paginate(
    db: Session,
    stmt: Select,
    page: int,
    page_size: int,
) -> tuple[list, int]:
    """
    Ejecuta paginación en dos pasos:
    1. COUNT(*) optimizado sobre un subquery sin ORDER BY.
    2. Consulta paginada con OFFSET y LIMIT.
    """
    count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
    total = db.scalar(count_stmt) or 0

    items = db.scalars(
        stmt.offset((page - 1) * page_size).limit(page_size)
    ).all()

    return list(items), int(total)


def build_page_meta(total: int, page: int, page_size: int) -> PageMeta:
    """
    Construye los metadatos estándar de paginación para las respuestas API.
    """
    total_pages = ceil(total / page_size) if page_size > 0 else 0
    return PageMeta(
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
    )


class BaseService:
    """Clase base para servicios de dominio."""

    def __init__(self, tenant_id: UUID | None = None):
        self.tenant_id = tenant_id

    def ensure_tenant(self) -> UUID:
        if not self.tenant_id:
            raise DomainException(
                "Contexto de tenant requerido",
                "La operación exige un tenant_id válido.",
                400,
            )
        return self.tenant_id
