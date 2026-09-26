from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class DocumentRead(BaseModel):
    id: UUID
    tenant_id: UUID
    filename: str
    mime_type: str
    size_bytes: int
    checksum_sha256: str | None
    storage_provider: str
    storage_uri: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
