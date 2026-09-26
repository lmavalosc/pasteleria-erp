import uuid
from datetime import datetime

from app.schemas.core_models import DTECreateRequest, DTEState
from app.services.dte_provider import dte_provider


class DTEStore:
    def __init__(self):
        self.dtes: dict[str, dict] = {} # id -> dte
        # (tenant_id, tipo_dte) -> last_folio
        self.folios: dict[tuple, int] = {}

    def get_next_folio(self, tenant_id: str, tipo_dte: int) -> int:
        key = (tenant_id, tipo_dte)
        next_folio = self.folios.get(key, 0) + 1
        self.folios[key] = next_folio
        return next_folio

    def create(self, tenant_id: str, data: DTECreateRequest) -> dict:
        dte_id = str(uuid.uuid4())
        folio = data.folio if data.folio is not None else self.get_next_folio(tenant_id, data.tipo_dte)

        dte = {
            "id": dte_id,
            "tenant_id": tenant_id,
            "tipo_dte": data.tipo_dte,
            "folio": folio,
            "fecha_emision": data.fecha_emision,
            "emisor_rut": data.emisor_rut,
            "receptor_rut": data.receptor_rut,
            "receptor_razon_social": data.receptor_razon_social,
            "monto_neto": data.monto_neto,
            "monto_exento": data.monto_exento,
            "monto_iva": data.monto_iva,
            "monto_total": data.monto_total,
            "estado_sii": DTEState.DRAFT.value,
            "track_id_sii": None,
            "xml_payload_uri": None,
            "order_id": data.order_id,
            "created_at": datetime.utcnow().isoformat()
        }
        self.dtes[dte_id] = dte
        return dte

    def get_by_id(self, dte_id: str, tenant_id: str) -> dict | None:
        d = self.dtes.get(dte_id)
        if d and d["tenant_id"] == tenant_id:
            return d
        return None

    def list_dtes(
        self,
        tenant_id: str,
        tipo_dte: int | None = None,
        estado_sii: str | None = None,
        fecha_desde: str | None = None,
        fecha_hasta: str | None = None,
        page: int = 1,
        page_size: int = 20
    ) -> list[dict]:
        res = [d for d in self.dtes.values() if d["tenant_id"] == tenant_id]
        if tipo_dte:
            res = [d for d in res if d["tipo_dte"] == tipo_dte]
        if estado_sii:
            res = [d for d in res if d["estado_sii"] == estado_sii]
        if fecha_desde:
            res = [d for d in res if d["fecha_emision"] >= fecha_desde]
        if fecha_hasta:
            res = [d for d in res if d["fecha_emision"] <= fecha_hasta]

        res.sort(key=lambda x: (x["tipo_dte"], x["folio"]), reverse=True)
        start = (page - 1) * page_size
        return res[start:start + page_size]

    def emit(self, dte_id: str, tenant_id: str) -> dict:
        dte = self.get_by_id(dte_id, tenant_id)
        if not dte:
            raise ValueError("DTE no encontrado.")

        if dte["estado_sii"] in (DTEState.ACCEPTED_BY_SII.value, DTEState.SENT_TO_SII.value):
            return dte # Already emitted

        emission_result = dte_provider.emit_dte(dte)
        dte["track_id_sii"] = emission_result.get("track_id_sii")
        dte["estado_sii"] = emission_result.get("estado_sii", DTEState.ACCEPTED_BY_SII.value)
        dte["xml_payload_uri"] = emission_result.get("xml_payload_uri")
        return dte

dte_store = DTEStore()
