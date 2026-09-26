import uuid
from decimal import Decimal
from datetime import date, datetime
from sqlalchemy import (
    Text,
    Date,
    Numeric,
    Integer,
    BigInteger,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
    Index,
    DateTime,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TenantMixin, TimestampMixin, CreatedAtMixin


class Document(Base, TenantMixin, CreatedAtMixin):
    __tablename__ = "documents"
    __table_args__ = (
        CheckConstraint("size_bytes >= 0", name="documents_size_non_negative"),
        CheckConstraint(
            "checksum_sha256 IS NULL OR checksum_sha256 ~ '^[a-fA-F0-9]{64}$'",
            name="documents_checksum_format",
        ),
        CheckConstraint(
            "storage_provider IN ('local', 's3', 'gcs', 'azure')",
            name="chk_documents_storage_provider",
        ),
        Index("idx_documents_tenant", "tenant_id"),
        Index("idx_documents_created_at", "tenant_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    filename: Mapped[str] = mapped_column(Text, nullable=False)
    mime_type: Mapped[str] = mapped_column(Text, nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    checksum_sha256: Mapped[str | None] = mapped_column(Text, nullable=True)
    storage_provider: Mapped[str] = mapped_column(Text, default="local", nullable=False)
    storage_uri: Mapped[str] = mapped_column(Text, nullable=False)


class Expense(Base, TenantMixin, TimestampMixin):
    __tablename__ = "expenses"
    __table_args__ = (
        CheckConstraint("amount >= 0", name="expenses_amount_non_negative"),
        CheckConstraint("currency IN ('CLP', 'USD')", name="chk_expenses_currency"),
        CheckConstraint(
            "status IN ('draft', 'submitted', 'approved', 'paid', 'rejected')",
            name="chk_expenses_status",
        ),
        Index("idx_expenses_tenant_date", "tenant_id", "expense_date"),
        Index("idx_expenses_tenant_status", "tenant_id", "status"),
        Index("idx_expenses_document", "document_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    expense_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(Text, default="CLP", nullable=False)
    status: Mapped[str] = mapped_column(Text, default="draft", nullable=False)
    document_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    merchant: Mapped[str | None] = mapped_column(Text, nullable=True)

    document: Mapped["Document | None"] = relationship("Document")


class DteInvoice(Base, TenantMixin, TimestampMixin):
    __tablename__ = "dte_invoices"
    __table_args__ = (
        CheckConstraint(
            "dte_type IN ('33', '34', '39', '41', '43', '45', '46', '52', '56', '61', '110', '111', '112')",
            name="chk_dte_invoices_type",
        ),
        CheckConstraint("folio > 0", name="dte_invoices_folio_positive"),
        CheckConstraint("total >= 0", name="dte_invoices_total_non_negative"),
        CheckConstraint(
            "status IN ('draft', 'issued', 'accepted', 'rejected', 'annulled')",
            name="chk_dte_invoices_status",
        ),
        CheckConstraint("currency IN ('CLP', 'USD')", name="chk_dte_invoices_currency"),
        UniqueConstraint("tenant_id", "dte_type", "folio", name="uq_dte_invoices_tenant_type_folio"),
        Index("idx_dte_invoices_tenant_date", "tenant_id", "issue_date"),
        Index("idx_dte_invoices_tenant_status", "tenant_id", "status"),
        Index("idx_dte_invoices_tenant_type", "tenant_id", "dte_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    dte_type: Mapped[str] = mapped_column(Text, nullable=False)
    folio: Mapped[int] = mapped_column(Integer, nullable=False)
    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(Text, default="draft", nullable=False)
    currency: Mapped[str] = mapped_column(Text, default="CLP", nullable=False)
    recipient_rut: Mapped[str | None] = mapped_column(Text, nullable=True)
    recipient_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    subtotal: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    tax_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    total: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    sii_receipt_uri: Mapped[str | None] = mapped_column(Text, nullable=True)
    sii_track_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    emitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    items: Mapped[list["DteInvoiceItem"]] = relationship(
        "DteInvoiceItem", back_populates="invoice", cascade="all, delete-orphan"
    )


class DteInvoiceItem(Base, TenantMixin, CreatedAtMixin):
    __tablename__ = "dte_invoice_items"
    __table_args__ = (
        CheckConstraint("line_number > 0", name="dte_invoice_items_line_number_positive"),
        CheckConstraint("quantity >= 0", name="dte_invoice_items_quantity_non_negative"),
        CheckConstraint("unit_price >= 0", name="dte_invoice_items_unit_price_non_negative"),
        CheckConstraint("discount >= 0", name="dte_invoice_items_discount_non_negative"),
        CheckConstraint("tax_amount >= 0", name="dte_invoice_items_tax_amount_non_negative"),
        CheckConstraint("line_total >= 0", name="dte_invoice_items_line_total_non_negative"),
        UniqueConstraint("dte_invoice_id", "line_number", name="uq_dte_invoice_items_invoice_line"),
        Index("idx_dte_invoice_items_tenant", "tenant_id"),
        Index("idx_dte_invoice_items_invoice", "dte_invoice_id"),
        Index("idx_dte_invoice_items_account", "account_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    dte_invoice_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dte_invoices.id", ondelete="CASCADE"), nullable=False
    )
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 3), default=Decimal("1.000"), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    discount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0.00"), nullable=False)
    tax_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("19.00"), nullable=False)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0.00"), nullable=False)
    line_total: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    account_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounting_accounts.id", ondelete="SET NULL"), nullable=True
    )

    invoice: Mapped["DteInvoice"] = relationship("DteInvoice", back_populates="items")
