from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from app.schemas.core_models import (
    ExpenseCreateRequest, ExpenseResponse, ExpenseRejectRequest,
    UserRole
)
from app.core.deps import get_current_context, require_roles
from app.services.expense_service import expense_store
from app.services.document_service import document_store

router = APIRouter(prefix="/v1/expenses", tags=["expenses"])

@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(
    payload: ExpenseCreateRequest,
    context: TenantContext = Depends(get_current_context)
):
    if payload.document_id:
        doc = document_store.get_by_id(payload.document_id, context.tenant_id)
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El documento {payload.document_id} no existe o no pertenece a su empresa."
            )

    expense = expense_store.create(
        tenant_id=context.tenant_id,
        user_id=context.user_id,
        data=payload
    )
    return ExpenseResponse(**expense)

@router.get("", response_model=List[ExpenseResponse])
def list_expenses(
    estado: Optional[str] = Query(None, description="Filtrar por estado: draft, pending_approval, approved, rejected"),
    categoria: Optional[str] = Query(None, description="Filtrar por categoría"),
    fecha_desde: Optional[str] = Query(None, description="YYYY-MM-DD"),
    fecha_hasta: Optional[str] = Query(None, description="YYYY-MM-DD"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    context: TenantContext = Depends(get_current_context)
):
    expenses = expense_store.list_expenses(
        tenant_id=context.tenant_id,
        estado=estado,
        categoria=categoria,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        page=page,
        page_size=page_size
    )
    return [ExpenseResponse(**e) for e in expenses]

@router.get("/{id}", response_model=ExpenseResponse)
def get_expense(
    id: str,
    context: TenantContext = Depends(get_current_context)
):
    exp = expense_store.get_by_id(id, context.tenant_id)
    if not exp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gasto no encontrado."
        )
    return ExpenseResponse(**exp)

@router.post("/{id}/approve", response_model=ExpenseResponse)
def approve_expense(
    id: str,
    context: TenantContext = Depends(require_roles([UserRole.OWNER, UserRole.ADMIN, UserRole.ACCOUNTANT]))
):
    exp = expense_store.approve(id, context.tenant_id, context.user_id)
    if not exp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gasto no encontrado."
        )
    return ExpenseResponse(**exp)

@router.post("/{id}/reject", response_model=ExpenseResponse)
def reject_expense(
    id: str,
    payload: ExpenseRejectRequest,
    context: TenantContext = Depends(require_roles([UserRole.OWNER, UserRole.ADMIN, UserRole.ACCOUNTANT]))
):
    exp = expense_store.reject(id, context.tenant_id, context.user_id, payload.motivo_rechazo)
    if not exp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gasto no encontrado."
        )
    return ExpenseResponse(**exp)
