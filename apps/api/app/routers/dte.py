
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.deps import get_current_context, require_roles
from app.schemas.core_models import DTECreateRequest, DTEResponse, UserRole
from app.services.dte_service import dte_store

router = APIRouter(prefix="/v1/dte", tags=["dte"])

@router.post("/create", response_model=DTEResponse, status_code=status.HTTP_201_CREATED)
def create_dte(
    payload: DTECreateRequest,
    context: TenantContext = Depends(require_roles([UserRole.OWNER, UserRole.ADMIN, UserRole.ACCOUNTANT, UserRole.CASHIER]))
):
    dte = dte_store.create(context.tenant_id, payload)
    return DTEResponse(**dte)

@router.post("/{id}/emit", response_model=DTEResponse)
def emit_dte(
    id: str,
    context: TenantContext = Depends(require_roles([UserRole.OWNER, UserRole.ADMIN, UserRole.ACCOUNTANT, UserRole.CASHIER]))
):
    try:
        dte = dte_store.emit(id, context.tenant_id)
        return DTEResponse(**dte)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("", response_model=list[DTEResponse])
def list_dtes(
    tipo_dte: int | None = Query(None, description="39: Boleta, 33: Factura, 61: Nota Credito"),
    estado_sii: str | None = Query(None, description="draft, generated, sent_to_sii, accepted_by_sii, rejected_by_sii"),
    fecha_desde: str | None = Query(None, description="YYYY-MM-DD"),
    fecha_hasta: str | None = Query(None, description="YYYY-MM-DD"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    context: TenantContext = Depends(get_current_context)
):
    dtes = dte_store.list_dtes(
        tenant_id=context.tenant_id,
        tipo_dte=tipo_dte,
        estado_sii=estado_sii,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        page=page,
        page_size=page_size
    )
    return [DTEResponse(**d) for d in dtes]

@router.get("/{id}", response_model=DTEResponse)
def get_dte(
    id: str,
    context: TenantContext = Depends(get_current_context)
):
    dte = dte_store.get_by_id(id, context.tenant_id)
    if not dte:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DTE no encontrado."
        )
    return DTEResponse(**dte)
