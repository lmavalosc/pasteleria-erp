import uuid
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.operations import Expense


class ExpenseRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, expense: Expense) -> Expense:
        self.db.add(expense)
        self.db.flush()
        return expense

    def get_by_id(self, expense_id: uuid.UUID) -> Expense | None:
        return self.db.query(Expense).filter(Expense.id == expense_id).first()

    def list_paginated(self, offset: int, limit: int) -> tuple[list[Expense], int]:
        total = self.db.query(func.count(Expense.id)).scalar() or 0
        items = (
            self.db.query(Expense)
            .order_by(Expense.expense_date.desc(), Expense.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return items, total
