from uuid import UUID

from app.core.errors import DomainException


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
