from fastapi import APIRouter, Depends
from typing import List, Optional
import uuid
from app.core.deps import get_current_context, TenantContext

router = APIRouter(prefix="/invoicing/dte", tags=["Tributario"])

@router.get("", response_model=List[dict])
def list_dtes(
    tipoDte: Optional[int] = None,
    estadoSii: Optional[str] = None,
    context: TenantContext = Depends(get_current_context)
):
    return [
        {
            "id": "55555555-5555-5555-5555-555555555555",
            "tenant_id": context.tenant_id,
            "tipo_dte": tipoDte or 39,
            "folio": 1042,
            "fecha_emision": "2026-09-25",
            "emisor_rut": "76.123.456-7",
            "receptor_rut": "66.666.666-6",
            "receptor_razon_social": "Cliente Final Pastelero",
            "monto_neto": 10000.0,
            "monto_exento": 0.0,
            "monto_iva": 1900.0,
            "monto_total": 11900.0,
            "estado_sii": estadoSii or "accepted_by_sii",
            "track_id_sii": "SII-MOCK-2026-0091",
            "xml_payload_uri": "sii-storage://mock-env/dte-39-folio-1042.xml",
            "order_id": "ord-01",
            "created_at": "2026-09-25T14:30:00Z"
        }
    ]

@router.post("", status_code=201, response_model=dict)
def create_dte(
    payload: dict,
    context: TenantContext = Depends(get_current_context)
):
    return {
        "id": str(uuid.uuid4()),
        "tenant_id": context.tenant_id,
        "tipo_dte": payload.get("tipo_dte", 39),
        "folio": payload.get("folio") or 1043,
        "fecha_emision": payload.get("fecha_emision", "2026-09-25"),
        "emisor_rut": payload.get("emisor_rut", "76.123.456-7"),
        "receptor_rut": payload.get("receptor_rut", "66.666.666-6"),
        "receptor_razon_social": payload.get("receptor_razon_social", "Consumidor"),
        "monto_neto": float(payload.get("monto_neto", 10000.0)),
        "monto_exento": float(payload.get("monto_exento", 0.0)),
        "monto_iva": float(payload.get("monto_iva", 1900.0)),
        "monto_total": float(payload.get("monto_total", 11900.0)),
        "estado_sii": "draft",
        "track_id_sii": None,
        "xml_payload_uri": None,
        "order_id": payload.get("order_id"),
        "created_at": "2026-09-25T15:30:00Z"
    }

@router.post("/{id}/emit", response_model=dict)
def emit_dte(
    id: str,
    context: TenantContext = Depends(get_current_context)
):
    return {
        "id": id,
        "tenant_id": context.tenant_id,
        "tipo_dte": 39,
        "folio": 1043,
        "fecha_emision": "2026-09-25",
        "emisor_rut": "76.123.456-7",
        "receptor_rut": "66.666.666-6",
        "receptor_razon_social": "Consumidor",
        "monto_neto": 10000.0,
        "monto_exento": 0.0,
        "monto_iva": 1900.0,
        "monto_total": 11900.0,
        "estado_sii": "accepted_by_sii",
        "track_id_sii": f"SII-SIM-{uuid.uuid4().hex[:8].upper()}",
        "xml_payload_uri": f"sii-storage://mock-env/dte-{id}.xml",
        "order_id": None,
        "created_at": "2026-09-25T15:30:00Z"
    }
