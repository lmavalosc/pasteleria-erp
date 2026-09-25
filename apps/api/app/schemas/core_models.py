from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

# ---------------- Enums ----------------
class UserRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    ACCOUNTANT = "accountant"
    CASHIER = "cashier"
    MEMBER = "member"

class AccountType(str, Enum):
    ACTIVO = "activo"
    PASIVO = "pasivo"
    PATRIMONIO = "patrimonio"
    INGRESO = "ingreso"
    GASTO = "gasto"

class JournalEntryState(str, Enum):
    DRAFT = "draft"
    POSTED = "posted"
    VOIDED = "voided"

class ExpenseState(str, Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"

class ExpenseCategory(str, Enum):
    MATERIAS_PRIMAS = "materias_primas"
    PACKAGING = "packaging"
    SERVICIOS = "servicios"
    ARRIENDO = "arriendo"
    OTROS = "otros"

class PaymentMethod(str, Enum):
    TRANSFERENCIA = "transferencia"
    EFECTIVO = "efectivo"
    TARJETA_CREDITO = "tarjeta_credito"

class DTEState(str, Enum):
    DRAFT = "draft"
    GENERATED = "generated"
    SENT_TO_SII = "sent_to_sii"
    ACCEPTED_BY_SII = "accepted_by_sii"
    REJECTED_BY_SII = "rejected_by_sii"

class TipoDTE(int, Enum):
    FACTURA_ELECTRONICA = 33
    BOLETA_ELECTRONICA = 39
    NOTA_CREDITO = 61

# ---------------- 15.1 Auth & Tenant Schemas ----------------
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    nombre_completo: str
    razon_social: str
    rut_o_identificador: Optional[str] = None
    nombre_fantasia: Optional[str] = None

class RegisterResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    tenant_id: str
    user_id: str
    role: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    tenant_id: Optional[str] = None

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    tenant_id: str
    user_id: str
    role: str

class SwitchTenantRequest(BaseModel):
    tenant_id: str

class SwitchTenantResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    tenant_id: str
    role: str

# ---------------- 15.2 Document Schemas ----------------
class DocumentResponse(BaseModel):
    id: str
    tenant_id: str
    filename_original: str
    mime_type: str
    file_size_bytes: int
    storage_uri: str
    checksum_sha256: str
    uploaded_by_user_id: str
    created_at: str

class ExpenseItemDetail(BaseModel):
    id: str
    ingredient_id: Optional[str] = None
    nombre_insumo: str
    cantidad: float
    unidad_medida: str
    precio_unitario: float
    subtotal: float

class ExpenseItemDetailInput(BaseModel):
    ingredient_id: Optional[str] = None
    nombre_insumo: str
    cantidad: float
    unidad_medida: str
    precio_unitario: float

# ---------------- 15.3 Expense Schemas ----------------
class ExpenseCreateRequest(BaseModel):
    folio_comprobante: Optional[str] = None
    proveedor_nombre: str
    proveedor_rut: Optional[str] = None
    fecha_gasto: str # YYYY-MM-DD
    monto_neto: float
    monto_iva: float = 0.0
    monto_total: float
    moneda: str = "CLP"
    categoria_gasto: ExpenseCategory = ExpenseCategory.MATERIAS_PRIMAS
    metodo_pago: PaymentMethod = PaymentMethod.TRANSFERENCIA
    document_id: Optional[str] = None
    insumos_detalle: Optional[List[ExpenseItemDetailInput]] = None

class ExpenseRejectRequest(BaseModel):
    motivo_rechazo: str

class ExpenseResponse(BaseModel):
    id: str
    tenant_id: str
    folio_comprobante: Optional[str] = None
    proveedor_nombre: str
    proveedor_rut: Optional[str] = None
    fecha_gasto: str
    monto_neto: float
    monto_iva: float
    monto_total: float
    moneda: str
    categoria_gasto: str
    metodo_pago: str
    estado: str
    document_id: Optional[str] = None
    insumos_detalle: List[ExpenseItemDetail] = []
    created_by_user_id: str
    approved_by_user_id: Optional[str] = None
    motivo_rechazo: Optional[str] = None
    created_at: str

# ---------------- 15.4 Accounting Schemas ----------------
class AccountResponse(BaseModel):
    id: str
    tenant_id: str
    codigo: str
    nombre: str
    tipo: str
    activa: bool

class JournalItemInput(BaseModel):
    account_id: str
    debe: float = 0.0
    haber: float = 0.0
    contacto_rut_o_nombre: Optional[str] = None

class JournalItemResponse(BaseModel):
    id: str
    entry_id: str
    account_id: str
    debe: float
    haber: float
    contacto_rut_o_nombre: Optional[str] = None

class JournalEntryCreateRequest(BaseModel):
    fecha_asiento: str # YYYY-MM-DD
    glosa_descripcion: str
    referencia_origen: Optional[str] = "MANUAL"
    items: List[JournalItemInput]

class JournalEntryResponse(BaseModel):
    id: str
    tenant_id: str
    numero_asiento: int
    fecha_asiento: str
    glosa_descripcion: str
    estado: str
    referencia_origen: str
    items: List[JournalItemResponse]
    created_at: str

# ---------------- 15.5 DTE Schemas ----------------
class DTECreateRequest(BaseModel):
    tipo_dte: int # 39: Boleta, 33: Factura, 61: Nota de Credito
    folio: Optional[int] = None
    fecha_emision: str # YYYY-MM-DD
    emisor_rut: str
    receptor_rut: str
    receptor_razon_social: str
    monto_neto: float
    monto_exento: float = 0.0
    monto_iva: float
    monto_total: float
    order_id: Optional[str] = None

class DTEResponse(BaseModel):
    id: str
    tenant_id: str
    tipo_dte: int
    folio: int
    fecha_emision: str
    emisor_rut: str
    receptor_rut: str
    receptor_razon_social: str
    monto_neto: float
    monto_exento: float
    monto_iva: float
    monto_total: float
    estado_sii: str
    track_id_sii: Optional[str] = None
    xml_payload_uri: Optional[str] = None
    order_id: Optional[str] = None
    created_at: str
