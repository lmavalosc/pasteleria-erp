from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.db import SessionLocal


def get_db():
    """
    Abre una sesión SQLAlchemy dentro de una transacción.

    SET LOCAL requiere transacción activa.
    """
    with SessionLocal() as session, session.begin():
        yield session


def get_tenant_id_from_header(
    x_tenant_id: Annotated[str | None, Header(alias="X-Tenant-ID")] = None,
) -> UUID:
    """
    Desarrollo/Fase 1:
    El tenant llega por header X-Tenant-ID.

    Producción:
    Este dependency debe reemplazarse por uno que derive tenant
    desde autenticación y memberships.
    """
    if not x_tenant_id:
        raise HTTPException(
            status_code=400,
            detail="Falta header X-Tenant-ID",
        )

    try:
        return UUID(x_tenant_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="X-Tenant-ID debe ser un UUID válido",
        )


def get_db_with_tenant(
    db: Annotated[Session, Depends(get_db)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id_from_header)],
) -> Session:
    """
    Inyecta sesión DB con tenant context activo para RLS.
    """
    db.execute(
        text("SELECT set_config('app.tenant_id', :tenant_id, true)"),
        {"tenant_id": str(tenant_id)},
    )
    return db


DbTenant = Annotated[Session, Depends(get_db_with_tenant)]
TenantId = Annotated[UUID, Depends(get_tenant_id_from_header)]
get_current_tenant_id = get_tenant_id_from_header
