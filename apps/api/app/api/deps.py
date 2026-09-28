from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.db import SessionLocal


def get_db():
    """
    Abre una sesión SQLAlchemy dentro de una transacción.
    SET LOCAL requiere transacción activa -> session.begin() lo garantiza.
    """
    with SessionLocal() as session:
        with session.begin():
            yield session


def get_tenant_id(
    x_tenant_id: Annotated[
        UUID,
        Header(
            alias="X-Tenant-ID",
            description="Identificador del tenant actual (UUID obligatorio)",
        ),
    ],
) -> UUID:
    """
    Extrae y valida X-Tenant-ID como UUID obligatorio sin defaults ni fallbacks silenciosos.
    """
    return x_tenant_id


def get_db_with_tenant(
    db: Annotated[Session, Depends(get_db)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
) -> Session:
    """
    Inyecta sesión DB con tenant context activo para RLS.
    Usa set_config con is_local=true -> aislado a esta transacción.
    """
    db.execute(
        text("SELECT set_config('app.tenant_id', :tenant_id, true)"),
        {"tenant_id": str(tenant_id)},
    )
    return db


# Type aliases para inyección concisa en routers
DbTenant = Annotated[Session, Depends(get_db_with_tenant)]
TenantId = Annotated[UUID, Depends(get_tenant_id)]

# Retrocompatibilidad con routers existentes
get_tenant_id_from_header = get_tenant_id
get_current_tenant_id = get_tenant_id
