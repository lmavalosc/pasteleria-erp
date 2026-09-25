import pytest
from fastapi.testclient import TestClient
from main import app
from app.services.production_service import production_store

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_production_data():
    """Limpia los stores de producción antes de cada test."""
    production_store.ingredients.clear()
    production_store.recipes.clear()
    production_store.products.clear()
    production_store.orders.clear()
    production_store.order_counter.clear()

# -------------------------------------------------------------
# 1. TEST PRECIO PROMEDIO PONDERADO (PPP) VÍA EGRESOS / GASTOS
# -------------------------------------------------------------
def test_weighted_average_price_ppp_calculation():
    tenant_a = "tenant-atelier-paris"
    headers_a = {"X-Tenant-ID": tenant_a}

    # Insumo inicial: 20 kg de Chocolate Belga a $10.000/kg (Valor inicial = $200.000)
    ing_res = client.post("/v1/inventory/ingredients", headers=headers_a, json={
        "codigo": "CHOCO-01",
        "nombre": "Chocolate Belga 70%",
        "unidad_medida": "kg",
        "costo_unitario_promedio": 10000.0,
        "stock_actual": 20.0,
        "alergenos": ["lacteos"]
    })
    assert ing_res.status_code == 201
    choco_id = ing_res.json()["id"]

    # Compra 1 vía gasto: 10 kg a $13.000/kg (Valor compra = $130.000)
    # Total valor = 200.000 + 130.000 = 330.000
    # Total stock = 20 + 10 = 30 kg
    # Nuevo PPP esperado = 330.000 / 30 = $11.000/kg
    expense_payload = {
        "proveedor_nombre": "Chocolaterie Valrhona Import",
        "fecha_gasto": "2026-09-25",
        "monto_neto": 130000.0,
        "monto_iva": 24700.0,
        "monto_total": 154700.0,
        "categoria_gasto": "materias_primas",
        "metodo_pago": "transferencia",
        "insumos_detalle": [
            {
                "ingredient_id": choco_id,
                "nombre_insumo": "Chocolate Belga 70%",
                "cantidad": 10.0,
                "unidad_medida": "kg",
                "precio_unitario": 13000.0
            }
        ]
    }
    exp_res = client.post("/v1/expenses", headers=headers_a, json=expense_payload)
    assert exp_res.status_code == 201, exp_res.text

    # Verificar stock y PPP actualizado del insumo
    check_res = client.get(f"/v1/inventory/ingredients/{choco_id}", headers=headers_a)
    assert check_res.status_code == 200
    ing_data = check_res.json()
    assert ing_data["stock_actual"] == 30.0
    assert ing_data["costo_unitario_promedio"] == 11000.0

    # Compra 2: Crear insumo automático si no existía previamente
    expense_new_ing = {
        "proveedor_nombre": "Molino del Sur",
        "fecha_gasto": "2026-09-25",
        "monto_neto": 25000.0,
        "monto_total": 25000.0,
        "categoria_gasto": "materias_primas",
        "metodo_pago": "efectivo",
        "insumos_detalle": [
            {
                "nombre_insumo": "Harina Almendras Extra Fina",
                "cantidad": 5.0,
                "unidad_medida": "kg",
                "precio_unitario": 5000.0
            }
        ]
    }
    exp_res2 = client.post("/v1/expenses", headers=headers_a, json=expense_new_ing)
    assert exp_res2.status_code == 201

    # Verificar que el insumo fue creado con PPP $5.000 y stock 5.0
    ing_list = client.get("/v1/inventory/ingredients?search=Almendras", headers=headers_a).json()
    assert len(ing_list) == 1
    assert ing_list[0]["costo_unitario_promedio"] == 5000.0
    assert ing_list[0]["stock_actual"] == 5.0

# -------------------------------------------------------------
# 2. TEST CÁLCULO DE ESCANDALLO Y RENTABILIDAD (/production/costing)
# -------------------------------------------------------------
def test_escandallo_costing_and_margin_warning():
    tenant = "tenant-pastry-chef"
    headers = {"X-Tenant-ID": tenant}

    # 1. Crear insumos con sus PPP
    # Insumo 1: Harina T55 ($1.000 / kg)
    res_harina = client.post("/v1/inventory/ingredients", headers=headers, json={
        "nombre": "Harina T55",
        "unidad_medida": "kg",
        "costo_unitario_promedio": 1000.0,
        "stock_actual": 50.0
    }).json()

    # Insumo 2: Mantequilla ($10.000 / kg)
    res_mantequilla = client.post("/v1/inventory/ingredients", headers=headers, json={
        "nombre": "Mantequilla Francesa",
        "unidad_medida": "kg",
        "costo_unitario_promedio": 10000.0,
        "stock_actual": 20.0
    }).json()

    # 2. Configurar precio de venta neto del producto en el tenant
    product_id = "tarta-francesa-01"
    # Precio venta = $10.000
    production_store.register_product(
        tenant_id=tenant,
        product_id=product_id,
        nombre="Tarta Francesa de Autor",
        precio_venta_neto=10000.0
    )

    # 3. Crear Receta para 4 porciones:
    # - Harina: 0.5 kg con 10% merma -> Cantidad bruta = 0.5 * 1.10 = 0.55 kg * $1.000 = $550
    # - Mantequilla: 0.4 kg con 5% merma -> Cantidad bruta = 0.4 * 1.05 = 0.42 kg * $10.000 = $4.200
    # Costo Insumos Batch = 550 + 4.200 = $4.750
    # Empaques: 4 cajas a $200 = $800
    # Costo Total Batch = 4.750 + 800 = $5.550
    # Costo por Porción = 5.550 / 4 = $1.387,5
    recipe_payload = {
        "product_id": product_id,
        "nombre_receta": "Receta Tarta 4 porciones",
        "rendimiento_porciones": 4,
        "tiempo_elaboracion_minutos": 90,
        "ingredientes": [
            {
                "ingredient_id": res_harina["id"],
                "cantidad_neta": 0.5,
                "porcentaje_merma": 10.0
            },
            {
                "ingredient_id": res_mantequilla["id"],
                "cantidad_neta": 0.4,
                "porcentaje_merma": 5.0
            }
        ],
        "empaques": [
            {
                "nombre": "Caja Individual Dorada",
                "costo_unitario": 200.0,
                "cantidad": 4.0
            }
        ]
    }
    rec_res = client.post("/v1/production/recipes", headers=headers, json=recipe_payload)
    assert rec_res.status_code == 201, rec_res.text
    rec_data = rec_res.json()
    assert rec_data["costo_total_batch"] == 5550.0
    assert rec_data["costo_por_porcion"] == 1387.5

    # 4. Consultar Análisis de Costeo y Rentabilidad
    # Precio venta = $10.000
    # Costo por porción = $1.387,5
    # Margen Bruto ($) = 10.000 - 1.387,5 = $8.612,5
    # Margen Bruto (%) = (8.612,5 / 10.000) * 100 = 86.13% (> 50%, no hay alerta)
    costing_res = client.get(f"/v1/production/costing/{product_id}", headers=headers)
    assert costing_res.status_code == 200
    c_data = costing_res.json()
    assert c_data["precio_venta_neto"] == 10000.0
    assert c_data["costo_total_porcion"] == 1387.5
    assert c_data["margen_bruto_monto"] == 8612.5
    assert c_data["margen_bruto_porcentaje"] == 86.12
    assert c_data["alerta_margen_bajo"] is False

    # 5. CASO MARGEN BAJO (< 50%):
    # Si el precio de venta baja a $2.500:
    # Margen = 2.500 - 1.387,5 = $1.112,5 -> Margen % = 44.5% (< 50%) -> low_margin_warning = True
    production_store.register_product(
        tenant_id=tenant,
        product_id=product_id,
        nombre="Tarta Francesa de Autor (Oferta)",
        precio_venta_neto=2500.0
    )
    costing_low = client.get(f"/v1/production/costing/{product_id}", headers=headers).json()
    assert costing_low["margen_bruto_monto"] == 1112.5
    assert costing_low["margen_bruto_porcentaje"] == 44.5
    assert costing_low["alerta_margen_bajo"] is True

# -------------------------------------------------------------
# 3. TEST EJECUCIÓN DE PRODUCCIÓN & DESCUENTO AUTOMÁTICO DE STOCK
# -------------------------------------------------------------
def test_production_order_inventory_deduction():
    tenant = "tenant-bakery-chile"
    headers = {"X-Tenant-ID": tenant}

    # Crear Insumos
    # Azúcar: Stock inicial = 100.0 kg
    azucar = client.post("/v1/inventory/ingredients", headers=headers, json={
        "nombre": "Azúcar Flor Fina",
        "unidad_medida": "kg",
        "costo_unitario_promedio": 1200.0,
        "stock_actual": 100.0
    }).json()

    # Receta rinde 10 unidades y usa 2 kg de azúcar con 0% merma (0.2 kg / unidad)
    receta = client.post("/v1/production/recipes", headers=headers, json={
        "product_id": "macarons-box",
        "nombre_receta": "Caja 12 Macarons",
        "rendimiento_porciones": 10.0,
        "ingredientes": [
            {
                "ingredient_id": azucar["id"],
                "cantidad_neta": 2.0,
                "porcentaje_merma": 0.0
            }
        ]
    }).json()

    # Crear Orden de producción para 50 unidades (5 batches de 10)
    # Consumo teórico esperado de azúcar = 50 * (2.0 / 10) = 10.0 kg
    order_res = client.post("/v1/production/orders", headers=headers, json={
        "recipe_id": receta["id"],
        "cantidad_a_elaborar": 50,
        "fecha_programada": "2026-09-26",
        "descontar_inventario_inmediato": False
    })
    assert order_res.status_code == 201
    order_data = order_res.json()
    order_id = order_data["id"]
    assert order_data["estado"] == "scheduled"
    assert order_data["inventario_descontado"] is False

    # El stock de azúcar aún debe permanecer intacto (100.0 kg)
    az_stock_pre = client.get(f"/v1/inventory/ingredients/{azucar['id']}", headers=headers).json()
    assert az_stock_pre["stock_actual"] == 100.0

    # Marcar orden como 'completed' vía endpoint dedicado
    complete_res = client.post(f"/v1/production/orders/{order_id}/complete", headers=headers)
    assert complete_res.status_code == 200
    completed_order = complete_res.json()
    assert completed_order["estado"] == "completed"
    assert completed_order["inventario_descontado"] is True

    # El stock de azúcar debe haberse reducido exactamente en 10.0 kg (100.0 - 10.0 = 90.0 kg)
    az_stock_post = client.get(f"/v1/inventory/ingredients/{azucar['id']}", headers=headers).json()
    assert az_stock_post["stock_actual"] == 90.0

    # Si se intenta volver a completar la orden, no debe duplicar el descuento de inventario
    client.post(f"/v1/production/orders/{order_id}/complete", headers=headers)
    az_stock_post2 = client.get(f"/v1/inventory/ingredients/{azucar['id']}", headers=headers).json()
    assert az_stock_post2["stock_actual"] == 90.0

# -------------------------------------------------------------
# 4. TEST AISLAMIENTO MULTI-TENANT ESTRICTO
# -------------------------------------------------------------
def test_multi_tenant_isolation_production_and_inventory():
    tenant_1 = "tenant-pasteleria-1"
    tenant_2 = "tenant-pasteleria-2"

    h1 = {"X-Tenant-ID": tenant_1}
    h2 = {"X-Tenant-ID": tenant_2}

    # Insumo en Tenant 1
    ing_t1 = client.post("/v1/inventory/ingredients", headers=h1, json={
        "nombre": "Cacao Puro en Polvo",
        "unidad_medida": "kg",
        "costo_unitario_promedio": 8000.0,
        "stock_actual": 15.0
    }).json()

    # Tenant 2 no debe ver el insumo de Tenant 1
    res_list_t2 = client.get("/v1/inventory/ingredients", headers=h2).json()
    assert len(res_list_t2) == 0

    res_get_t2 = client.get(f"/v1/inventory/ingredients/{ing_t1['id']}", headers=h2)
    assert res_get_t2.status_code == 404

    # Receta en Tenant 1
    rec_t1 = client.post("/v1/production/recipes", headers=h1, json={
        "product_id": "trufas-cacao",
        "nombre_receta": "Trufas de Cacao",
        "rendimiento_porciones": 20.0,
        "ingredientes": [
            {
                "ingredient_id": ing_t1["id"],
                "cantidad_neta": 1.0,
                "porcentaje_merma": 0.0
            }
        ]
    }).json()

    # Tenant 2 no puede ver ni usar la receta de Tenant 1
    res_rec_t2 = client.get("/v1/production/recipes", headers=h2).json()
    assert len(res_rec_t2) == 0

    # Tenant 2 no puede crear órdenes con una receta ajena
    order_fail = client.post("/v1/production/orders", headers=h2, json={
        "recipe_id": rec_t1["id"],
        "cantidad_a_elaborar": 10,
        "fecha_programada": "2026-09-30"
    })
    assert order_fail.status_code == 400
    assert "no existe en el tenant" in order_fail.json()["detail"]
