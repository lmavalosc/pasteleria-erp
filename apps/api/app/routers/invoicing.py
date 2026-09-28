from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Header, Query

from app.api.deps import DbTenant, TenantId
from app.schemas.invoicing import (
    DteInvoiceCreate,
    DteInvoicePage,
    DteInvoiceRead,
)
from app.services import invoicing as invoicing_service

router = APIRouter(prefix="/invoicing", tags=["invoicing"])


@router.get("/dte", response_model=DteInvoicePage)
def list_dte(
    db: DbTenant,
    tenant_id: TenantId,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    return invoicing_service.list_dte_invoices(db, tenant_id, page, page_size)


@router.post("/dte", response_model=DteInvoiceRead, status_code=201)
def create_dte(
    db: DbTenant,
    tenant_id: TenantId,
    payload: DteInvoiceCreate,
    idempotency_key: Annotated[str | None, Header()] = None,
):
    _ = idempotency_key
    return invoicing_service.create_dte_invoice(db, tenant_id, payload)


@router.get("/dte/{dte_id}", response_model=DteInvoiceRead)
def get_dte(
    db: DbTenant,
    tenant_id: TenantId,
    dte_id: UUID,
):
    return invoicing_service.get_dte_invoice(db, tenant_id, dte_id)


@router.post("/dte/{dte_id}/issue", response_model=DteInvoiceRead)
def issue_dte(
    db: DbTenant,
    tenant_id: TenantId,
    dte_id: UUID,
):
    return invoicing_service.issue_dte_invoice(db, tenant_id, dte_id)
