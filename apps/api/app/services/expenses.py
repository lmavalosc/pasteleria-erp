import uuid

from app.core.errors import DomainException
from app.models.operations import Expense
from app.repositories.documents import DocumentRepository
from app.repositories.expenses import ExpenseRepository
from app.schemas.expenses import ExpenseCreate


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

        from decimal import Decimal

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
