-- ============================================================================
-- PASTELERÍA ARTESANAL & REPOSTERÍA DE AUTOR — FASE 1
-- ESQUEMA RELACIONAL POSTGRESQL MULTI-TENANT CON TENANT_ID
-- ============================================================================
-- Cumple con:
-- 1. ADR 0001: Esquema compartido con tenant_id en todas las tablas de negocio.
-- 2. Claves primarias compuestas / Foráneas que incluyen tenant_id para integridad estricta.
-- 3. Índices B-Tree optimizados para filtros obligatorios por tenant_id.
-- 4. Soporte nativo para Row Level Security (RLS) habilitado.
-- ============================================================================

-- Habilitar extensión para generación de identificadores UUID v4
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- 1. NÚCLEO DE TENANTS Y ACCESO
-- ============================================================================

CREATE TABLE IF NOT EXISTS tenants (
    id VARCHAR(64) PRIMARY KEY,
    razon_social VARCHAR(255) NOT NULL,
    rut_o_identificador VARCHAR(32),
    nombre_fantasia VARCHAR(255),
    moneda_principal VARCHAR(10) NOT NULL DEFAULT 'CLP',
    activo BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nombre_completo VARCHAR(255) NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tenant_memberships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(64) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    rol VARCHAR(32) NOT NULL DEFAULT 'member' CHECK (rol IN ('owner', 'admin', 'accountant', 'cashier', 'member')),
    activo BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_tenant_user UNIQUE (tenant_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_memberships_tenant ON tenant_memberships(tenant_id);
CREATE INDEX IF NOT EXISTS idx_memberships_user ON tenant_memberships(user_id);

-- ============================================================================
-- 2. BÓVEDA DE DOCUMENTOS (Comprobantes, Boletas, Facturas adjuntas)
-- ============================================================================

CREATE TABLE IF NOT EXISTS documents (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(64) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    filename_original VARCHAR(255) NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    file_size_bytes BIGINT NOT NULL CHECK (file_size_bytes >= 0),
    storage_uri TEXT NOT NULL,
    checksum_sha256 VARCHAR(64) NOT NULL,
    uploaded_by_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, tenant_id)
);

CREATE INDEX IF NOT EXISTS idx_documents_tenant_created ON documents(tenant_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_documents_checksum ON documents(tenant_id, checksum_sha256);

-- ============================================================================
-- 3. INVENTARIO DE INSUMOS & PRECIO PROMEDIO PONDERADO (PPP)
-- ============================================================================

CREATE TABLE IF NOT EXISTS inventory_ingredients (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(64) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    codigo VARCHAR(64),
    nombre VARCHAR(255) NOT NULL,
    unidad_medida VARCHAR(20) NOT NULL CHECK (unidad_medida IN ('kg', 'g', 'l', 'ml', 'unidad')),
    costo_unitario_promedio NUMERIC(14, 2) NOT NULL DEFAULT 0.0 CHECK (costo_unitario_promedio >= 0),
    stock_actual NUMERIC(14, 4) NOT NULL DEFAULT 0.0,
    alergenos JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, tenant_id),
    CONSTRAINT uq_ingredient_code UNIQUE (tenant_id, codigo)
);

CREATE INDEX IF NOT EXISTS idx_ingredients_tenant_name ON inventory_ingredients(tenant_id, nombre);

-- ============================================================================
-- 4. EGRESOS / GASTOS CON DETALLE DE LÍNEAS DE INSUMOS
-- ============================================================================

CREATE TABLE IF NOT EXISTS expenses (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(64) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    folio_comprobante VARCHAR(64),
    proveedor_nombre VARCHAR(255) NOT NULL,
    proveedor_rut VARCHAR(32),
    fecha_gasto DATE NOT NULL,
    monto_neto NUMERIC(14, 2) NOT NULL CHECK (monto_neto >= 0),
    monto_iva NUMERIC(14, 2) NOT NULL DEFAULT 0.0 CHECK (monto_iva >= 0),
    monto_total NUMERIC(14, 2) NOT NULL CHECK (monto_total >= 0),
    moneda VARCHAR(10) NOT NULL DEFAULT 'CLP',
    categoria_gasto VARCHAR(50) NOT NULL DEFAULT 'materias_primas' 
        CHECK (categoria_gasto IN ('materias_primas', 'packaging', 'servicios', 'arriendo', 'otros')),
    metodo_pago VARCHAR(50) NOT NULL DEFAULT 'transferencia'
        CHECK (metodo_pago IN ('transferencia', 'efectivo', 'tarjeta_credito')),
    estado VARCHAR(32) NOT NULL DEFAULT 'pending_approval'
        CHECK (estado IN ('draft', 'pending_approval', 'approved', 'rejected')),
    document_id UUID,
    motivo_rechazo TEXT,
    created_by_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    approved_by_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, tenant_id),
    FOREIGN KEY (document_id, tenant_id) REFERENCES documents(id, tenant_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_expenses_tenant_date ON expenses(tenant_id, fecha_gasto DESC);
CREATE INDEX IF NOT EXISTS idx_expenses_tenant_estado ON expenses(tenant_id, estado);

CREATE TABLE IF NOT EXISTS expense_items (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(64) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    expense_id UUID NOT NULL,
    ingredient_id UUID,
    nombre_insumo VARCHAR(255) NOT NULL,
    cantidad NUMERIC(14, 4) NOT NULL CHECK (cantidad > 0),
    unidad_medida VARCHAR(20) NOT NULL DEFAULT 'kg',
    precio_unitario NUMERIC(14, 2) NOT NULL CHECK (precio_unitario >= 0),
    subtotal NUMERIC(14, 2) NOT NULL CHECK (subtotal >= 0),
    PRIMARY KEY (id, tenant_id),
    FOREIGN KEY (expense_id, tenant_id) REFERENCES expenses(id, tenant_id) ON DELETE CASCADE,
    FOREIGN KEY (ingredient_id, tenant_id) REFERENCES inventory_ingredients(id, tenant_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_expense_items_expense ON expense_items(tenant_id, expense_id);
CREATE INDEX IF NOT EXISTS idx_expense_items_ingredient ON expense_items(tenant_id, ingredient_id);

-- ============================================================================
-- 5. RECETAS, ESCANDALLOS Y PRODUCCIÓN
-- ============================================================================

CREATE TABLE IF NOT EXISTS recipes (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(64) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    product_id VARCHAR(64) NOT NULL,
    nombre_receta VARCHAR(255) NOT NULL,
    rendimiento_porciones NUMERIC(10, 2) NOT NULL DEFAULT 1.0 CHECK (rendimiento_porciones > 0),
    tiempo_elaboracion_minutos INTEGER NOT NULL DEFAULT 60 CHECK (tiempo_elaboracion_minutos > 0),
    costo_total_batch NUMERIC(14, 2) NOT NULL DEFAULT 0.0 CHECK (costo_total_batch >= 0),
    costo_por_porcion NUMERIC(14, 2) NOT NULL DEFAULT 0.0 CHECK (costo_por_porcion >= 0),
    instrucciones TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, tenant_id)
);

CREATE INDEX IF NOT EXISTS idx_recipes_tenant_product ON recipes(tenant_id, product_id);

CREATE TABLE IF NOT EXISTS recipe_ingredients (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(64) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    recipe_id UUID NOT NULL,
    ingredient_id UUID NOT NULL,
    cantidad_neta NUMERIC(14, 4) NOT NULL CHECK (cantidad_neta > 0),
    porcentaje_merma NUMERIC(5, 2) NOT NULL DEFAULT 0.0 CHECK (porcentaje_merma >= 0),
    costo_calculado NUMERIC(14, 2) NOT NULL DEFAULT 0.0 CHECK (costo_calculado >= 0),
    PRIMARY KEY (id, tenant_id),
    FOREIGN KEY (recipe_id, tenant_id) REFERENCES recipes(id, tenant_id) ON DELETE CASCADE,
    FOREIGN KEY (ingredient_id, tenant_id) REFERENCES inventory_ingredients(id, tenant_id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_recipe ON recipe_ingredients(tenant_id, recipe_id);

CREATE TABLE IF NOT EXISTS recipe_packagings (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(64) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    recipe_id UUID NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    costo_unitario NUMERIC(14, 2) NOT NULL CHECK (costo_unitario >= 0),
    cantidad NUMERIC(10, 2) NOT NULL DEFAULT 1.0 CHECK (cantidad > 0),
    PRIMARY KEY (id, tenant_id),
    FOREIGN KEY (recipe_id, tenant_id) REFERENCES recipes(id, tenant_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_recipe_packagings_recipe ON recipe_packagings(tenant_id, recipe_id);

CREATE TABLE IF NOT EXISTS production_orders (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(64) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    numero_orden VARCHAR(64) NOT NULL,
    recipe_id UUID NOT NULL,
    product_id VARCHAR(64) NOT NULL,
    cantidad_a_elaborar INTEGER NOT NULL CHECK (cantidad_a_elaborar > 0),
    estado VARCHAR(32) NOT NULL DEFAULT 'scheduled'
        CHECK (estado IN ('scheduled', 'in_prep', 'baking', 'finished', 'completed', 'cancelled')),
    fecha_programada DATE NOT NULL,
    fecha_finalizada TIMESTAMPTZ,
    responsable_chef VARCHAR(255),
    inventario_descontado BOOLEAN NOT NULL DEFAULT false,
    notas TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, tenant_id),
    FOREIGN KEY (recipe_id, tenant_id) REFERENCES recipes(id, tenant_id) ON DELETE RESTRICT,
    CONSTRAINT uq_order_number UNIQUE (tenant_id, numero_orden)
);

CREATE INDEX IF NOT EXISTS idx_orders_tenant_estado ON production_orders(tenant_id, estado);
CREATE INDEX IF NOT EXISTS idx_orders_tenant_fecha ON production_orders(tenant_id, fecha_programada);

-- ============================================================================
-- 6. CONTABILIDAD (PLAN DE CUENTAS & ASIENTOS DE PARTIDA DOBLE)
-- ============================================================================

CREATE TABLE IF NOT EXISTS accounting_accounts (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(64) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    codigo VARCHAR(32) NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    tipo VARCHAR(32) NOT NULL CHECK (tipo IN ('activo', 'pasivo', 'patrimonio', 'ingreso', 'gasto')),
    activa BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, tenant_id),
    CONSTRAINT uq_account_code UNIQUE (tenant_id, codigo)
);

CREATE INDEX IF NOT EXISTS idx_accounts_tenant ON accounting_accounts(tenant_id, activa);

CREATE TABLE IF NOT EXISTS journal_entries (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(64) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    numero_asiento BIGINT NOT NULL,
    fecha_asiento DATE NOT NULL,
    glosa_descripcion TEXT NOT NULL,
    estado VARCHAR(32) NOT NULL DEFAULT 'posted' CHECK (estado IN ('draft', 'posted', 'voided')),
    referencia_origen VARCHAR(64) NOT NULL DEFAULT 'MANUAL',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, tenant_id),
    CONSTRAINT uq_entry_number UNIQUE (tenant_id, numero_asiento)
);

CREATE INDEX IF NOT EXISTS idx_entries_tenant_date ON journal_entries(tenant_id, fecha_asiento);

CREATE TABLE IF NOT EXISTS journal_items (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(64) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    entry_id UUID NOT NULL,
    account_id UUID NOT NULL,
    debe NUMERIC(14, 2) NOT NULL DEFAULT 0.0 CHECK (debe >= 0),
    haber NUMERIC(14, 2) NOT NULL DEFAULT 0.0 CHECK (haber >= 0),
    contacto_rut_o_nombre VARCHAR(255),
    PRIMARY KEY (id, tenant_id),
    FOREIGN KEY (entry_id, tenant_id) REFERENCES journal_entries(id, tenant_id) ON DELETE CASCADE,
    FOREIGN KEY (account_id, tenant_id) REFERENCES accounting_accounts(id, tenant_id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_journal_items_entry ON journal_items(tenant_id, entry_id);
CREATE INDEX IF NOT EXISTS idx_journal_items_account ON journal_items(tenant_id, account_id);

-- ============================================================================
-- 7. TRIBUTARIO Y DTE (Documentos Tributarios Electrónicos)
-- ============================================================================

CREATE TABLE IF NOT EXISTS dtes (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(64) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    tipo_dte INTEGER NOT NULL CHECK (tipo_dte IN (33, 39, 61)), -- 33: Factura, 39: Boleta, 61: Nota Crédito
    folio BIGINT NOT NULL,
    fecha_emision DATE NOT NULL,
    emisor_rut VARCHAR(32) NOT NULL,
    receptor_rut VARCHAR(32) NOT NULL,
    receptor_razon_social VARCHAR(255) NOT NULL,
    monto_neto NUMERIC(14, 2) NOT NULL CHECK (monto_neto >= 0),
    monto_exento NUMERIC(14, 2) NOT NULL DEFAULT 0.0 CHECK (monto_exento >= 0),
    monto_iva NUMERIC(14, 2) NOT NULL DEFAULT 0.0 CHECK (monto_iva >= 0),
    monto_total NUMERIC(14, 2) NOT NULL CHECK (monto_total >= 0),
    estado_sii VARCHAR(32) NOT NULL DEFAULT 'draft'
        CHECK (estado_sii IN ('draft', 'generated', 'sent_to_sii', 'accepted_by_sii', 'rejected_by_sii')),
    track_id_sii VARCHAR(64),
    xml_payload_uri TEXT,
    order_id VARCHAR(64),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, tenant_id),
    CONSTRAINT uq_dte_folio UNIQUE (tenant_id, tipo_dte, folio)
);

CREATE INDEX IF NOT EXISTS idx_dtes_tenant_folio ON dtes(tenant_id, tipo_dte, folio);
CREATE INDEX IF NOT EXISTS idx_dtes_tenant_fecha ON dtes(tenant_id, fecha_emision DESC);

-- ============================================================================
-- 8. POLÍTICAS DE ROW LEVEL SECURITY (RLS) COMO DEFENSA EN PROFUNDIDAD
-- ============================================================================
-- Configuración preparada para cuando la sesión de base de datos establezca:
-- SET LOCAL app.current_tenant = 'tenant-id-aqui';

ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory_ingredients ENABLE ROW LEVEL SECURITY;
ALTER TABLE expenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE expense_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE recipes ENABLE ROW LEVEL SECURITY;
ALTER TABLE recipe_ingredients ENABLE ROW LEVEL SECURITY;
ALTER TABLE recipe_packagings ENABLE ROW LEVEL SECURITY;
ALTER TABLE production_orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE accounting_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE journal_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE journal_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE dtes ENABLE ROW LEVEL SECURITY;

-- Políticas de aislamiento por tenant activo en sesión
DO $$
DECLARE
    tbl text;
BEGIN
    FOR tbl IN 
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public' 
          AND tablename IN (
            'documents', 'inventory_ingredients', 'expenses', 'expense_items',
            'recipes', 'recipe_ingredients', 'recipe_packagings', 'production_orders',
            'accounting_accounts', 'journal_entries', 'journal_items', 'dtes'
          )
    LOOP
        EXECUTE format('
            CREATE POLICY tenant_isolation_policy ON %I
            AS PERMISSIVE
            FOR ALL
            USING (tenant_id = NULLIF(current_setting(''app.current_tenant'', true), ''''))
            WITH CHECK (tenant_id = NULLIF(current_setting(''app.current_tenant'', true), ''''));
        ', tbl);
    END LOOP;
END $$;
