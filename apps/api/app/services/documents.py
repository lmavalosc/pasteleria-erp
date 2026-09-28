import hashlib
import uuid
from pathlib import Path
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import DomainError, DomainException
from app.models.entities import Document
from app.repositories.documents import DocumentRepository
from app.schemas.documents import DocumentPage, DocumentRead
from app.services.common import build_page_meta, paginate


def list_documents(
    db: Session,
    tenant_id: UUID,
    page: int = 1,
    page_size: int = 20,
) -> DocumentPage:
    stmt = (
        select(Document)
        .where(Document.tenant_id == tenant_id)
        .order_by(Document.created_at.desc())
    )
    items, total = paginate(db, stmt, page, page_size)
    meta = build_page_meta(total=total, page=page, page_size=page_size)
    return DocumentPage(
        items=[DocumentRead.model_validate(doc) for doc in items],
        **meta.model_dump(),
    )


async def create_document(
    db: Session,
    tenant_id: UUID,
    file: UploadFile,
    filename: str | None = None,
    mime_type: str | None = None,
    checksum_sha256: str | None = None,
) -> DocumentRead:
    resolved_filename = filename or file.filename
    if not resolved_filename:
        raise DomainError(
            status_code=400,
            title="Nombre de archivo inválido",
            detail="El archivo proporcionado no tiene un nombre válido.",
            code="INVALID_FILENAME",
        )

    tenant_dir = settings.STORAGE_DIR / str(tenant_id)
    tenant_dir.mkdir(parents=True, exist_ok=True)

    doc_id = uuid.uuid4()
    dest_filename = f"{doc_id}_{resolved_filename}"
    dest_path = tenant_dir / dest_filename

    hasher = hashlib.sha256()
    total_bytes = 0

    with dest_path.open("wb") as buffer:
        while chunk := await file.read(1024 * 1024):  # 1MB
            total_bytes += len(chunk)
            hasher.update(chunk)
            buffer.write(chunk)

    calculated_checksum = hasher.hexdigest()

    doc = Document(
        id=doc_id,
        tenant_id=tenant_id,
        filename=resolved_filename,
        mime_type=mime_type or file.content_type or "application/octet-stream",
        size_bytes=total_bytes,
        checksum_sha256=calculated_checksum,
        storage_provider="local",
        storage_uri=str(dest_path),
    )
    db.add(doc)
    db.flush()
    db.refresh(doc)
    return DocumentRead.model_validate(doc)


def get_document(
    db: Session,
    tenant_id: UUID,
    document_id: UUID,
) -> DocumentRead:
    doc = db.scalar(
        select(Document).where(
            Document.tenant_id == tenant_id,
            Document.id == document_id,
        )
    )
    if not doc:
        raise DomainError(
            status_code=404,
            title="Documento no encontrado",
            detail=f"El documento con ID {document_id} no existe.",
            code="DOCUMENT_NOT_FOUND",
        )
    return DocumentRead.model_validate(doc)


def get_document_file(
    db: Session,
    tenant_id: UUID,
    document_id: UUID,
) -> tuple[str, Document]:
    doc = db.scalar(
        select(Document).where(
            Document.tenant_id == tenant_id,
            Document.id == document_id,
        )
    )
    if not doc:
        raise DomainError(
            status_code=404,
            title="Documento no encontrado",
            detail=f"El documento con ID {document_id} no existe.",
            code="DOCUMENT_NOT_FOUND",
        )

    file_path = Path(doc.storage_uri)
    if not file_path.exists():
        raise DomainError(
            status_code=404,
            title="Archivo no encontrado",
            detail="El archivo físico asociado al documento no existe en el almacenamiento.",
            code="FILE_NOT_FOUND",
        )
    return str(file_path), doc


# =========================================================================
# Clase DocumentService para retrocompatibilidad
# =========================================================================
class DocumentService:
    def __init__(self, repo: DocumentRepository):
        self.repo = repo

    async def upload_document(self, tenant_id: uuid.UUID, file: UploadFile) -> Document:
        if not file.filename:
            raise DomainException(
                "Nombre de archivo inválido",
                "El archivo proporcionado no tiene un nombre válido.",
                400,
            )

        tenant_dir = settings.STORAGE_DIR / str(tenant_id)
        tenant_dir.mkdir(parents=True, exist_ok=True)

        doc_id = uuid.uuid4()
        dest_filename = f"{doc_id}_{file.filename}"
        dest_path = tenant_dir / dest_filename

        hasher = hashlib.sha256()
        total_bytes = 0

        with dest_path.open("wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                total_bytes += len(chunk)
                hasher.update(chunk)
                buffer.write(chunk)

        doc = Document(
            id=doc_id,
            tenant_id=tenant_id,
            filename=file.filename,
            mime_type=file.content_type or "application/octet-stream",
            size_bytes=total_bytes,
            checksum_sha256=hasher.hexdigest(),
            storage_provider="local",
            storage_uri=str(dest_path),
        )
        return self.repo.create(doc)
