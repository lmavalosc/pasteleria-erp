from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import DbTenant, TenantId

router = APIRouter(tags=["system"])


@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "api",
        "version": "1.0.0-fase1",
    }


@router.get("/debug/tenant-context", include_in_schema=False)
def debug_tenant_context(
    db: DbTenant,
    tenant_id: TenantId,
):
    current_tenant = db.execute(
        text("SELECT CURRENT_SETTING('app.tenant_id', TRUE)")
    ).scalar()

    return {
        "expected_tenant_id": str(tenant_id),
        "database_tenant_context": current_tenant,
        "tenant_id": current_tenant,
    }


@router.get("/debug/accounts", include_in_schema=False)
def debug_accounts(
    tenant_id: TenantId,
    db: DbTenant,
):
    from app.repositories.accounting import AccountingRepository

    repo = AccountingRepository(db, tenant_id=tenant_id)
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
