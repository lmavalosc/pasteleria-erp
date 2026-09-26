from datetime import date, datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.common import MoneyStr


class ExpenseCreate(BaseModel):
    expense_date: date
    amount: Decimal = Field(..., gt=0, description="Monto en moneda de la transacción")
    currency: str = Field(default="CLP", pattern="^(CLP|USD)$")
    document_id: UUID | None = None
    description: str | None = None
    merchant: str | None = None


class ExpenseRead(BaseModel):
    id: UUID
    tenant_id: UUID
    expense_date: date
    amount: MoneyStr
    currency: str
    status: str
    document_id: UUID | None
    description: str | None
    merchant: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
