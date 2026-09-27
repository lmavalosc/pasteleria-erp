from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Any, Literal
from uuid import UUID

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    StringConstraints,
    model_validator,
)

from app.schemas.common import Page

Currency = Literal["CLP", "USD"]
DteStatus = Literal["draft", "issued", "accepted", "rejected", "annulled"]

DteType = Literal[
    "33",
    "34",
    "39",
    "41",
    "43",
    "45",
    "46",
    "52",
    "56",
    "61",
    "110",
    "111",
    "112",
]


def _coerce_decimal_str(v: Any) -> str:
    if isinstance(v, (int, float, Decimal)):
        return f"{Decimal(str(v)):.2f}"
    return str(v)


NonNegativeDecimalStr = Annotated[
    str,
    BeforeValidator(_coerce_decimal_str),
    StringConstraints(pattern=r"^\d+(\.\d{1,2})?$"),
]


class DteInvoiceCreate(BaseModel):
    dte_type: DteType | str
    folio: int = Field(gt=0)
    issue_date: date
    currency: Currency = "CLP"
    recipient_rut: str | None = None
    recipient_name: str | None = None
    subtotal: NonNegativeDecimalStr | None = None
    tax_amount: NonNegativeDecimalStr | None = None
    total: NonNegativeDecimalStr

    @model_validator(mode="before")
    @classmethod
    def map_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "dte_type" in data:
                data["dte_type"] = str(data["dte_type"])
            if "receiver_rut" in data and "recipient_rut" not in data:
                data["recipient_rut"] = data["receiver_rut"]
            if "receiver_name" in data and "recipient_name" not in data:
                data["recipient_name"] = data["receiver_name"]
        return data

    @property
    def receiver_rut(self) -> str | None:
        return self.recipient_rut

    @property
    def receiver_name(self) -> str | None:
        return self.recipient_name



class DteInvoiceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    dte_type: str
    folio: int
    issue_date: date
    status: DteStatus | str
    currency: Currency | str
    recipient_rut: str | None = None
    recipient_name: str | None = None
    subtotal: NonNegativeDecimalStr | None = None
    tax_amount: NonNegativeDecimalStr | None = None
    total: NonNegativeDecimalStr
    sii_receipt_uri: str | None = None
    sii_track_id: str | None = None
    emitted_at: datetime | None = None
    created_at: datetime
    updated_at: datetime | None = None


class DteInvoicePage(Page[DteInvoiceRead]):
    pass


# Alias para retrocompatibilidad
DteEmissionRequest = DteInvoiceCreate
