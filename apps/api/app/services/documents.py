import hashlib
import uuid
from fastapi import UploadFile
from app.core.config import settings
from app.core.errors import DomainException
from app.models.operations import Document
from app.repositories.documents import DocumentRepository


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

        # Directorio aislado por tenant
        tenant_dir = settings.STORAGE_DIR / str(tenant_id)
        tenant_dir.mkdir(parents=True, exist_ok=True)

        doc_id = uuid.uuid4()
        dest_filename = f"{doc_id}_{file.filename}"
        dest_path = tenant_dir / dest_filename

        hasher = hashlib.sha256()
        total_bytes = 0

        # Guardado en streaming para optimizar uso de memoria
        with dest_path.open("wb") as buffer:
            while chunk := await file.read(1024 * 1024):  # 1MB
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
