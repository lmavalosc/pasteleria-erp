import math
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db_with_tenant, get_tenant_id_from_header
from app.core.pagination import Page, PageParams
from app.repositories.documents import DocumentRepository
from app.repositories.expenses import ExpenseRepository
from app.schemas.expenses import ExpenseCreate, ExpenseRead
from app.services.expenses import ExpenseService

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post("", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
def create_expense(
    data: ExpenseCreate,
    tenant_id: Annotated[UUID, Depends(get_tenant_id_from_header)],
    db: Annotated[Session, Depends(get_db_with_tenant)],
):
    service = ExpenseService(ExpenseRepository(db), DocumentRepository(db))
    return service.create_expense(tenant_id, data)


@router.get("", response_model=Page[ExpenseRead])
def list_expenses(
    params: Annotated[PageParams, Depends()],
    db: Annotated[Session, Depends(get_db_with_tenant)],
):
    repo = ExpenseRepository(db)
    items, total = repo.list_paginated(params.offset, params.page_size)
    pages = math.ceil(total / params.page_size) if total > 0 else 1
    return Page(
        items=items,
        total=total,
        page=params.page,
        page_size=params.page_size,
        total_pages=pages,
    )
