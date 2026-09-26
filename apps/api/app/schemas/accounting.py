from datetime import date, datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.schemas.common import MoneyStr


class AccountCreate(BaseModel):
    code: str = Field(..., pattern=r"^[0-9.]{1,25}$")
    name: str = Field(..., min_length=2, max_length=255)
    account_type: str = Field(..., pattern="^(asset|liability|equity|income|expense)$")
    parent_id: UUID | None = None


class AccountRead(BaseModel):
    id: UUID
    tenant_id: UUID
    parent_id: UUID | None
    code: str
    name: str
    account_type: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JournalLineCreate(BaseModel):
    account_id: UUID
    debit: Decimal = Field(default=Decimal("0.00"), ge=0)
    credit: Decimal = Field(default=Decimal("0.00"), ge=0)
    memo: str | None = None

    @model_validator(mode="after")
    def validate_line_purity(self):
        if self.debit == 0 and self.credit == 0:
            raise ValueError("La línea no puede tener débito y crédito en cero.")
        if self.debit > 0 and self.credit > 0:
            raise ValueError("Una línea no puede contener débito y crédito simultáneamente.")
        return self


class JournalLineRead(BaseModel):
    id: UUID
    account_id: UUID
    debit: MoneyStr
    credit: MoneyStr
    memo: str | None

    model_config = ConfigDict(from_attributes=True)


class JournalEntryCreate(BaseModel):
    entry_date: date
    description: str = Field(..., min_length=3)
    lines: list[JournalLineCreate] = Field(..., min_length=2)

    @model_validator(mode="after")
    def validate_double_entry(self):
        total_debit = sum(line.debit for line in self.lines)
        total_credit = sum(line.credit for line in self.lines)
        if total_debit != total_credit:
            raise ValueError(
                f"Asiento desbalanceado: Total Débito ({total_debit}) != Total Crédito ({total_credit})."
            )
        return self


class JournalEntryRead(BaseModel):
    id: UUID
    tenant_id: UUID
    entry_date: date
    description: str
    status: str
    total_debit: MoneyStr
    total_credit: MoneyStr
    lines: list[JournalLineRead]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
