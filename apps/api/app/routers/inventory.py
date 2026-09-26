
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import TenantContext, get_current_context
from app.schemas.production_models import (
    IngredientCreateInput,
    IngredientItem,
)
from app.services.production_service import production_store

router = APIRouter(prefix="/inventory/ingredients", tags=["Producción y Costeo"])

@router.get("", response_model=list[IngredientItem])
def list_ingredients(
    search: str | None = None,
    context: TenantContext = Depends(get_current_context)
):
    items = production_store.list_ingredients(tenant_id=context.tenant_id, search=search)
    return [IngredientItem(**i) for i in items]

@router.post("", status_code=status.HTTP_201_CREATED, response_model=IngredientItem)
def create_ingredient(
    payload: IngredientCreateInput,
    context: TenantContext = Depends(get_current_context)
):
    created = production_store.create_ingredient(tenant_id=context.tenant_id, data=payload)
    return IngredientItem(**created)

@router.get("/{id}", response_model=IngredientItem)
def get_ingredient(
    id: str,
    context: TenantContext = Depends(get_current_context)
):
    ing = production_store.get_ingredient(tenant_id=context.tenant_id, ing_id=id)
    if not ing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insumo no encontrado."
        )
    return IngredientItem(**ing)
