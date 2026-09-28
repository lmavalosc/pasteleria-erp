import uuid
from typing import Any

from app.integrations.sii.port import SIIClientPort, SIIDtePayload, SIIEmissionResult


class StubSIIClient(SIIClientPort):
    """Stub determinista para desarrollo y tests en Fase 1."""

    def emit_dte(self, payload: Any) -> SIIEmissionResult:
        dte_type = getattr(payload, "dte_type", None) or "33"
        folio = getattr(payload, "folio", None) or 1
        fake_track_id = f"STUB-{uuid.uuid4().hex[:8]}-TRACK-{dte_type}-{folio}"
        return SIIEmissionResult(
            track_id=fake_track_id,
            sii_receipt_uri=None,
            status="issued",
        )

    def get_track_status(self, track_id: str) -> str:
        return "issued"
