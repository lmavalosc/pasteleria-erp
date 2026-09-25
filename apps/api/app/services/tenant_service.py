from typing import Dict, Optional, List
from datetime import datetime
import uuid
from app.core.security import get_password_hash, verify_password

class TenantStore:
    def __init__(self):
        self.tenants: Dict[str, dict] = {}
        self.users: Dict[str, dict] = {}
        self.memberships: Dict[str, dict] = {} # id -> membership

        # Initial demo tenant & user for immediate local testing
        default_user_id = str(uuid.uuid4())
        default_tenant_id = "default-tenant-001"
        self.tenants[default_tenant_id] = {
            "id": default_tenant_id,
            "rut_o_identificador": "76.123.456-7",
            "razon_social": "Pasteleria Demo SpA",
            "nombre_fantasia": "Dulce Delicia",
            "plan": "starter",
            "estado": "activo",
            "created_at": datetime.utcnow().isoformat()
        }
        self.users[default_user_id] = {
            "id": default_user_id,
            "email": "admin@pasteleria.local",
            "password_hash": get_password_hash("Admin123!"),
            "nombre_completo": "Administrador Pasteleria",
            "activo": True,
            "created_at": datetime.utcnow().isoformat()
        }
        mem_id = str(uuid.uuid4())
        self.memberships[mem_id] = {
            "id": mem_id,
            "tenant_id": default_tenant_id,
            "user_id": default_user_id,
            "rol": "owner",
            "created_at": datetime.utcnow().isoformat()
        }

    def get_user_by_email(self, email: str) -> Optional[dict]:
        for u in self.users.values():
            if u["email"].lower() == email.lower():
                return u
        return None

    def get_user_by_id(self, user_id: str) -> Optional[dict]:
        return self.users.get(user_id)

    def get_membership(self, tenant_id: str, user_id: str) -> Optional[dict]:
        for m in self.memberships.values():
            if m["tenant_id"] == tenant_id and m["user_id"] == user_id:
                return m
        return None

    def get_user_memberships(self, user_id: str) -> List[dict]:
        return [m for m in self.memberships.values() if m["user_id"] == user_id]

    def create_user_and_tenant(self, email: str, password: str, nombre_completo: str, razon_social: str, rut_o_identificador: Optional[str] = None, nombre_fantasia: Optional[str] = None):
        user_id = str(uuid.uuid4())
        tenant_id = str(uuid.uuid4())
        mem_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        tenant = {
            "id": tenant_id,
            "rut_o_identificador": rut_o_identificador or "SIN-RUT",
            "razon_social": razon_social,
            "nombre_fantasia": nombre_fantasia or razon_social,
            "plan": "starter",
            "estado": "activo",
            "created_at": now
        }
        self.tenants[tenant_id] = tenant

        user = {
            "id": user_id,
            "email": email.lower(),
            "password_hash": get_password_hash(password),
            "nombre_completo": nombre_completo,
            "activo": True,
            "created_at": now
        }
        self.users[user_id] = user

        membership = {
            "id": mem_id,
            "tenant_id": tenant_id,
            "user_id": user_id,
            "rol": "owner",
            "created_at": now
        }
        self.memberships[mem_id] = membership

        return tenant, user, membership

tenant_store = TenantStore()
