from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import get_db_with_tenant, get_tenant_id_from_header
from uuid import UUID

router = APIRouter(tags=["system"])


@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "api",
        "version": "1.0.0-fase1",
    }


@router.get("/debug/tenant-context")
def debug_tenant_context(
    db: Annotated[Session, Depends(get_db_with_tenant)],
):
    tenant_id = db.execute(
        text("SELECT CURRENT_SETTING('app.tenant_id', TRUE)")
    ).scalar()

    return {
        "tenant_id": tenant_id,
    }


@router.get("/debug/accounts")
def debug_accounts(
    tenant_id: Annotated[UUID, Depends(get_tenant_id_from_header)],
    db: Annotated[Session, Depends(get_db_with_tenant)],
):
    query = text("SELECT id, code, name, account_type FROM accounting_accounts ORDER BY code;")
    results = db.execute(query).mappings().fetchall()

    return {
        "tenant_id": str(tenant_id),
        "total_accounts": len(results),
        "accounts": [dict(row) for row in results],
    }
