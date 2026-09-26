from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.db import SessionLocal


def get_db():
    """
    Abre una sesión SQLAlchemy dentro de una transacción.
    SET LOCAL requiere una transacción activa (with session.begin()).
    """
    with SessionLocal() as session:
        with session.begin():
            yield session


def get_tenant_id_from_header(
    x_tenant_id: Annotated[str | None, Header(alias="X-Tenant-ID")] = None,
) -> UUID:
    """
    Fase 1 / Desarrollo:
    El tenant llega mediante el encabezado HTTP X-Tenant-ID.
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


# Alias para compatibilidad
get_current_tenant_id = get_tenant_id_from_header


def get_db_with_tenant(
    db: Annotated[Session, Depends(get_db)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id_from_header)],
) -> Session:
    """
    Inyecta la sesión de base de datos con el contexto de tenant activo en PostgreSQL.
    set_config con is_local=true aplica la variable de sesión únicamente a la transacción actual.
    """
    db.execute(
        text(
            "SELECT set_config('app.tenant_id', :tenant_id, true), "
            "set_config('app.current_tenant_id', :tenant_id, true);"
        ),
        {"tenant_id": str(tenant_id)},
    )
    return db
