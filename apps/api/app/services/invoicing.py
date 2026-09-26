import uuid
from datetime import datetime, timezone
from app.core.errors import DomainException
from app.integrations.sii.port import SIIClientPort, SIIDtePayload
from app.models.operations import DteInvoice
from app.repositories.invoicing import InvoicingRepository
from app.schemas.invoicing import DteEmissionRequest


class InvoicingService:
    def __init__(self, repo: InvoicingRepository, sii_client: SIIClientPort):
        self.repo = repo
        self.sii_client = sii_client

    def emit_dte(
        self, tenant_id: uuid.UUID, emitter_rut: str, data: DteEmissionRequest
    ) -> DteInvoice:
        str_dte_type = str(data.dte_type)
        if self.repo.get_by_type_and_folio(str_dte_type, data.folio):
            raise DomainException(
                "DTE ya registrado",
                f"El folio {data.folio} para el tipo DTE {data.dte_type} ya existe.",
                409,
            )

        # 1. Llamada a la integración SII aislada
        sii_payload = SIIDtePayload(
            dte_type=data.dte_type,
            folio=data.folio,
            emitter_rut=emitter_rut,
            receiver_rut=data.receiver_rut,
            net_amount=data.subtotal,
            tax_amount=data.tax_amount,
            total_amount=data.total,
        )
        sii_res = self.sii_client.emit_dte(sii_payload)

        # 2. Persistencia relacional
        invoice = DteInvoice(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            dte_type=str_dte_type,
            folio=data.folio,
            issue_date=data.issue_date,
            status=sii_res.status,
            currency=data.currency,
            recipient_rut=data.receiver_rut,
            recipient_name=data.receiver_name,
            subtotal=data.subtotal,
            tax_amount=data.tax_amount,
            total=data.total,
            sii_receipt_uri=sii_res.sii_receipt_uri,
            sii_track_id=sii_res.track_id,
            emitted_at=datetime.now(timezone.utc),
        )
        return self.repo.create_invoice(invoice)
