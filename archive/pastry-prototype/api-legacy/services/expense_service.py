import uuid
from datetime import datetime

from app.schemas.core_models import ExpenseCreateRequest, ExpenseState
from app.services.production_service import production_store


class ExpenseStore:
    def __init__(self):
        self.expenses: dict[str, dict] = {} # id -> expense

    def create(self, tenant_id: str, user_id: str, data: ExpenseCreateRequest) -> dict:
        exp_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat() + "Z"
        
        # Procesar líneas de detalle de insumos
        insumos_procesados = []
        if data.insumos_detalle:
            for item in data.insumos_detalle:
                item_id = str(uuid.uuid4())
                subtotal = float(item.cantidad) * float(item.precio_unitario)
                
                # Actualizar el Precio Promedio Ponderado (PPP) en el inventario del tenant
                ing = production_store.apply_purchase_ppp(
                    tenant_id=tenant_id,
                    ingredient_id=item.ingredient_id,
                    nombre_insumo=item.nombre_insumo,
                    cantidad_comprada=float(item.cantidad),
                    precio_unitario_compra=float(item.precio_unitario),
                    unidad_medida=item.unidad_medida
                )

                insumos_procesados.append({
                    "id": item_id,
                    "ingredient_id": ing["id"] if ing else item.ingredient_id,
                    "nombre_insumo": item.nombre_insumo,
                    "cantidad": float(item.cantidad),
                    "unidad_medida": item.unidad_medida,
                    "precio_unitario": float(item.precio_unitario),
                    "subtotal": round(subtotal, 2)
                })

        expense = {
            "id": exp_id,
            "tenant_id": tenant_id,
            "folio_comprobante": data.folio_comprobante,
            "proveedor_nombre": data.proveedor_nombre,
            "proveedor_rut": data.proveedor_rut,
            "fecha_gasto": data.fecha_gasto,
            "monto_neto": data.monto_neto,
            "monto_iva": data.monto_iva,
            "monto_total": data.monto_total,
            "moneda": data.moneda,
            "categoria_gasto": data.categoria_gasto.value,
            "metodo_pago": data.metodo_pago.value,
            "estado": ExpenseState.PENDING_APPROVAL.value,
            "document_id": data.document_id,
            "insumos_detalle": insumos_procesados,
            "created_by_user_id": user_id,
            "approved_by_user_id": None,
            "motivo_rechazo": None,
            "created_at": now
        }
        self.expenses[exp_id] = expense
        return expense

    def get_by_id(self, exp_id: str, tenant_id: str) -> dict | None:
        exp = self.expenses.get(exp_id)
        if exp and exp["tenant_id"] == tenant_id:
            return exp
        return None

    def list_expenses(
        self,
        tenant_id: str,
        estado: str | None = None,
        categoria: str | None = None,
        fecha_desde: str | None = None,
        fecha_hasta: str | None = None,
        page: int = 1,
        page_size: int = 20
    ) -> list[dict]:
        res = [e for e in self.expenses.values() if e["tenant_id"] == tenant_id]
        if estado:
            res = [e for e in res if e["estado"] == estado]
        if categoria:
            res = [e for e in res if e["categoria_gasto"] == categoria]
        if fecha_desde:
            res = [e for e in res if e["fecha_gasto"] >= fecha_desde]
        if fecha_hasta:
            res = [e for e in res if e["fecha_gasto"] <= fecha_hasta]
        
        res.sort(key=lambda x: x["fecha_gasto"], reverse=True)
        start = (page - 1) * page_size
        return res[start:start + page_size]

    def approve(self, exp_id: str, tenant_id: str, approver_user_id: str) -> dict | None:
        exp = self.get_by_id(exp_id, tenant_id)
        if not exp:
            return None
        exp["estado"] = ExpenseState.APPROVED.value
        exp["approved_by_user_id"] = approver_user_id
        return exp

    def reject(self, exp_id: str, tenant_id: str, approver_user_id: str, motivo: str) -> dict | None:
        exp = self.get_by_id(exp_id, tenant_id)
        if not exp:
            return None
        exp["estado"] = ExpenseState.REJECTED.value
        exp["approved_by_user_id"] = approver_user_id
        exp["motivo_rechazo"] = motivo
        return exp

expense_store = ExpenseStore()
