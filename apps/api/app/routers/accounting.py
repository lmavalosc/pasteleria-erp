import math
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db_with_tenant, get_tenant_id_from_header
from app.core.pagination import Page, PageParams
from app.repositories.accounting import AccountingRepository
from app.schemas.accounting import (
    AccountCreate,
    AccountRead,
    JournalEntryCreate,
    JournalEntryRead,
)
from app.services.accounting import AccountingService

router = APIRouter(prefix="/accounting", tags=["accounting"])


@router.get("/accounts", response_model=list[AccountRead])
def list_accounts(db: Annotated[Session, Depends(get_db_with_tenant)]):
    repo = AccountingRepository(db)
    return repo.list_accounts()


@router.post("/accounts", response_model=AccountRead, status_code=status.HTTP_201_CREATED)
def create_account(
    data: AccountCreate,
    tenant_id: Annotated[UUID, Depends(get_tenant_id_from_header)],
    db: Annotated[Session, Depends(get_db_with_tenant)],
):
    service = AccountingService(AccountingRepository(db))
    return service.create_account(tenant_id, data)


@router.post(
    "/journal-entries",
    response_model=JournalEntryRead,
    status_code=status.HTTP_201_CREATED,
)
def create_journal_entry(
    data: JournalEntryCreate,
    tenant_id: Annotated[UUID, Depends(get_tenant_id_from_header)],
    db: Annotated[Session, Depends(get_db_with_tenant)],
):
    service = AccountingService(AccountingRepository(db))
    return service.create_journal_entry(tenant_id, data)


@router.get("/journal-entries", response_model=Page[JournalEntryRead])
def list_journal_entries(
    params: Annotated[PageParams, Depends()],
    db: Annotated[Session, Depends(get_db_with_tenant)],
):
    repo = AccountingRepository(db)
    items, total = repo.list_journal_entries_paginated(params.offset, params.page_size)
    pages = math.ceil(total / params.page_size) if total > 0 else 1
    return Page(
        items=items,
        total=total,
        page=params.page,
        page_size=params.page_size,
        total_pages=pages,
    )
