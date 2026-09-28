from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Header, Query

from app.api.deps import DbTenant, TenantId
from app.schemas.accounting import (
    AccountingAccountCreate,
    AccountingAccountPage,
    AccountingAccountRead,
    AccountingAccountUpdate,
    JournalEntryCreate,
    JournalEntryPage,
    JournalEntryRead,
)
from app.services import accounting as accounting_service

router = APIRouter(prefix="/accounting", tags=["accounting"])


@router.get("/accounts", response_model=AccountingAccountPage)
def list_accounts(
    db: DbTenant,
    tenant_id: TenantId,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    return accounting_service.list_accounts(db, tenant_id, page, page_size)


@router.post("/accounts", response_model=AccountingAccountRead, status_code=201)
def create_account(
    db: DbTenant,
    tenant_id: TenantId,
    payload: AccountingAccountCreate,
    idempotency_key: Annotated[str | None, Header()] = None,
):
    # Idempotency-key queda preparado para fases posteriores.
    _ = idempotency_key
    return accounting_service.create_account(db, tenant_id, payload)


@router.get("/accounts/{account_id}", response_model=AccountingAccountRead)
def get_account(
    db: DbTenant,
    tenant_id: TenantId,
    account_id: UUID,
):
    return accounting_service.get_account(db, tenant_id, account_id)


@router.patch("/accounts/{account_id}", response_model=AccountingAccountRead)
def update_account(
    db: DbTenant,
    tenant_id: TenantId,
    account_id: UUID,
    payload: AccountingAccountUpdate,
):
    return accounting_service.update_account(db, tenant_id, account_id, payload)


@router.get("/journal-entries", response_model=JournalEntryPage)
def list_journal_entries(
    db: DbTenant,
    tenant_id: TenantId,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    return accounting_service.list_journal_entries(db, tenant_id, page, page_size)


@router.post("/journal-entries", response_model=JournalEntryRead, status_code=201)
def create_journal_entry(
    db: DbTenant,
    tenant_id: TenantId,
    payload: JournalEntryCreate,
    idempotency_key: Annotated[str | None, Header()] = None,
):
    _ = idempotency_key
    return accounting_service.create_journal_entry(db, tenant_id, payload)


@router.get("/journal-entries/{entry_id}", response_model=JournalEntryRead)
def get_journal_entry(
    db: DbTenant,
    tenant_id: TenantId,
    entry_id: UUID,
):
    return accounting_service.get_journal_entry(db, tenant_id, entry_id)


@router.post("/journal-entries/{entry_id}/post", response_model=JournalEntryRead)
def post_journal_entry(
    db: DbTenant,
    tenant_id: TenantId,
    entry_id: UUID,
):
    return accounting_service.post_journal_entry(db, tenant_id, entry_id)
