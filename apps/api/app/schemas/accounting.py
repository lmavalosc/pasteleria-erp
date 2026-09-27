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

AccountType = Literal["asset", "liability", "equity", "income", "expense"]
JournalStatus = Literal["draft", "posted", "voided"]


def _coerce_decimal_str(v: Any) -> str:
    if isinstance(v, (int, float, Decimal)):
        return f"{Decimal(str(v)):.2f}"
    return str(v)


NonNegativeDecimalStr = Annotated[
    str,
    BeforeValidator(_coerce_decimal_str),
    StringConstraints(pattern=r"^\d+(\.\d{1,2})?$"),
]


class AccountingAccountBase(BaseModel):
    code: str = Field(pattern=r"^[0-9.]{1,25}$")
    name: str = Field(min_length=1, max_length=200)
    account_type: AccountType
    parent_id: UUID | None = None


class AccountingAccountCreate(AccountingAccountBase):
    pass


class AccountingAccountUpdate(BaseModel):
    code: str | None = Field(default=None, pattern=r"^[0-9.]{1,25}$")
    name: str | None = Field(default=None, min_length=1, max_length=200)
    account_type: AccountType | None = None
    is_active: bool | None = None


class AccountingAccountRead(AccountingAccountBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None


class AccountingAccountPage(Page[AccountingAccountRead]):
    pass


class JournalLineBase(BaseModel):
    account_id: UUID
    debit: NonNegativeDecimalStr = "0.00"
    credit: NonNegativeDecimalStr = "0.00"
    memo: str | None = None

    @model_validator(mode="after")
    def validate_line_purity(self):
        d = Decimal(self.debit)
        c = Decimal(self.credit)
        if d == 0 and c == 0:
            raise ValueError("La línea no puede tener débito y crédito en cero.")
        if d > 0 and c > 0:
            raise ValueError("Una línea no puede contener débito y crédito simultáneamente.")
        return self


class JournalLineCreate(JournalLineBase):
    pass


class JournalLineRead(JournalLineBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    entry_id: UUID | None = None
    created_at: datetime | None = None


class JournalEntryBase(BaseModel):
    entry_date: date
    description: str = Field(min_length=1)


class JournalEntryCreate(JournalEntryBase):
    lines: list[JournalLineCreate] = Field(min_length=2)

    @model_validator(mode="after")
    def validate_double_entry(self):
        total_debit = sum(Decimal(line.debit) for line in self.lines)
        total_credit = sum(Decimal(line.credit) for line in self.lines)
        if total_debit != total_credit:
            raise ValueError(
                f"Asiento desbalanceado: Total Débito ({total_debit}) != Total Crédito ({total_credit})."
            )
        return self


class JournalEntryRead(JournalEntryBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    status: JournalStatus | str
    lines: list[JournalLineRead]
    total_debit: NonNegativeDecimalStr
    total_credit: NonNegativeDecimalStr
    posted_at: datetime | None = None
    created_at: datetime
    updated_at: datetime | None = None


class JournalEntryPage(Page[JournalEntryRead]):
    pass


# Aliases para retrocompatibilidad
AccountCreate = AccountingAccountCreate
AccountRead = AccountingAccountRead
