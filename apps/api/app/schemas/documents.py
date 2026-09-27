from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.common import Page


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    filename: str
    mime_type: str
    size_bytes: int
    checksum_sha256: str | None = None
    content_path: str | None = None
    storage_provider: str | None = "local"
    storage_uri: str
    created_at: datetime


class DocumentPage(Page[DocumentRead]):
    pass
