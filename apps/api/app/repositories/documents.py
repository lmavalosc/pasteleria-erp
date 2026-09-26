import uuid
from sqlalchemy.orm import Session
from app.models.operations import Document


class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, document: Document) -> Document:
        self.db.add(document)
        self.db.flush()
        return document

    def get_by_id(self, document_id: uuid.UUID) -> Document | None:
        return self.db.query(Document).filter(Document.id == document_id).first()
