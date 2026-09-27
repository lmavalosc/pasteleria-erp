from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Any, Literal
from uuid import UUID

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    StringConstraints,
)

from app.schemas.common import Page

Currency = Literal["CLP", "USD"]
ExpenseStatus = Literal["draft", "submitted", "approved", "paid", "rejected"]


def _coerce_decimal_str(v: Any) -> str:
    if isinstance(v, (int, float, Decimal)):
        return f"{Decimal(str(v)):.2f}"
    return str(v)


NonNegativeDecimalStr = Annotated[
    str,
    BeforeValidator(_coerce_decimal_str),
    StringConstraints(pattern=r"^\d+(\.\d{1,2})?$"),
]


class ExpenseCreate(BaseModel):
    expense_date: date
    amount: NonNegativeDecimalStr
    currency: Currency | str = "CLP"
    document_id: UUID | None = None
    description: str | None = None
    merchant: str | None = None


class ExpenseUpdate(BaseModel):
    status: ExpenseStatus | str | None = None
    document_id: UUID | None = None
    description: str | None = None
    merchant: str | None = None


class ExpenseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    expense_date: date
    amount: NonNegativeDecimalStr
    currency: Currency | str
    status: ExpenseStatus | str
    document_id: UUID | None = None
    description: str | None = None
    merchant: str | None = None
    created_at: datetime
    updated_at: datetime | None = None


class ExpensePage(Page[ExpenseRead]):
    pass
