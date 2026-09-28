import uuid
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.core.errors import DomainError, DomainException
from app.integrations.sii.factory import get_sii_adapter
from app.integrations.sii.port import SIIClientPort, SIIDtePayload
from app.models.entities import DteInvoice
from app.repositories.invoicing import InvoicingRepository
from app.schemas.invoicing import (
    DteEmissionRequest,
    DteInvoiceCreate,
    DteInvoicePage,
    DteInvoiceRead,
)
from app.services.common import build_page_meta, decimal_to_str, paginate, parse_money


def list_dte_invoices(
    db: Session,
    tenant_id: UUID,
    page: int,
    page_size: int,
) -> DteInvoicePage:
    stmt = (
        select(DteInvoice)
        .where(DteInvoice.tenant_id == tenant_id)
        .order_by(DteInvoice.issue_date.desc(), DteInvoice.created_at.desc())
    )

    items, total = paginate(db, stmt, page, page_size)
    meta = build_page_meta(total=total, page=page, page_size=page_size)

    return DteInvoicePage(
        items=[_to_dte_read(item) for item in items],
        **meta.model_dump(),
    )


def get_dte_invoice(
    db: Session,
    tenant_id: UUID,
    dte_id: UUID,
) -> DteInvoiceRead:
    obj = _get_dte_obj(db, tenant_id, dte_id)
    return _to_dte_read(obj)


def create_dte_invoice(
    db: Session,
    tenant_id: UUID,
    payload: DteInvoiceCreate,
) -> DteInvoiceRead:
    # Si viene folio, validar unicidad; si no viene, asignar folio automáticamente
    folio = payload.folio
    if folio is not None:
        exists = db.scalar(
            select(DteInvoice.id).where(
                DteInvoice.tenant_id == tenant_id,
                DteInvoice.dte_type == str(payload.dte_type),
                DteInvoice.folio == folio,
            )
        )

        if exists:
            raise DomainError(
                status_code=409,
                title="DTE duplicado",
                detail=(
                    f"Ya existe un DTE tipo {payload.dte_type} "
                    f"con folio {folio} para este tenant."
                ),
                code="DTE_DUPLICATE",
            )
    else:
        folio = _claim_atomic_folio(db, tenant_id, str(payload.dte_type))

    # Cuantización de montos
    subtotal_val = int(parse_money(payload.subtotal)) if payload.subtotal else None
    tax_val = int(parse_money(payload.tax_amount)) if payload.tax_amount else None
    total_val = int(parse_money(payload.total))

    obj = DteInvoice(
        tenant_id=tenant_id,
        dte_type=str(payload.dte_type),
        folio=folio,
        issue_date=payload.issue_date,
        status="draft",
        currency=payload.currency,
        recipient_rut=payload.recipient_rut,
        recipient_name=payload.recipient_name,
        subtotal=subtotal_val,
        tax_amount=tax_val,
        total=total_val,
    )

    db.add(obj)
    db.flush()
    db.refresh(obj)

    return _to_dte_read(obj)


def issue_dte_invoice(
    db: Session,
    tenant_id: UUID,
    dte_id: UUID,
) -> DteInvoiceRead:
    obj = _get_dte_obj(db, tenant_id, dte_id)

    if obj.status != "draft":
        raise DomainError(
            status_code=409,
            title="DTE no emitible",
            detail="Solo se pueden emitir DTE en estado draft.",
            code="DTE_NOT_DRAFT",
        )

    adapter = get_sii_adapter()
    result = adapter.emit_dte(obj)

    obj.status = (
        result.status
        if result.status in {"issued", "accepted", "rejected"}
        else "issued"
    )

    obj.sii_track_id = result.track_id
    obj.sii_receipt_uri = getattr(result, "receipt_uri", None) or getattr(result, "sii_receipt_uri", None)
    obj.emitted_at = datetime.now(timezone.utc)

    db.flush()
    db.refresh(obj)

    return _to_dte_read(obj)


def _get_dte_obj(
    db: Session,
    tenant_id: UUID,
    dte_id: UUID,
) -> DteInvoice:
    obj = db.scalar(
        select(DteInvoice).where(
            DteInvoice.tenant_id == tenant_id,
            DteInvoice.id == dte_id,
        )
    )

    if not obj:
        raise DomainError(
            status_code=404,
            title="DTE no encontrado",
            detail="El DTE solicitado no existe para este tenant.",
            code="DTE_NOT_FOUND",
        )

    return obj


def _to_dte_read(obj: DteInvoice) -> DteInvoiceRead:
    return DteInvoiceRead(
        id=obj.id,
        tenant_id=obj.tenant_id,
        dte_type=obj.dte_type,
        folio=obj.folio,
        issue_date=obj.issue_date,
        status=obj.status,
        currency=obj.currency,
        recipient_rut=obj.recipient_rut,
        subtotal=f"{Decimal(str(obj.subtotal)):.2f}" if obj.subtotal is not None else None,
        tax_amount=f"{Decimal(str(obj.tax_amount)):.2f}" if obj.tax_amount is not None else None,
        total=f"{Decimal(str(obj.total)):.2f}",
        sii_receipt_uri=obj.sii_receipt_uri,
        sii_track_id=obj.sii_track_id,
        emitted_at=obj.emitted_at,
        created_at=obj.created_at,
        updated_at=obj.updated_at,
    )


def _claim_atomic_folio(db: Session, tenant_id: UUID, dte_type: str) -> int:
    """
    Reclama folio atómico con bloqueo pesimista en tabla folio_ranges.
    """
    row = db.execute(
        text("""
            SELECT id, next_folio, range_end
            FROM folio_ranges
            WHERE tenant_id = :tid
              AND dte_type = :dtype
              AND is_active = TRUE
              AND next_folio <= range_end
            ORDER BY range_start
            LIMIT 1
            FOR UPDATE
        """),
        {"tid": str(tenant_id), "dtype": dte_type},
    ).fetchone()

    if not row:
        max_folio = db.execute(
            text("""
                SELECT COALESCE(MAX(folio), 0)
                FROM dte_invoices
                WHERE tenant_id = :tid AND dte_type = :dtype
            """),
            {"tid": str(tenant_id), "dtype": dte_type},
        ).scalar() or 0
        return int(max_folio) + 1

    folio = row.next_folio
    new_next = folio + 1
    is_exhausted = new_next > row.range_end

    db.execute(
        text("""
            UPDATE folio_ranges
            SET next_folio = :new_next,
                is_active = :active
            WHERE id = :rid
        """),
        {"new_next": new_next, "active": not is_exhausted, "rid": row.id},
    )
    return int(folio)


# =========================================================================
# Clase InvoicingService para retrocompatibilidad con router y tests Fase 1
# =========================================================================
class InvoicingService:
    def __init__(self, repo: InvoicingRepository, sii_client: SIIClientPort | None = None):
        self.repo = repo
        self.sii_client = sii_client or get_sii_adapter()

    def emit_dte(
        self, tenant_id: UUID, emitter_rut: str, data: DteEmissionRequest
    ) -> DteInvoice:
        str_dte_type = str(data.dte_type)

        if data.folio:
            if self.repo.get_by_type_and_folio(str_dte_type, data.folio):
                raise DomainException(
                    "DTE ya registrado",
                    f"El folio {data.folio} para el tipo DTE {data.dte_type} ya existe.",
                    409,
                )
            folio = data.folio
        else:
            folio = _claim_atomic_folio(self.repo.db, tenant_id, str_dte_type)

        if data.currency == "CLP":
            net_val = int(Decimal(str(data.subtotal or 0)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
            tax_val = int(Decimal(str(data.tax_amount or 0)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
            tot_val = int(Decimal(str(data.total)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        else:
            net_val = int(Decimal(str(data.subtotal or 0)))
            tax_val = int(Decimal(str(data.tax_amount or 0)))
            tot_val = int(Decimal(str(data.total)))

        sii_payload = SIIDtePayload(
            dte_type=str_dte_type,
            folio=folio,
            emitter_rut=emitter_rut,
            receiver_rut=data.receiver_rut or "",
            net_amount=Decimal(net_val),
            tax_amount=Decimal(tax_val),
            total_amount=Decimal(tot_val),
        )
        sii_res = self.sii_client.emit_dte(sii_payload)

        invoice = DteInvoice(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            dte_type=str_dte_type,
            folio=folio,
            issue_date=data.issue_date,
            status=sii_res.status,
            currency=data.currency,
            recipient_rut=data.receiver_rut,
            recipient_name=data.receiver_name,
            subtotal=net_val,
            tax_amount=tax_val,
            total=tot_val,
            sii_receipt_uri=getattr(sii_res, "receipt_uri", None) or getattr(sii_res, "sii_receipt_uri", None),
            sii_track_id=sii_res.track_id,
            emitted_at=datetime.now(timezone.utc),
        )
        return self.repo.create_invoice(invoice)
