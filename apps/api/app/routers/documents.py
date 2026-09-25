from fastapi import APIRouter, HTTPException, status, UploadFile, File, Depends
from fastapi.responses import FileResponse
from app.schemas.core_models import DocumentResponse
from app.core.deps import TenantContext
from app.core.deps import get_current_context
from app.core.config import settings
from app.storage.local_driver import storage_driver
from app.services.document_service import document_store
import os

router = APIRouter(prefix="/v1/documents", tags=["documents"])

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/webp"
}

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    context: TenantContext = Depends(get_current_context)
):
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de archivo no permitido: {file.content_type}. Tipos admitidos: PDF, PNG, JPEG, WEBP."
        )

    content = await file.read()
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"El archivo supera el límite de {settings.MAX_UPLOAD_SIZE_MB}MB permitidos."
        )

    storage_uri, sha256_checksum, file_size = storage_driver.save(
        tenant_id=context.tenant_id,
        filename=file.filename or "archivo",
        content=content
    )

    doc = document_store.save_metadata(
        tenant_id=context.tenant_id,
        filename_original=file.filename or "archivo",
        mime_type=file.content_type,
        file_size_bytes=file_size,
        storage_uri=storage_uri,
        checksum_sha256=sha256_checksum,
        uploaded_by_user_id=context.user_id
    )

    return DocumentResponse(**doc)

@router.get("/{id}", response_model=DocumentResponse)
def get_document_metadata(
    id: str,
    context: TenantContext = Depends(get_current_context)
):
    doc = document_store.get_by_id(id, context.tenant_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento no encontrado o no pertenece a la empresa actual."
        )
    return DocumentResponse(**doc)

@router.get("/{id}/download")
def download_document(
    id: str,
    context: TenantContext = Depends(get_current_context)
):
    doc = document_store.get_by_id(id, context.tenant_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento no encontrado o no pertenece a la empresa actual."
        )

    abs_path = storage_driver.get_absolute_path(doc["storage_uri"])
    if not os.path.exists(abs_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo binario físico no disponible."
        )

    return FileResponse(
        path=abs_path,
        media_type=doc["mime_type"],
        filename=doc["filename_original"]
    )
