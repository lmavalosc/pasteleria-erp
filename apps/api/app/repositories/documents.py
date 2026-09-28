import uuid
from sqlalchemy.orm import Session
from app.models.entities import Document


class DocumentRepository:
    def __init__(self, db: Session, tenant_id: uuid.UUID | None = None):
        self.db = db
        self.tenant_id = tenant_id

    def create(self, document: Document) -> Document:
        self.db.add(document)
        self.db.flush()
        return document

    def get_by_id(self, document_id: uuid.UUID) -> Document | None:
        q = self.db.query(Document).filter(Document.id == document_id)
        if self.tenant_id:
            q = q.filter(Document.tenant_id == self.tenant_id)
        return q.first()
