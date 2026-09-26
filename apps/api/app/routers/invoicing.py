import math
from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.deps import get_db_with_tenant, get_tenant_id_from_header
from app.core.pagination import Page, PageParams
from app.integrations.sii.adapter import get_sii_client
from app.repositories.invoicing import InvoicingRepository
from app.schemas.invoicing import DteEmissionRequest, DteInvoiceRead
from app.services.invoicing import InvoicingService

router = APIRouter(prefix="/invoicing", tags=["invoicing"])


@router.post("/dte", response_model=DteInvoiceRead, status_code=status.HTTP_201_CREATED)
def emit_dte(
    data: DteEmissionRequest,
    tenant_id: UUID = Depends(get_tenant_id_from_header),
    db: Session = Depends(get_db_with_tenant),
):
    # En producción el RUT emisor se extrae del tenant activo
    emitter_rut = "76000000-9"
    service = InvoicingService(InvoicingRepository(db), get_sii_client())
    return service.emit_dte(tenant_id, emitter_rut, data)


@router.get("/dte", response_model=Page[DteInvoiceRead])
def list_invoices(
    params: Annotated[PageParams, Depends()],
    db: Session = Depends(get_db_with_tenant),
):
    repo = InvoicingRepository(db)
    items, total = repo.list_paginated(params.offset, params.page_size)
    pages = math.ceil(total / params.page_size) if total > 0 else 1
    return Page(
        items=items,
        total=total,
        page=params.page,
        page_size=params.page_size,
        total_pages=pages,
    )
