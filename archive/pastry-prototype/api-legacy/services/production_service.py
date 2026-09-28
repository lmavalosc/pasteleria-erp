import uuid
from datetime import datetime

from app.schemas.production_models import (
    IngredientCreateInput,
    ProductionOrderCreateInput,
    RecipeCreateInput,
)


class ProductionStore:
    def __init__(self):
        # tenant_id -> {id: ingredient_dict}
        self.ingredients: dict[str, dict[str, dict]] = {}
        # tenant_id -> {id: recipe_dict}
        self.recipes: dict[str, dict[str, dict]] = {}
        # tenant_id -> {product_id: product_dict}
        self.products: dict[str, dict[str, dict]] = {}
        # tenant_id -> {id: order_dict}
        self.orders: dict[str, dict[str, dict]] = {}
        # tenant_id -> int
        self.order_counter: dict[str, int] = {}

    def _ensure_tenant(self, tenant_id: str):
        if tenant_id not in self.ingredients:
            self.ingredients[tenant_id] = {}
        if tenant_id not in self.recipes:
            self.recipes[tenant_id] = {}
        if tenant_id not in self.products:
            self.products[tenant_id] = {}
        if tenant_id not in self.orders:
            self.orders[tenant_id] = {}
        if tenant_id not in self.order_counter:
            self.order_counter[tenant_id] = 0

    # ----------------------------------------------------
    # INGREDIENTES & PPP (Precio Promedio Ponderado)
    # ----------------------------------------------------
    def create_ingredient(self, tenant_id: str, data: IngredientCreateInput) -> dict:
        self._ensure_tenant(tenant_id)
        ing_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat() + "Z"
        item = {
            "id": ing_id,
            "tenant_id": tenant_id,
            "codigo": data.codigo or f"ING-{uuid.uuid4().hex[:6].upper()}",
            "nombre": data.nombre,
            "unidad_medida": data.unidad_medida,
            "costo_unitario_promedio": float(data.costo_unitario_promedio),
            "stock_actual": float(data.stock_actual),
            "alergenos": data.alergenos,
            "created_at": now
        }
        self.ingredients[tenant_id][ing_id] = item
        return item

    def get_ingredient(self, tenant_id: str, ing_id: str) -> dict | None:
        self._ensure_tenant(tenant_id)
        return self.ingredients[tenant_id].get(ing_id)

    def find_ingredient_by_name(self, tenant_id: str, name: str) -> dict | None:
        self._ensure_tenant(tenant_id)
        name_clean = name.strip().lower()
        for item in self.ingredients[tenant_id].values():
            if item["nombre"].strip().lower() == name_clean:
                return item
        return None

    def list_ingredients(self, tenant_id: str, search: str | None = None) -> list[dict]:
        self._ensure_tenant(tenant_id)
        items = list(self.ingredients[tenant_id].values())
        if search:
            s = search.lower()
            items = [i for i in items if s in i["nombre"].lower() or (i.get("codigo") and s in i["codigo"].lower())]
        return items

    def apply_purchase_ppp(
        self,
        tenant_id: str,
        ingredient_id: str | None,
        nombre_insumo: str,
        cantidad_comprada: float,
        precio_unitario_compra: float,
        unidad_medida: str = "kg"
    ) -> dict:
        """
        Actualiza el Precio Promedio Ponderado (PPP) y el stock al registrar una compra/gasto:
        
        Formula contable PPP:
        PPP_nuevo = (Stock_previo * PPP_previo + Cantidad_comprada * Precio_compra) / (Stock_previo + Cantidad_comprada)
        Stock_nuevo = Stock_previo + Cantidad_comprada
        
        Si el stock previo era <= 0, el nuevo PPP es directamente el precio_unitario_compra.
        """
        self._ensure_tenant(tenant_id)
        ing = None
        if ingredient_id:
            ing = self.get_ingredient(tenant_id, ingredient_id)
        if not ing:
            ing = self.find_ingredient_by_name(tenant_id, nombre_insumo)

        if not ing:
            # Crear insumo nuevo en el inventario con el stock inicial de la compra
            ing = self.create_ingredient(
                tenant_id=tenant_id,
                data=IngredientCreateInput(
                    nombre=nombre_insumo,
                    unidad_medida=unidad_medida,
                    costo_unitario_promedio=precio_unitario_compra,
                    stock_actual=cantidad_comprada,
                    alergenos=[]
                )
            )
            return ing

        # Cálculo de PPP
        stock_antiguo = float(ing.get("stock_actual", 0.0))
        costo_antiguo = float(ing.get("costo_unitario_promedio", 0.0))
        nuevo_stock = stock_antiguo + cantidad_comprada

        if stock_antiguo <= 0:
            nuevo_ppp = precio_unitario_compra
        elif nuevo_stock > 0:
            valor_total_anterior = stock_antiguo * costo_antiguo
            valor_nueva_compra = cantidad_comprada * precio_unitario_compra
            nuevo_ppp = (valor_total_anterior + valor_nueva_compra) / nuevo_stock
        else:
            nuevo_ppp = costo_antiguo

        ing["stock_actual"] = round(nuevo_stock, 4)
        ing["costo_unitario_promedio"] = round(nuevo_ppp, 2)
        return ing

    # ----------------------------------------------------
    # RECETAS & ESCANDALLOS
    # ----------------------------------------------------
    def create_recipe(self, tenant_id: str, data: RecipeCreateInput) -> dict:
        self._ensure_tenant(tenant_id)
        rec_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat() + "Z"

        # Validar y calcular cada ingrediente
        calc_ingredientes = []
        costo_insumos_total = 0.0

        for item_in in data.ingredientes:
            ing = self.get_ingredient(tenant_id, item_in.ingredient_id)
            if not ing:
                raise ValueError(f"Insumo con ID '{item_in.ingredient_id}' no encontrado en el tenant {tenant_id}.")

            costo_unitario = float(ing["costo_unitario_promedio"])
            cantidad_neta = float(item_in.cantidad_neta)
            porcentaje_merma = float(item_in.porcentaje_merma)

            # Costo con merma técnica:
            # Cantidad bruta requerida = Cantidad neta * (1 + % merma / 100)
            costo_item = cantidad_neta * (1.0 + (porcentaje_merma / 100.0)) * costo_unitario
            costo_insumos_total += costo_item

            calc_ingredientes.append({
                "ingredient_id": item_in.ingredient_id,
                "nombre_ingrediente": ing["nombre"],
                "cantidad_neta": cantidad_neta,
                "unidad_medida": ing["unidad_medida"],
                "porcentaje_merma": porcentaje_merma,
                "costo_calculado": round(costo_item, 2)
            })

        # Costo de packaging
        costo_empaques_total = 0.0
        calc_empaques = []
        for emp in (data.empaques or []):
            c_emp = float(emp.costo_unitario) * float(emp.cantidad)
            costo_empaques_total += c_emp
            calc_empaques.append({
                "nombre": emp.nombre,
                "costo_unitario": float(emp.costo_unitario),
                "cantidad": float(emp.cantidad)
            })

        costo_total_batch = round(costo_insumos_total + costo_empaques_total, 2)
        porciones = float(data.rendimiento_porciones)
        costo_por_porcion = round(costo_total_batch / porciones, 2) if porciones > 0 else 0.0

        recipe = {
            "id": rec_id,
            "tenant_id": tenant_id,
            "product_id": data.product_id,
            "nombre_receta": data.nombre_receta,
            "rendimiento_porciones": porciones,
            "tiempo_elaboracion_minutos": data.tiempo_elaboracion_minutos,
            "ingredientes": calc_ingredientes,
            "empaques": calc_empaques,
            "costo_total_batch": costo_total_batch,
            "costo_por_porcion": costo_por_porcion,
            "instrucciones": data.instrucciones,
            "created_at": now
        }
        self.recipes[tenant_id][rec_id] = recipe
        return recipe

    def get_recipe(self, tenant_id: str, recipe_id: str) -> dict | None:
        self._ensure_tenant(tenant_id)
        return self.recipes[tenant_id].get(recipe_id)

    def get_recipe_by_product(self, tenant_id: str, product_id: str) -> dict | None:
        self._ensure_tenant(tenant_id)
        for r in self.recipes[tenant_id].values():
            if r["product_id"] == product_id:
                return r
        return None

    def list_recipes(self, tenant_id: str, product_id: str | None = None) -> list[dict]:
        self._ensure_tenant(tenant_id)
        items = list(self.recipes[tenant_id].values())
        if product_id:
            items = [r for r in items if r["product_id"] == product_id]
        return items

    # ----------------------------------------------------
    # PRODUCTOS & PRECIOS DE VENTA
    # ----------------------------------------------------
    def register_product(self, tenant_id: str, product_id: str, nombre: str, precio_venta_neto: float):
        self._ensure_tenant(tenant_id)
        self.products[tenant_id][product_id] = {
            "product_id": product_id,
            "nombre": nombre,
            "precio_venta_neto": float(precio_venta_neto)
        }

    def get_product(self, tenant_id: str, product_id: str) -> dict:
        self._ensure_tenant(tenant_id)
        if product_id in self.products[tenant_id]:
            return self.products[tenant_id][product_id]
        # Producto default si no está explícitamente registrado
        return {
            "product_id": product_id,
            "nombre": f"Producto Pastel {product_id}",
            "precio_venta_neto": 12500.0
        }

    # ----------------------------------------------------
    # CÁLCULO DEL ESCANDALLO Y RENTABILIDAD EN VIVO
    # ----------------------------------------------------
    def calculate_product_costing(self, tenant_id: str, product_id: str) -> dict:
        """
        Calcula el escandallo en tiempo real usando los PPP vigentes de cada insumo.
        
        Fórmulas requeridas:
        Costo Insumos = Suma(Cantidad * Costo Promedio del Insumo * (1 + % Merma / 100))
        Costo Total = Costo Insumos + Costo de Packaging
        Costo por Porción = Costo Total / Número de Porciones
        
        Métricas de Rentabilidad:
        Margen Bruto en dinero ($) = Precio Venta Neto - Costo por Porción
        Porcentaje de Rentabilidad (%) = (Margen Bruto / Precio Venta Neto) * 100
        Alerta Booleana 'low_margin_warning' = True si Margen % < 50.0%
        """
        self._ensure_tenant(tenant_id)
        recipe = self.get_recipe_by_product(tenant_id, product_id)
        product = self.get_product(tenant_id, product_id)
        precio_venta_neto = float(product["precio_venta_neto"])

        now = datetime.utcnow().isoformat() + "Z"

        if not recipe:
            # Fallback seguro si aún no se ha cargado una receta
            costo_insumos_porcion = 0.0
            costo_empaque_porcion = 0.0
            costo_total_porcion = 0.0
            margen_monto = precio_venta_neto
            margen_pct = 100.0 if precio_venta_neto > 0 else 0.0
            return {
                "product_id": product_id,
                "tenant_id": tenant_id,
                "nombre_producto": product["nombre"],
                "precio_venta_neto": precio_venta_neto,
                "costo_insumos_porcion": costo_insumos_porcion,
                "costo_empaque_porcion": costo_empaque_porcion,
                "costo_total_porcion": costo_total_porcion,
                "margen_bruto_monto": round(margen_monto, 2),
                "margen_bruto_porcentaje": round(margen_pct, 2),
                "alerta_margen_bajo": margen_pct < 50.0,
                "low_margin_warning": margen_pct < 50.0,
                "fecha_calculo": now
            }

        porciones = float(recipe.get("rendimiento_porciones", 1.0))
        if porciones <= 0:
            porciones = 1.0

        # Recalcular costo de insumos con los PPP actuales del inventario
        costo_insumos_batch = 0.0
        for item in recipe["ingredientes"]:
            ing_id = item["ingredient_id"]
            ing = self.get_ingredient(tenant_id, ing_id)
            costo_unit = float(ing["costo_unitario_promedio"]) if ing else float(item.get("costo_calculado", 0))
            cant_neta = float(item["cantidad_neta"])
            merma_pct = float(item.get("porcentaje_merma", 0.0))
            costo_item = cant_neta * (1.0 + (merma_pct / 100.0)) * costo_unit
            costo_insumos_batch += costo_item

        # Costo de packaging
        costo_empaques_batch = sum(
            float(e["costo_unitario"]) * float(e["cantidad"])
            for e in recipe.get("empaques", [])
        )

        costo_insumos_porcion = round(costo_insumos_batch / porciones, 2)
        costo_empaque_porcion = round(costo_empaques_batch / porciones, 2)
        costo_total_porcion = round(costo_insumos_porcion + costo_empaque_porcion, 2)

        margen_monto = round(precio_venta_neto - costo_total_porcion, 2)
        if precio_venta_neto > 0:
            margen_pct = round((margen_monto / precio_venta_neto) * 100.0, 2)
        else:
            margen_pct = 0.0

        low_margin = margen_pct < 50.0

        return {
            "product_id": product_id,
            "tenant_id": tenant_id,
            "nombre_producto": product["nombre"],
            "precio_venta_neto": precio_venta_neto,
            "costo_insumos_porcion": costo_insumos_porcion,
            "costo_empaque_porcion": costo_empaque_porcion,
            "costo_total_porcion": costo_total_porcion,
            "margen_bruto_monto": margen_monto,
            "margen_bruto_porcentaje": margen_pct,
            "alerta_margen_bajo": low_margin,
            "low_margin_warning": low_margin,
            "fecha_calculo": now
        }

    # ----------------------------------------------------
    # ÓRDENES DE PRODUCCIÓN & DESCUENTO DE STOCK
    # ----------------------------------------------------
    def create_production_order(self, tenant_id: str, data: ProductionOrderCreateInput) -> dict:
        self._ensure_tenant(tenant_id)
        recipe = self.get_recipe(tenant_id, data.recipe_id)
        if not recipe:
            raise ValueError(f"Receta con ID '{data.recipe_id}' no existe en el tenant {tenant_id}.")

        self.order_counter[tenant_id] += 1
        num_orden = f"ORD-PROD-2026-{self.order_counter[tenant_id]:04d}"
        order_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat() + "Z"

        order = {
            "id": order_id,
            "tenant_id": tenant_id,
            "numero_orden": num_orden,
            "recipe_id": data.recipe_id,
            "product_id": recipe["product_id"],
            "cantidad_a_elaborar": data.cantidad_a_elaborar,
            "estado": "scheduled",
            "fecha_programada": data.fecha_programada,
            "fecha_finalizada": None,
            "responsable_chef": data.responsable_chef or "Chef Pastelero",
            "inventario_descontado": False,
            "notas": data.notas,
            "created_at": now
        }

        # Si se solicitó descuento inmediato al crear la orden
        if data.descontar_inventario_inmediato:
            self._deduct_inventory_for_order(tenant_id, order, recipe)

        self.orders[tenant_id][order_id] = order
        return order

    def update_order_status(self, tenant_id: str, order_id: str, new_status: str) -> dict:
        self._ensure_tenant(tenant_id)
        order = self.orders[tenant_id].get(order_id)
        if not order:
            raise ValueError(f"Orden de producción con ID '{order_id}' no encontrada.")

        recipe = self.get_recipe(tenant_id, order["recipe_id"])
        norm_status = new_status.strip().lower()
        order["estado"] = norm_status

        # Requisito: Al marcar una orden como 'completed' (o 'finished'),
        # descuenta automáticamente las cantidades de insumos del stock teórico
        if norm_status in ("completed", "finished"):
            now = datetime.utcnow().isoformat() + "Z"
            order["fecha_finalizada"] = now
            if not order["inventario_descontado"]:
                if recipe:
                    self._deduct_inventory_for_order(tenant_id, order, recipe)

        return order

    def _deduct_inventory_for_order(self, tenant_id: str, order: dict, recipe: dict):
        """
        Descuenta las cantidades de insumos del stock teórico del tenant.
        Multiplicador = cantidad_a_elaborar / rendimiento_porciones_de_receta
        """
        porciones_batch = float(recipe.get("rendimiento_porciones", 1.0))
        if porciones_batch <= 0:
            porciones_batch = 1.0

        cantidad_orden = float(order["cantidad_a_elaborar"])
        multiplicador = cantidad_orden / porciones_batch

        for item in recipe.get("ingredientes", []):
            ing_id = item["ingredient_id"]
            ing = self.get_ingredient(tenant_id, ing_id)
            if ing:
                # Cantidad bruta = cantidad neta * (1 + % merma / 100)
                cant_neta = float(item["cantidad_neta"])
                merma_pct = float(item.get("porcentaje_merma", 0.0))
                cant_bruta_por_batch = cant_neta * (1.0 + (merma_pct / 100.0))
                total_a_descontar = cant_bruta_por_batch * multiplicador

                ing["stock_actual"] = round(ing["stock_actual"] - total_a_descontar, 4)

        order["inventario_descontado"] = True

    def list_orders(self, tenant_id: str, estado: str | None = None) -> list[dict]:
        self._ensure_tenant(tenant_id)
        items = list(self.orders[tenant_id].values())
        if estado:
            norm = estado.strip().lower()
            items = [o for o in items if o["estado"] == norm]
        return items

    def get_order(self, tenant_id: str, order_id: str) -> dict | None:
        self._ensure_tenant(tenant_id)
        return self.orders[tenant_id].get(order_id)


# Singleton
production_store = ProductionStore()
