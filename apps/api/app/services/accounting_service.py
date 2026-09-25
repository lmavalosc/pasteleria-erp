from typing import Dict, Optional, List
from datetime import datetime
from decimal import Decimal
import uuid
from app.schemas.core_models import AccountType, AccountResponse, JournalEntryCreateRequest, JournalEntryState

# Standard Chilean chart of accounts template
CHILEAN_DEFAULT_ACCOUNTS = [
    # Activos
    {"codigo": "1.1.01", "nombre": "Caja y Efectivo", "tipo": AccountType.ACTIVO},
    {"codigo": "1.1.02", "nombre": "Banco Cuenta Corriente", "tipo": AccountType.ACTIVO},
    {"codigo": "1.1.03", "nombre": "Clientes Nacionales", "tipo": AccountType.ACTIVO},
    {"codigo": "1.1.04", "nombre": "IVA Credito Fiscal", "tipo": AccountType.ACTIVO},
    {"codigo": "1.1.05", "nombre": "Inventario Materias Primas", "tipo": AccountType.ACTIVO},
    # Pasivos
    {"codigo": "2.1.01", "nombre": "Proveedores Nacionales", "tipo": AccountType.PASIVO},
    {"codigo": "2.1.02", "nombre": "IVA Debito Fiscal", "tipo": AccountType.PASIVO},
    {"codigo": "2.1.03", "nombre": "Retenciones por Pagar (PPM/Honorarios)", "tipo": AccountType.PASIVO},
    # Patrimonio
    {"codigo": "3.1.01", "nombre": "Capital Pagado", "tipo": AccountType.PATRIMONIO},
    {"codigo": "3.1.02", "nombre": "Resultados Acumulados", "tipo": AccountType.PATRIMONIO},
    # Ingresos
    {"codigo": "4.1.01", "nombre": "Ventas de Pasteleria y Panaderia", "tipo": AccountType.INGRESO},
    {"codigo": "4.1.02", "nombre": "Ingresos por Servicios de Catering", "tipo": AccountType.INGRESO},
    # Gastos / Costos
    {"codigo": "5.1.01", "nombre": "Costo de Ventas (Harinas, Lacteos, etc.)", "tipo": AccountType.GASTO},
    {"codigo": "5.1.02", "nombre": "Gastos de Envoltorios y Packaging", "tipo": AccountType.GASTO},
    {"codigo": "5.1.03", "nombre": "Remuneraciones y Sueldos", "tipo": AccountType.GASTO},
    {"codigo": "5.1.04", "nombre": "Servicios Basicos (Luz, Agua, Gas)", "tipo": AccountType.GASTO},
    {"codigo": "5.1.05", "nombre": "Arriendo Local Comercial", "tipo": AccountType.GASTO},
]

class AccountingStore:
    def __init__(self):
        self.accounts: Dict[str, dict] = {} # id -> account
        self.entries: Dict[str, dict] = {} # id -> entry
        self.correlatives: Dict[str, int] = {} # tenant_id -> current_number

    def seed_defaults(self, tenant_id: str) -> List[dict]:
        existing_codes = {a["codigo"] for a in self.accounts.values() if a["tenant_id"] == tenant_id}
        created = []
        for tpl in CHILEAN_DEFAULT_ACCOUNTS:
            if tpl["codigo"] not in existing_codes:
                acc_id = str(uuid.uuid4())
                acc = {
                    "id": acc_id,
                    "tenant_id": tenant_id,
                    "codigo": tpl["codigo"],
                    "nombre": tpl["nombre"],
                    "tipo": tpl["tipo"].value,
                    "activa": True
                }
                self.accounts[acc_id] = acc
                created.append(acc)
        return created

    def list_accounts(self, tenant_id: str) -> List[dict]:
        accs = [a for a in self.accounts.values() if a["tenant_id"] == tenant_id]
        if not accs:
            # Seed automatically on first read if empty
            accs = self.seed_defaults(tenant_id)
        accs.sort(key=lambda x: x["codigo"])
        return accs

    def get_account_by_id(self, acc_id: str, tenant_id: str) -> Optional[dict]:
        acc = self.accounts.get(acc_id)
        if acc and acc["tenant_id"] == tenant_id:
            return acc
        return None

    def create_entry(self, tenant_id: str, data: JournalEntryCreateRequest) -> dict:
        entry_id = str(uuid.uuid4())
        curr_num = self.correlatives.get(tenant_id, 0) + 1
        self.correlatives[tenant_id] = curr_num

        items = []
        for line in data.items:
            items.append({
                "id": str(uuid.uuid4()),
                "entry_id": entry_id,
                "account_id": line.account_id,
                "debe": line.debe,
                "haber": line.haber,
                "contacto_rut_o_nombre": line.contacto_rut_o_nombre
            })

        entry = {
            "id": entry_id,
            "tenant_id": tenant_id,
            "numero_asiento": curr_num,
            "fecha_asiento": data.fecha_asiento,
            "glosa_descripcion": data.glosa_descripcion,
            "estado": JournalEntryState.DRAFT.value,
            "referencia_origen": data.referencia_origen or "MANUAL",
            "items": items,
            "created_at": datetime.utcnow().isoformat()
        }
        self.entries[entry_id] = entry
        return entry

    def get_entry(self, entry_id: str, tenant_id: str) -> Optional[dict]:
        e = self.entries.get(entry_id)
        if e and e["tenant_id"] == tenant_id:
            return e
        return None

    def post_entry(self, entry_id: str, tenant_id: str) -> dict:
        entry = self.get_entry(entry_id, tenant_id)
        if not entry:
            raise ValueError("Asiento no encontrado.")

        if entry["estado"] == JournalEntryState.POSTED.value:
            return entry # Already posted

        if entry["estado"] == JournalEntryState.VOIDED.value:
            raise ValueError("Un asiento anulado no puede ser publicado.")

        # Strict Double-Entry Validation: sum(Debe) == sum(Haber)
        total_debe = sum(Decimal(str(item["debe"])) for item in entry["items"])
        total_haber = sum(Decimal(str(item["haber"])) for item in entry["items"])

        if total_debe != total_haber:
            diff = abs(total_debe - total_haber)
            raise ValueError(
                f"El asiento contable no está cuadrado (Partida Doble violada). Debe total: {total_debe}, Haber total: {total_haber}, Diferencia: {diff}"
            )

        if len(entry["items"]) < 2:
            raise ValueError("Un asiento contable debe tener al menos dos líneas.")

        entry["estado"] = JournalEntryState.POSTED.value
        return entry

    def void_entry(self, entry_id: str, tenant_id: str) -> dict:
        entry = self.get_entry(entry_id, tenant_id)
        if not entry:
            raise ValueError("Asiento no encontrado.")

        entry["estado"] = JournalEntryState.VOIDED.value
        return entry

accounting_store = AccountingStore()
