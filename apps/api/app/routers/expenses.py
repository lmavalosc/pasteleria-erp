from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Header, Path, Query

from app.api.deps import DbTenant, TenantId
from app.schemas.expenses import (
    ExpenseCreate,
    ExpensePage,
    ExpenseRead,
    ExpenseUpdate,
)
from app.services import expenses as expenses_service

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.get("", response_model=ExpensePage)
def list_expenses(
    db: DbTenant,
    tenant_id: TenantId,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    return expenses_service.list_expenses(db, tenant_id, page, page_size)


@router.post("", response_model=ExpenseRead, status_code=201)
def create_expense(
    db: DbTenant,
    tenant_id: TenantId,
    payload: ExpenseCreate,
    idempotency_key: Annotated[str | None, Header()] = None,
):
    _ = idempotency_key
    return expenses_service.create_expense(db, tenant_id, payload)


@router.get("/{expenseId}", response_model=ExpenseRead)
def get_expense(
    db: DbTenant,
    tenant_id: TenantId,
    expense_id: Annotated[UUID, Path(alias="expenseId")],
):
    return expenses_service.get_expense(db, tenant_id, expense_id)


@router.patch("/{expenseId}", response_model=ExpenseRead)
def update_expense(
    db: DbTenant,
    tenant_id: TenantId,
    expense_id: Annotated[UUID, Path(alias="expenseId")],
    payload: ExpenseUpdate,
):
    return expenses_service.update_expense(db, tenant_id, expense_id, payload)
