from enum import Enum

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
    codigo: str | None = None
    nombre: str
    unidad_medida: str
    costo_unitario_promedio: float
    stock_actual: float
    alergenos: list[str] = Field(default_factory=list)
    created_at: str

class IngredientCreateInput(BaseModel):
    codigo: str | None = None
    nombre: str
    unidad_medida: str = "kg"
    costo_unitario_promedio: float
    stock_actual: float = 0.0
    alergenos: list[str] = Field(default_factory=list)

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
    ingredientes: list[RecipeIngredientItem]
    empaques: list[RecipePackagingItem] = Field(default_factory=list)
    costo_total_batch: float
    costo_por_porcion: float
    instrucciones: str | None = None
    created_at: str

class RecipeCreateInput(BaseModel):
    product_id: str
    nombre_receta: str
    rendimiento_porciones: float = Field(ge=1.0)
    tiempo_elaboracion_minutos: int = 60
    ingredientes: list[RecipeIngredientItemInput]
    empaques: list[RecipePackagingItem] = Field(default_factory=list)
    instrucciones: str | None = None

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
    fecha_finalizada: str | None = None
    responsable_chef: str | None = None
    inventario_descontado: bool = False
    notas: str | None = None
    created_at: str

class ProductionOrderCreateInput(BaseModel):
    recipe_id: str
    cantidad_a_elaborar: int = Field(ge=1)
    fecha_programada: str
    responsable_chef: str | None = None
    descontar_inventario_inmediato: bool = False
    notas: str | None = None

class ProductionOrderUpdateStatusInput(BaseModel):
    estado: str
