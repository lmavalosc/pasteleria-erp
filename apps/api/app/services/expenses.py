import uuid
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import DomainError, DomainException
from app.models.entities import Document, Expense
from app.repositories.documents import DocumentRepository
from app.repositories.expenses import ExpenseRepository
from app.schemas.expenses import (
    ExpenseCreate,
    ExpensePage,
    ExpenseRead,
    ExpenseUpdate,
)
from app.services.common import build_page_meta, paginate


def list_expenses(
    db: Session,
    tenant_id: UUID,
    page: int = 1,
    page_size: int = 20,
) -> ExpensePage:
    stmt = (
        select(Expense)
        .where(Expense.tenant_id == tenant_id)
        .order_by(Expense.expense_date.desc(), Expense.created_at.desc())
    )
    items, total = paginate(db, stmt, page, page_size)
    meta = build_page_meta(total=total, page=page, page_size=page_size)
    return ExpensePage(
        items=[_to_expense_read(e) for e in items],
        **meta.model_dump(),
    )


def create_expense(
    db: Session,
    tenant_id: UUID,
    payload: ExpenseCreate,
) -> ExpenseRead:
    if payload.document_id:
        doc_exists = db.scalar(
            select(Document.id).where(
                Document.tenant_id == tenant_id,
                Document.id == payload.document_id,
            )
        )
        if not doc_exists:
            raise DomainError(
                status_code=404,
                title="Documento no encontrado",
                detail="El archivo adjunto indicado no existe para este tenant.",
                code="DOCUMENT_NOT_FOUND",
            )

    expense = Expense(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        expense_date=payload.expense_date,
        amount=Decimal(str(payload.amount)),
        currency=payload.currency,
        status="draft",
        document_id=payload.document_id,
        description=payload.description,
        merchant=payload.merchant,
    )
    db.add(expense)
    db.flush()
    db.refresh(expense)
    return _to_expense_read(expense)


def get_expense(
    db: Session,
    tenant_id: UUID,
    expense_id: UUID,
) -> ExpenseRead:
    expense = db.scalar(
        select(Expense).where(
            Expense.tenant_id == tenant_id,
            Expense.id == expense_id,
        )
    )
    if not expense:
        raise DomainError(
            status_code=404,
            title="Gasto no encontrado",
            detail=f"El gasto con ID {expense_id} no existe.",
            code="EXPENSE_NOT_FOUND",
        )
    return _to_expense_read(expense)


def update_expense(
    db: Session,
    tenant_id: UUID,
    expense_id: UUID,
    payload: ExpenseUpdate,
) -> ExpenseRead:
    expense = db.scalar(
        select(Expense).where(
            Expense.tenant_id == tenant_id,
            Expense.id == expense_id,
        )
    )
    if not expense:
        raise DomainError(
            status_code=404,
            title="Gasto no encontrado",
            detail=f"El gasto con ID {expense_id} no existe.",
            code="EXPENSE_NOT_FOUND",
        )

    if payload.document_id is not None:
        doc_exists = db.scalar(
            select(Document.id).where(
                Document.tenant_id == tenant_id,
                Document.id == payload.document_id,
            )
        )
        if not doc_exists:
            raise DomainError(
                status_code=404,
                title="Documento no encontrado",
                detail="El archivo adjunto indicado no existe para este tenant.",
                code="DOCUMENT_NOT_FOUND",
            )
        expense.document_id = payload.document_id

    if payload.status is not None:
        expense.status = payload.status
    if payload.description is not None:
        expense.description = payload.description
    if payload.merchant is not None:
        expense.merchant = payload.merchant

    db.flush()
    db.refresh(expense)
    return _to_expense_read(expense)


def _to_expense_read(expense: Expense) -> ExpenseRead:
    return ExpenseRead(
        id=expense.id,
        tenant_id=expense.tenant_id,
        expense_date=expense.expense_date,
        amount=f"{expense.amount:.2f}",
        currency=expense.currency,
        status=expense.status,
        document_id=expense.document_id,
        description=expense.description,
        merchant=expense.merchant,
        created_at=expense.created_at,
        updated_at=expense.updated_at,
    )


# =========================================================================
# Clase ExpenseService para retrocompatibilidad
# =========================================================================
class ExpenseService:
    def __init__(self, expense_repo: ExpenseRepository, doc_repo: DocumentRepository):
        self.expense_repo = expense_repo
        self.doc_repo = doc_repo

    def create_expense(self, tenant_id: uuid.UUID, data: ExpenseCreate) -> Expense:
        if data.document_id:
            doc = self.doc_repo.get_by_id(data.document_id)
            if not doc:
                raise DomainException(
                    "Documento no encontrado",
                    "El archivo adjunto indicado no existe para este tenant.",
                    404,
                )

        expense = Expense(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            expense_date=data.expense_date,
            amount=Decimal(str(data.amount)),
            currency=data.currency,
            status="draft",
            document_id=data.document_id,
            description=data.description,
            merchant=data.merchant,
        )
        return self.expense_repo.create(expense)
