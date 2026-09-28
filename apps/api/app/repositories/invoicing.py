import uuid
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.entities import DteInvoice


class InvoicingRepository:
    def __init__(self, db: Session, tenant_id: uuid.UUID | None = None):
        self.db = db
        self.tenant_id = tenant_id

    def create_invoice(self, invoice: DteInvoice) -> DteInvoice:
        self.db.add(invoice)
        self.db.flush()
        return invoice

    def get_by_type_and_folio(self, dte_type: str, folio: int) -> DteInvoice | None:
        q = self.db.query(DteInvoice).filter(DteInvoice.dte_type == dte_type, DteInvoice.folio == folio)
        if self.tenant_id:
            q = q.filter(DteInvoice.tenant_id == self.tenant_id)
        return q.first()

    def list_paginated(self, offset: int, limit: int) -> tuple[list[DteInvoice], int]:
        count_q = self.db.query(func.count(DteInvoice.id))
        items_q = self.db.query(DteInvoice)
        if self.tenant_id:
            count_q = count_q.filter(DteInvoice.tenant_id == self.tenant_id)
            items_q = items_q.filter(DteInvoice.tenant_id == self.tenant_id)
        total = count_q.scalar() or 0
        items = (
            items_q
            .order_by(DteInvoice.issue_date.desc(), DteInvoice.folio.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return items, total
