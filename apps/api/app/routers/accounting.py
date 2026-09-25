from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.schemas.core_models import (
    AccountResponse, JournalEntryCreateRequest, JournalEntryResponse,
    UserRole
)
from app.core.deps import get_current_context, require_roles
from app.services.accounting_service import accounting_store

router = APIRouter(prefix="/v1/accounting", tags=["accounting"])

@router.get("/accounts", response_model=List[AccountResponse])
def get_accounts(
    context: TenantContext = Depends(get_current_context)
):
    accs = accounting_store.list_accounts(context.tenant_id)
    return [AccountResponse(**a) for a in accs]

@router.post("/accounts/seed-default", response_model=List[AccountResponse])
def seed_default_accounts(
    context: TenantContext = Depends(require_roles([UserRole.OWNER, UserRole.ADMIN, UserRole.ACCOUNTANT]))
):
    created = accounting_store.seed_defaults(context.tenant_id)
    all_accs = accounting_store.list_accounts(context.tenant_id)
    return [AccountResponse(**a) for a in all_accs]

@router.post("/entries", response_model=JournalEntryResponse, status_code=status.HTTP_201_CREATED)
def create_journal_entry(
    payload: JournalEntryCreateRequest,
    context: TenantContext = Depends(require_roles([UserRole.OWNER, UserRole.ADMIN, UserRole.ACCOUNTANT]))
):
    # Verify account IDs belong to tenant
    for item in payload.items:
        acc = accounting_store.get_account_by_id(item.account_id, context.tenant_id)
        if not acc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La cuenta contable {item.account_id} no existe en su empresa."
            )

    entry = accounting_store.create_entry(context.tenant_id, payload)
    return JournalEntryResponse(**entry)

@router.post("/entries/{id}/post", response_model=JournalEntryResponse)
def post_journal_entry(
    id: str,
    context: TenantContext = Depends(require_roles([UserRole.OWNER, UserRole.ADMIN, UserRole.ACCOUNTANT]))
):
    try:
        entry = accounting_store.post_entry(id, context.tenant_id)
        return JournalEntryResponse(**entry)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/entries/{id}/void", response_model=JournalEntryResponse)
def void_journal_entry(
    id: str,
    context: TenantContext = Depends(require_roles([UserRole.OWNER, UserRole.ADMIN, UserRole.ACCOUNTANT]))
):
    try:
        entry = accounting_store.void_entry(id, context.tenant_id)
        return JournalEntryResponse(**entry)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
