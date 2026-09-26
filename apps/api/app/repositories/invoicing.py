import uuid
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.operations import DteInvoice


class InvoicingRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_invoice(self, invoice: DteInvoice) -> DteInvoice:
        self.db.add(invoice)
        self.db.flush()
        return invoice

    def get_by_type_and_folio(self, dte_type: str, folio: int) -> DteInvoice | None:
        return (
            self.db.query(DteInvoice)
            .filter(DteInvoice.dte_type == dte_type, DteInvoice.folio == folio)
            .first()
        )

    def list_paginated(self, offset: int, limit: int) -> tuple[list[DteInvoice], int]:
        total = self.db.query(func.count(DteInvoice.id)).scalar() or 0
        items = (
            self.db.query(DteInvoice)
            .order_by(DteInvoice.issue_date.desc(), DteInvoice.folio.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return items, total
