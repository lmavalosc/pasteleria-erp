from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, File, Form, Header, Query, UploadFile
from fastapi.responses import FileResponse

from app.api.deps import DbTenant, TenantId
from app.schemas.documents import DocumentPage, DocumentRead
from app.services import documents as documents_service

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=DocumentPage)
async def list_documents(
    db: DbTenant,
    tenant_id: TenantId,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    return documents_service.list_documents(db, tenant_id, page, page_size)


@router.post("", response_model=DocumentRead, status_code=201)
async def create_document(
    db: DbTenant,
    tenant_id: TenantId,
    file: UploadFile = File(...),
    filename: Annotated[str | None, Form()] = None,
    mime_type: Annotated[str | None, Form()] = None,
    checksum_sha256: Annotated[str | None, Form()] = None,
    idempotency_key: Annotated[str | None, Header()] = None,
):
    _ = idempotency_key
    return await documents_service.create_document(
        db=db,
        tenant_id=tenant_id,
        file=file,
        filename=filename,
        mime_type=mime_type,
        checksum_sha256=checksum_sha256,
    )


@router.post("/upload", response_model=DocumentRead, status_code=201, include_in_schema=False)
async def upload_document_alias(
    db: DbTenant,
    tenant_id: TenantId,
    file: UploadFile = File(...),
    filename: Annotated[str | None, Form()] = None,
    mime_type: Annotated[str | None, Form()] = None,
    checksum_sha256: Annotated[str | None, Form()] = None,
    idempotency_key: Annotated[str | None, Header()] = None,
):
    return await create_document(
        db=db,
        tenant_id=tenant_id,
        file=file,
        filename=filename,
        mime_type=mime_type,
        checksum_sha256=checksum_sha256,
        idempotency_key=idempotency_key,
    )


@router.get("/{document_id}", response_model=DocumentRead)
def get_document(
    db: DbTenant,
    tenant_id: TenantId,
    document_id: UUID,
):
    return documents_service.get_document(db, tenant_id, document_id)


@router.get("/{document_id}/content")
def get_document_content(
    db: DbTenant,
    tenant_id: TenantId,
    document_id: UUID,
):
    path, doc = documents_service.get_document_file(db, tenant_id, document_id)
    return FileResponse(
        path=path,
        media_type=doc.mime_type,
        filename=doc.filename,
    )
