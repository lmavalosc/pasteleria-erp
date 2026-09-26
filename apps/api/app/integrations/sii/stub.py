import uuid
from app.integrations.sii.port import SIIClientPort, SIIDtePayload, SIIEmissionResult


class StubSIIClient(SIIClientPort):
    """Stub determinista para desarrollo y tests en Fase 1."""

    def emit_dte(self, payload: SIIDtePayload) -> SIIEmissionResult:
        fake_track_id = f"TRACK-{payload.dte_type}-{payload.folio}-{uuid.uuid4().hex[:6].upper()}"
        return SIIEmissionResult(
            track_id=fake_track_id,
            sii_receipt_uri=f"https://sii-sandbox.local/receipts/{fake_track_id}.xml",
            status="accepted",
        )

    def get_track_status(self, track_id: str) -> str:
        return "accepted"
