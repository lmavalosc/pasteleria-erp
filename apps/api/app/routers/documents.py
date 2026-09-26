from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_db_with_tenant, get_tenant_id_from_header
from app.repositories.documents import DocumentRepository
from app.schemas.documents import DocumentRead
from app.services.documents import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: Annotated[UploadFile, File(...)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id_from_header)],
    db: Annotated[Session, Depends(get_db_with_tenant)],
):
    service = DocumentService(DocumentRepository(db))
    return await service.upload_document(tenant_id, file)
