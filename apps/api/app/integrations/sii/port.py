from decimal import Decimal
from typing import Protocol
from pydantic import BaseModel


class SIIDtePayload(BaseModel):
    dte_type: int
    folio: int
    emitter_rut: str
    receiver_rut: str
    net_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal


class SIIEmissionResult(BaseModel):
    track_id: str
    sii_receipt_uri: str
    status: str  # 'accepted', 'rejected', 'pending'


class SIIClientPort(Protocol):
    def emit_dte(self, payload: SIIDtePayload) -> SIIEmissionResult:
        """Emite y firma el DTE ante el SII."""
        ...

    def get_track_status(self, track_id: str) -> str:
        """Consulta el estado del envío mediante su Track ID."""
        ...
