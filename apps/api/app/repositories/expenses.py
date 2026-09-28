import uuid
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.entities import Expense


class ExpenseRepository:
    def __init__(self, db: Session, tenant_id: uuid.UUID | None = None):
        self.db = db
        self.tenant_id = tenant_id

    def create(self, expense: Expense) -> Expense:
        self.db.add(expense)
        self.db.flush()
        return expense

    def get_by_id(self, expense_id: uuid.UUID) -> Expense | None:
        q = self.db.query(Expense).filter(Expense.id == expense_id)
        if self.tenant_id:
            q = q.filter(Expense.tenant_id == self.tenant_id)
        return q.first()

    def list_paginated(self, offset: int, limit: int) -> tuple[list[Expense], int]:
        count_q = self.db.query(func.count(Expense.id))
        items_q = self.db.query(Expense)
        if self.tenant_id:
            count_q = count_q.filter(Expense.tenant_id == self.tenant_id)
            items_q = items_q.filter(Expense.tenant_id == self.tenant_id)
        total = count_q.scalar() or 0
        items = (
            items_q
            .order_by(Expense.expense_date.desc(), Expense.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return items, total
