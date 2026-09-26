from datetime import date, datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.common import MoneyStr


class DteEmissionRequest(BaseModel):
    dte_type: int = Field(..., description="Tipo DTE SII (33, 34, 61, etc.)")
    folio: int = Field(..., gt=0)
    issue_date: date
    receiver_rut: str = Field(..., pattern=r"^[0-9]+-[0-9kK]$")
    receiver_name: str
    subtotal: Decimal = Field(default=Decimal("0.00"), ge=0)
    tax_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    total: Decimal = Field(..., gt=0)
    currency: str = Field(default="CLP", pattern="^(CLP|USD)$")


class DteInvoiceRead(BaseModel):
    id: UUID
    tenant_id: UUID
    dte_type: str
    folio: int
    issue_date: date
    status: str
    currency: str
    recipient_rut: str | None
    recipient_name: str | None
    total: MoneyStr
    sii_receipt_uri: str | None
    sii_track_id: str | None
    emitted_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
