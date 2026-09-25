from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class UnitOfMeasure(str, Enum):
    KG = "kg"
    G = "g"
    L = "l"
    ML = "ml"
    UNIDAD = "unidad"

class ProductionOrderStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PREP = "in_prep"
    BAKING = "baking"
    FINISHED = "finished"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# Insumos / Ingredients
class IngredientItem(BaseModel):
    id: str
    tenant_id: str
    codigo: Optional[str] = None
    nombre: str
    unidad_medida: str
    costo_unitario_promedio: float
    stock_actual: float
    alergenos: List[str] = Field(default_factory=list)
    created_at: str

class IngredientCreateInput(BaseModel):
    codigo: Optional[str] = None
    nombre: str
    unidad_medida: str = "kg"
    costo_unitario_promedio: float
    stock_actual: float = 0.0
    alergenos: List[str] = Field(default_factory=list)

# Recetas / Escandallos
class RecipeIngredientItem(BaseModel):
    ingredient_id: str
    nombre_ingrediente: str
    cantidad_neta: float
    unidad_medida: str
    porcentaje_merma: float = 0.0
    costo_calculado: float

class RecipeIngredientItemInput(BaseModel):
    ingredient_id: str
    cantidad_neta: float
    porcentaje_merma: float = 0.0

class RecipePackagingItem(BaseModel):
    nombre: str
    costo_unitario: float
    cantidad: float = 1.0

class Recipe(BaseModel):
    id: str
    tenant_id: str
    product_id: str
    nombre_receta: str
    rendimiento_porciones: float
    tiempo_elaboracion_minutos: int = 60
    ingredientes: List[RecipeIngredientItem]
    empaques: List[RecipePackagingItem] = Field(default_factory=list)
    costo_total_batch: float
    costo_por_porcion: float
    instrucciones: Optional[str] = None
    created_at: str

class RecipeCreateInput(BaseModel):
    product_id: str
    nombre_receta: str
    rendimiento_porciones: float = Field(ge=1.0)
    tiempo_elaboracion_minutos: int = 60
    ingredientes: List[RecipeIngredientItemInput]
    empaques: List[RecipePackagingItem] = Field(default_factory=list)
    instrucciones: Optional[str] = None

# Costeo y Rentabilidad
class ProductCostingAnalysis(BaseModel):
    product_id: str
    tenant_id: str
    nombre_producto: str
    precio_venta_neto: float
    costo_insumos_porcion: float
    costo_empaque_porcion: float
    costo_total_porcion: float
    margen_bruto_monto: float
    margen_bruto_porcentaje: float
    alerta_margen_bajo: bool
    fecha_calculo: str

# Órdenes de Producción
class ProductionOrder(BaseModel):
    id: str
    tenant_id: str
    numero_orden: str
    recipe_id: str
    product_id: str
    cantidad_a_elaborar: int
    estado: str
    fecha_programada: str
    fecha_finalizada: Optional[str] = None
    responsable_chef: Optional[str] = None
    inventario_descontado: bool = False
    notas: Optional[str] = None
    created_at: str

class ProductionOrderCreateInput(BaseModel):
    recipe_id: str
    cantidad_a_elaborar: int = Field(ge=1)
    fecha_programada: str
    responsable_chef: Optional[str] = None
    descontar_inventario_inmediato: bool = False
    notas: Optional[str] = None

class ProductionOrderUpdateStatusInput(BaseModel):
    estado: str
