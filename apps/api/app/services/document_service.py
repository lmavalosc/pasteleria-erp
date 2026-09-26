import uuid
from datetime import datetime


class DocumentStore:
    def __init__(self):
        self.documents: dict[str, dict] = {} # id -> doc

    def save_metadata(
        self,
        tenant_id: str,
        filename_original: str,
        mime_type: str,
        file_size_bytes: int,
        storage_uri: str,
        checksum_sha256: str,
        uploaded_by_user_id: str
    ) -> dict:
        doc_id = str(uuid.uuid4())
        doc = {
            "id": doc_id,
            "tenant_id": tenant_id,
            "filename_original": filename_original,
            "mime_type": mime_type,
            "file_size_bytes": file_size_bytes,
            "storage_uri": storage_uri,
            "checksum_sha256": checksum_sha256,
            "uploaded_by_user_id": uploaded_by_user_id,
            "created_at": datetime.utcnow().isoformat()
        }
        self.documents[doc_id] = doc
        return doc

    def get_by_id(self, doc_id: str, tenant_id: str) -> dict | None:
        doc = self.documents.get(doc_id)
        if doc and doc["tenant_id"] == tenant_id:
            return doc
        return None

document_store = DocumentStore()
