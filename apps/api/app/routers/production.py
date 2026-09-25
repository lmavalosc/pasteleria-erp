from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.core.deps import get_current_context, TenantContext
from app.schemas.production_models import (
    Recipe,
    RecipeCreateInput,
    ProductCostingAnalysis,
    ProductionOrder,
    ProductionOrderCreateInput,
    ProductionOrderUpdateStatusInput,
)
from app.services.production_service import production_store

router = APIRouter(prefix="/production", tags=["Producción y Costeo"])

# -----------------------------------------------------------------
# 1. Recetas / Escandallos
# -----------------------------------------------------------------
@router.get("/recipes", response_model=List[Recipe])
def list_recipes(
    productId: Optional[str] = None,
    context: TenantContext = Depends(get_current_context)
):
    recipes = production_store.list_recipes(tenant_id=context.tenant_id, product_id=productId)
    return [Recipe(**r) for r in recipes]

@router.post("/recipes", status_code=status.HTTP_201_CREATED, response_model=Recipe)
def create_recipe(
    payload: RecipeCreateInput,
    context: TenantContext = Depends(get_current_context)
):
    try:
        recipe = production_store.create_recipe(tenant_id=context.tenant_id, data=payload)
        return Recipe(**recipe)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/recipes/{id}", response_model=Recipe)
def get_recipe(
    id: str,
    context: TenantContext = Depends(get_current_context)
):
    recipe = production_store.get_recipe(tenant_id=context.tenant_id, recipe_id=id)
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receta no encontrada."
        )
    return Recipe(**recipe)

# -----------------------------------------------------------------
# 2. Escandallo y Análisis de Margen / Rentabilidad
# -----------------------------------------------------------------
@router.get("/costing/{productId}", response_model=ProductCostingAnalysis)
def get_product_costing(
    productId: str,
    context: TenantContext = Depends(get_current_context)
):
    costing = production_store.calculate_product_costing(
        tenant_id=context.tenant_id,
        product_id=productId
    )
    return ProductCostingAnalysis(**costing)

# -----------------------------------------------------------------
# 3. Órdenes de Producción
# -----------------------------------------------------------------
@router.get("/orders", response_model=List[ProductionOrder])
def list_production_orders(
    estado: Optional[str] = None,
    context: TenantContext = Depends(get_current_context)
):
    orders = production_store.list_orders(tenant_id=context.tenant_id, estado=estado)
    return [ProductionOrder(**o) for o in orders]

@router.post("/orders", status_code=status.HTTP_201_CREATED, response_model=ProductionOrder)
def create_production_order(
    payload: ProductionOrderCreateInput,
    context: TenantContext = Depends(get_current_context)
):
    try:
        order = production_store.create_production_order(tenant_id=context.tenant_id, data=payload)
        return ProductionOrder(**order)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.patch("/orders/{id}/status", response_model=ProductionOrder)
def update_production_order_status(
    id: str,
    payload: ProductionOrderUpdateStatusInput,
    context: TenantContext = Depends(get_current_context)
):
    try:
        order = production_store.update_order_status(
            tenant_id=context.tenant_id,
            order_id=id,
            new_status=payload.estado
        )
        return ProductionOrder(**order)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.post("/orders/{id}/complete", response_model=ProductionOrder)
def complete_production_order(
    id: str,
    context: TenantContext = Depends(get_current_context)
):
    """
    Marca la orden de producción como completed y descuenta automáticamente los insumos.
    """
    try:
        order = production_store.update_order_status(
            tenant_id=context.tenant_id,
            order_id=id,
            new_status="completed"
        )
        return ProductionOrder(**order)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
