from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.api.deps import get_db_with_tenant, get_tenant_id_from_header
from app.repositories.accounting import AccountingRepository

router = APIRouter(tags=["system"])


@router.get("/health")
def health():
    return {"status": "ok", "service": "api", "version": "1.0.0-fase1"}


@router.get("/debug/tenant-context")
def debug_tenant_context(db: Annotated[Session, Depends(get_db_with_tenant)]):
    tenant_id = db.execute(text("SELECT CURRENT_SETTING('app.tenant_id', TRUE)")).scalar()
    return {"tenant_id": tenant_id}


@router.get("/debug/accounts")
def debug_accounts(
    tenant_id: Annotated[UUID, Depends(get_tenant_id_from_header)],
    db: Annotated[Session, Depends(get_db_with_tenant)],
):
    repo = AccountingRepository(db)
    accounts = repo.list_accounts()
    return {
        "tenant_id": str(tenant_id),
        "total_accounts": len(accounts),
        "accounts": [
            {
                "code": acc.code,
                "name": acc.name,
                "account_type": acc.account_type,
            }
            for acc in accounts
        ],
    }
