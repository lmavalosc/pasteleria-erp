import uuid
from decimal import Decimal
from datetime import date, datetime
from sqlalchemy import Text, Date, Numeric, Boolean, ForeignKey, CheckConstraint, UniqueConstraint, Index, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TenantMixin, TimestampMixin, CreatedAtMixin


class AccountingAccount(Base, TenantMixin, TimestampMixin):
    __tablename__ = "accounting_accounts"
    __table_args__ = (
        CheckConstraint(
            "account_type IN ('asset', 'liability', 'equity', 'income', 'expense')",
            name="chk_accounting_accounts_type",
        ),
        CheckConstraint("code ~ '^[0-9.]{1,25}$'", name="accounting_accounts_code_format"),
        UniqueConstraint("tenant_id", "code", name="uq_accounting_accounts_tenant_code"),
        Index("idx_accounting_accounts_tenant", "tenant_id"),
        Index("idx_accounting_accounts_type", "tenant_id", "account_type"),
        Index("idx_accounting_accounts_active", "tenant_id", "is_active"),
        Index("idx_accounting_accounts_parent", "parent_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounting_accounts.id", ondelete="SET NULL"),
        nullable=True,
    )
    code: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    account_type: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    parent: Mapped["AccountingAccount | None"] = relationship(
        "AccountingAccount", remote_side=[id], back_populates="children"
    )
    children: Mapped[list["AccountingAccount"]] = relationship(
        "AccountingAccount", back_populates="parent"
    )
    journal_lines: Mapped[list["JournalLine"]] = relationship(
        "JournalLine", back_populates="account"
    )


class JournalEntry(Base, TenantMixin, TimestampMixin):
    __tablename__ = "journal_entries"
    __table_args__ = (
        CheckConstraint("status IN ('draft', 'posted', 'voided')", name="chk_journal_entries_status"),
        CheckConstraint("total_debit >= 0", name="journal_entries_total_debit_non_negative"),
        CheckConstraint("total_credit >= 0", name="journal_entries_total_credit_non_negative"),
        CheckConstraint("total_debit = total_credit", name="journal_entries_balance"),
        Index("idx_journal_entries_tenant_date", "tenant_id", "entry_date"),
        Index("idx_journal_entries_tenant_status", "tenant_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    entry_date: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, default="draft", nullable=False)
    total_debit: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0.00"), nullable=False)
    total_credit: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0.00"), nullable=False)
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    lines: Mapped[list["JournalLine"]] = relationship(
        "JournalLine", back_populates="entry", cascade="all, delete-orphan"
    )


class JournalLine(Base, TenantMixin, CreatedAtMixin):
    __tablename__ = "journal_lines"
    __table_args__ = (
        CheckConstraint("debit >= 0", name="journal_lines_debit_non_negative"),
        CheckConstraint("credit >= 0", name="journal_lines_credit_non_negative"),
        CheckConstraint("NOT (debit = 0 AND credit = 0)", name="journal_lines_not_both_zero"),
        CheckConstraint("NOT (debit > 0 AND credit > 0)", name="journal_lines_not_both_positive"),
        Index("idx_journal_lines_tenant", "tenant_id"),
        Index("idx_journal_lines_entry", "entry_id"),
        Index("idx_journal_lines_account", "account_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    entry_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("journal_entries.id", ondelete="CASCADE"),
        nullable=False,
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounting_accounts.id", ondelete="RESTRICT"),
        nullable=False,
    )
    debit: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0.00"), nullable=False)
    credit: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0.00"), nullable=False)
    memo: Mapped[str | None] = mapped_column(Text, nullable=True)

    entry: Mapped["JournalEntry"] = relationship("JournalEntry", back_populates="lines")
    account: Mapped["AccountingAccount"] = relationship("AccountingAccount", back_populates="journal_lines")
