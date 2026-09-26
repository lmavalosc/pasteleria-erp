# Diccionario de Datos — Fase 1 (PostgreSQL)

## 1. Convenciones Globales de Ingeniería de Datos

- **Identificadores primarios:** `UUID PRIMARY KEY DEFAULT gen_random_uuid()` (evita enumeración predecible y colisiones en replicación o migración).
- **Moneda y montos contables:** `NUMERIC(18, 2)` (estricto punto fijo, prohibido `FLOAT` o `DOUBLE PRECISION` para evitar errores de redondeo financiero).
- **Cantidades físicas y unidades:** `NUMERIC(18, 3)` (permite decimales para fraccionamiento en kilos, litros, unidades).
- **Tasas porcentuales:** `NUMERIC(5, 2)` (ej. `19.00` para IVA).
- **Fechas y horas:** `TIMESTAMPTZ` en UTC para eventos y auditoría; `DATE` sin zona horaria para fechas de imputación contable o emisión tributaria.
- **Triggers automáticos de auditoría:** Trigger `trg_{table}_updated_at` actualiza automáticamente la columna `updated_at = NOW()` antes de cada `UPDATE`.
- **Estrategia Multi-Tenant:** Toda tabla de negocio incluye `tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE` con políticas **Row Level Security (RLS)** activadas y forzadas a nivel de motor.

---

## 2. Clasificación de Tablas por Nivel de Aislamiento

| Tabla | Dominio | Alcance de Aislamiento | Política Row Level Security (RLS) |
|---|---|---|---|
| `tenants` | Identidad | Global (Directorio de Empresas) | No aplica (administración de tenants) |
| `users` | Identidad | Global (Cuentas de Usuario) | No aplica (usuarios globales) |
| `memberships` | Identidad / RBAC | N:M Tenant-User | No aplica / Filtrado por consulta |
| `accounting_accounts` | Contabilidad | **Aislado por Tenant** | **Activo & Forzado (`app.tenant_id`)** |
| `journal_entries` | Contabilidad | **Aislado por Tenant** | **Activo & Forzado (`app.tenant_id`)** |
| `journal_lines` | Contabilidad | **Aislado por Tenant** | **Activo & Forzado (`app.tenant_id`)** |
| `documents` | Operaciones | **Aislado por Tenant** | **Activo & Forzado (`app.tenant_id`)** |
| `expenses` | Operaciones | **Aislado por Tenant** | **Activo & Forzado (`app.tenant_id`)** |
| `dte_invoices` | Tributario | **Aislado por Tenant** | **Activo & Forzado (`app.tenant_id`)** |
| `dte_invoice_items` | Tributario | **Aislado por Tenant** | **Activo & Forzado (`app.tenant_id`)** |

---

## 3. Especificación Detallada de Entidades

### 1. `tenants`
Empresas u organizaciones dadas de alta en la plataforma.

| Campo | Tipo | Nulo | Restricciones / Default | Descripción |
|---|---|---|---|---|
| `id` | `UUID` | No | PK, `gen_random_uuid()` | Identificador universal único de la empresa |
| `name` | `TEXT` | No | — | Razón social o nombre comercial |
| `tax_id` | `TEXT` | Sí | — | Identificador tributario (RUT en Chile) |
| `status` | `TEXT` | No | Default `'active'`, `CHECK (status IN ('active', 'suspended', 'deleted'))` | Estado operativo del tenant |
| `created_at` | `TIMESTAMPTZ` | No | Default `NOW()` | Fecha y hora de creación |
| `updated_at` | `TIMESTAMPTZ` | No | Default `NOW()` | Última actualización |

- **Índices:**
  - `idx_tenants_status` en `(status)`

---

### 2. `users`
Identidades de usuario globales en el sistema (un usuario puede pertenecer a múltiples tenants).

| Campo | Tipo | Nulo | Restricciones / Default | Descripción |
|---|---|---|---|---|
| `id` | `UUID` | No | PK, `gen_random_uuid()` | Identificador de usuario |
| `email` | `TEXT` | No | Unique, `CHECK (email = LOWER(email))` | Correo normalizado en minúsculas |
| `name` | `TEXT` | Sí | — | Nombre completo del usuario |
| `password_hash` | `TEXT` | Sí | — | Hash de contraseña (NULL en desarrollo/OAuth) |
| `status` | `TEXT` | No | Default `'active'`, `CHECK (status IN ('active', 'invited', 'disabled', 'deleted'))` | Estado de la cuenta de usuario |
| `created_at` | `TIMESTAMPTZ` | No | Default `NOW()` | Fecha y hora de registro |
| `updated_at` | `TIMESTAMPTZ` | No | Default `NOW()` | Última actualización |

- **Restricción de unicidad:** `UNIQUE (email)`

---

### 3. `memberships`
Vínculo N:M entre usuarios y empresas con control de acceso basado en roles (RBAC).

| Campo | Tipo | Nulo | Restricciones / Default | Descripción |
|---|---|---|---|---|
| `id` | `UUID` | No | PK, `gen_random_uuid()` | Identificador de membresía |
| `tenant_id` | `UUID` | No | FK `tenants(id) ON DELETE CASCADE` | Empresa a la que pertenece el usuario |
| `user_id` | `UUID` | No | FK `users(id) ON DELETE CASCADE` | Usuario asociado |
| `role` | `TEXT` | No | Default `'member'`, `CHECK (role IN ('owner', 'admin', 'accountant', 'approver', 'member', 'viewer'))` | Rol operativo en la empresa |
| `created_at` | `TIMESTAMPTZ` | No | Default `NOW()` | Fecha de asignación |

- **Restricción de unicidad:** `UNIQUE (tenant_id, user_id)`
- **Índices:**
  - `idx_memberships_tenant` en `(tenant_id)`
  - `idx_memberships_user` en `(user_id)`

---

### 4. `accounting_accounts`
Catálogo y plan de cuentas contables parametrizable por empresa bajo estándar IFRS.

| Campo | Tipo | Nulo | Restricciones / Default | Descripción |
|---|---|---|---|---|
| `id` | `UUID` | No | PK, `gen_random_uuid()` | Identificador único de la cuenta |
| `tenant_id` | `UUID` | No | FK `tenants(id) ON DELETE CASCADE` | Tenant propietario (RLS activo) |
| `parent_id` | `UUID` | Sí | FK `accounting_accounts(id) ON DELETE SET NULL` | Cuenta padre (jerarquía contable) |
| `code` | `TEXT` | No | `CHECK (code ~ '^[0-9.]{1,25}$')` | Código estructurado (ej. `1110101` o `1.1.01`) |
| `name` | `TEXT` | No | — | Glosa descriptiva de la cuenta |
| `account_type` | `TEXT` | No | `CHECK (account_type IN ('asset', 'liability', 'equity', 'income', 'expense'))` | Clasificación bajo estándar contable IFRS |
| `is_active` | `BOOLEAN` | No | Default `TRUE` | Permite imputación contable si es TRUE |
| `created_at` | `TIMESTAMPTZ` | No | Default `NOW()` | Fecha de creación |
| `updated_at` | `TIMESTAMPTZ` | No | Default `NOW()` | Última actualización |

- **Restricción de unicidad:** `UNIQUE (tenant_id, code)` (permite mismo código contable en diferentes tenants)
- **Índices:**
  - `idx_accounting_accounts_tenant` en `(tenant_id)`
  - `idx_accounting_accounts_type` en `(tenant_id, account_type)`
  - `idx_accounting_accounts_active` en `(tenant_id, is_active)`
  - `idx_accounting_accounts_parent` en `(tenant_id, parent_id)`

---

### 5. `journal_entries`
Cabeceras de los comprobantes y asientos del libro diario contable.

| Campo | Tipo | Nulo | Restricciones / Default | Descripción |
|---|---|---|---|---|
| `id` | `UUID` | No | PK, `gen_random_uuid()` | Identificador del asiento |
| `tenant_id` | `UUID` | No | FK `tenants(id) ON DELETE CASCADE` | Tenant propietario (RLS activo) |
| `entry_date` | `DATE` | No | — | Fecha contable de devengo |
| `description` | `TEXT` | No | — | Glosa general del comprobante |
| `status` | `TEXT` | No | Default `'draft'`, `CHECK (status IN ('draft', 'posted', 'voided'))` | Estado del comprobante |
| `total_debit` | `NUMERIC(18,2)`| No | Default `0`, `CHECK (total_debit >= 0)` | Sumatoria total de débitos |
| `total_credit`| `NUMERIC(18,2)`| No | Default `0`, `CHECK (total_credit >= 0)` | Sumatoria total de créditos |
| `posted_at` | `TIMESTAMPTZ` | Sí | — | Momento en que pasa a estado posted |
| `created_at` | `TIMESTAMPTZ` | No | Default `NOW()` | Fecha de registro |
| `updated_at` | `TIMESTAMPTZ` | No | Default `NOW()` | Última actualización |

- **Restricción de partida doble:** `CHECK (total_debit = total_credit)`
- **Índices:**
  - `idx_journal_entries_tenant_date` en `(tenant_id, entry_date)`
  - `idx_journal_entries_tenant_status` en `(tenant_id, status)`

---

### 6. `journal_lines`
Partidas contables de detalle que componen cada asiento.

| Campo | Tipo | Nulo | Restricciones / Default | Descripción |
|---|---|---|---|---|
| `id` | `UUID` | No | PK, `gen_random_uuid()` | Identificador de la partida |
| `tenant_id` | `UUID` | No | FK `tenants(id) ON DELETE CASCADE` | Tenant propietario (RLS activo) |
| `entry_id` | `UUID` | No | FK `journal_entries(id) ON DELETE CASCADE` | Asiento cabecera |
| `account_id` | `UUID` | No | FK `accounting_accounts(id) ON DELETE RESTRICT`| Cuenta contable imputada |
| `debit` | `NUMERIC(18,2)`| No | Default `0`, `CHECK (debit >= 0)` | Monto imputado al debe |
| `credit` | `NUMERIC(18,2)`| No | Default `0`, `CHECK (credit >= 0)` | Monto imputado al haber |
| `memo` | `TEXT` | Sí | — | Glosa o detalle de la línea |
| `created_at` | `TIMESTAMPTZ` | No | Default `NOW()` | Fecha de inserción |

- **Reglas de partida pura (Check constraints):**
  - `CHECK (NOT (debit = 0 AND credit = 0))` (prohíbe líneas neutras sin monto)
  - `CHECK (NOT (debit > 0 AND credit > 0))` (prohíbe imputación simultánea a debe y haber en una misma línea)
- **Índices:**
  - `idx_journal_lines_tenant` en `(tenant_id)`
  - `idx_journal_lines_entry` en `(tenant_id, entry_id)`
  - `idx_journal_lines_account` en `(tenant_id, account_id)`

---

### 7. `documents`
Metadatos de archivos adjuntos (PDFs tributarios, boletas físicas escaneadas, comprobantes bancarios).

| Campo | Tipo | Nulo | Restricciones / Default | Descripción |
|---|---|---|---|---|
| `id` | `UUID` | No | PK, `gen_random_uuid()` | Identificador del archivo |
| `tenant_id` | `UUID` | No | FK `tenants(id) ON DELETE CASCADE` | Tenant propietario (RLS activo) |
| `filename` | `TEXT` | No | — | Nombre original del archivo |
| `mime_type` | `TEXT` | No | — | Tipo MIME (ej. `application/pdf`, `image/png`) |
| `size_bytes` | `BIGINT` | No | Default `0`, `CHECK (size_bytes >= 0)` | Peso en bytes |
| `checksum_sha256` | `TEXT`| Sí | `CHECK (checksum_sha256 ~ '^[a-fA-F0-9]{64}$')` | Hash SHA-256 para integridad |
| `storage_provider`| `TEXT`| No | Default `'local'`, `CHECK (storage_provider IN ('local', 's3', 'gcs', 'azure'))` | Backend de almacenamiento |
| `storage_uri`| `TEXT` | No | — | URI o ruta relativa del objeto |
| `created_at` | `TIMESTAMPTZ` | No | Default `NOW()` | Fecha de subida |

- **Índices:**
  - `idx_documents_tenant` en `(tenant_id)`
  - `idx_documents_created_at` en `(tenant_id, created_at DESC)`

---

### 8. `expenses`
Rendición y control de gastos operacionales y compras no centralizadas por DTE.

| Campo | Tipo | Nulo | Restricciones / Default | Descripción |
|---|---|---|---|---|
| `id` | `UUID` | No | PK, `gen_random_uuid()` | Identificador del gasto |
| `tenant_id` | `UUID` | No | FK `tenants(id) ON DELETE CASCADE` | Tenant propietario (RLS activo) |
| `expense_date`| `DATE` | No | — | Fecha en que ocurrió el desembolso |
| `amount` | `NUMERIC(18,2)`| No | `CHECK (amount >= 0)` | Monto del gasto |
| `currency` | `TEXT` | No | Default `'CLP'`, `CHECK (currency IN ('CLP', 'USD'))` | Moneda de registro |
| `status` | `TEXT` | No | Default `'draft'`, `CHECK (status IN ('draft', 'submitted', 'approved', 'paid', 'rejected'))` | Estado en el flujo de aprobación |
| `document_id`| `UUID` | Sí | FK `documents(id) ON DELETE SET NULL` | Respaldo digital adjunto |
| `description`| `TEXT` | Sí | — | Justificación o detalle |
| `merchant` | `TEXT` | Sí | — | Comercio, proveedor o emisor |
| `created_at` | `TIMESTAMPTZ` | No | Default `NOW()` | Creación |
| `updated_at` | `TIMESTAMPTZ` | No | Default `NOW()` | Actualización |

- **Índices:**
  - `idx_expenses_tenant_date` en `(tenant_id, expense_date)`
  - `idx_expenses_tenant_status` en `(tenant_id, status)`
  - `idx_expenses_document` en `(tenant_id, document_id)`

---

### 9. `dte_invoices`
Encabezados de Documentos Tributarios Electrónicos normados según normativa SII Chile.

| Campo | Tipo | Nulo | Restricciones / Default | Descripción |
|---|---|---|---|---|
| `id` | `UUID` | No | PK, `gen_random_uuid()` | Identificador de factura/DTE |
| `tenant_id` | `UUID` | No | FK `tenants(id) ON DELETE CASCADE` | Tenant propietario (RLS activo) |
| `dte_type` | `TEXT` | No | `CHECK (dte_type IN ('33','34','39','41','43','45','46','52','56','61','110','111','112'))` | Código oficial del tipo de DTE SII |
| `folio` | `INTEGER` | No | `CHECK (folio > 0)` | Número de folio asignado |
| `issue_date` | `DATE` | No | — | Fecha de emisión legal del DTE |
| `status` | `TEXT` | No | Default `'draft'`, `CHECK (status IN ('draft', 'issued', 'accepted', 'rejected', 'annulled'))` | Estado ante el SII / interno |
| `currency` | `TEXT` | No | Default `'CLP'`, `CHECK (currency IN ('CLP', 'USD'))` | Moneda del DTE |
| `recipient_rut`| `TEXT` | Sí | — | RUT del receptor |
| `recipient_name`| `TEXT`| Sí | — | Razón social del receptor |
| `subtotal` | `NUMERIC(18,2)`| Sí | — | Monto neto afecto o exento |
| `tax_amount` | `NUMERIC(18,2)`| Sí | — | Monto del IVA (19%) o impuestos específicos |
| `total` | `NUMERIC(18,2)`| No | `CHECK (total >= 0)` | Monto bruto final facturado |
| `sii_receipt_uri`| `TEXT` | Sí | — | Enlace o referencia al acuse de recibo SII |
| `sii_track_id`| `TEXT` | Sí | — | Track ID del envío al SII |
| `emitted_at` | `TIMESTAMPTZ` | Sí | — | Estampa de tiempo de timbraje |
| `created_at` | `TIMESTAMPTZ` | No | Default `NOW()` | Creación |
| `updated_at` | `TIMESTAMPTZ` | No | Default `NOW()` | Actualización |

- **Restricción de unicidad tributaria legal:** `UNIQUE (tenant_id, dte_type, folio)`
- **Índices:**
  - `idx_dte_invoices_tenant_date` en `(tenant_id, issue_date)`
  - `idx_dte_invoices_tenant_status` en `(tenant_id, status)`
  - `idx_dte_invoices_tenant_type` en `(tenant_id, dte_type)`

---

### 10. `dte_invoice_items`
Detalle ítem por ítem del contenido del DTE.

| Campo | Tipo | Nulo | Restricciones / Default | Descripción |
|---|---|---|---|---|
| `id` | `UUID` | No | PK, `gen_random_uuid()` | Identificador de línea del DTE |
| `tenant_id` | `UUID` | No | FK `tenants(id) ON DELETE CASCADE` | Tenant propietario (RLS activo) |
| `dte_invoice_id`| `UUID` | No | FK `dte_invoices(id) ON DELETE CASCADE` | DTE cabecera |
| `line_number`| `INTEGER` | No | `CHECK (line_number > 0)` | Número ordinal de línea en el XML |
| `description`| `TEXT` | No | — | Nombre o descripción del ítem/servicio |
| `quantity` | `NUMERIC(18,3)`| No | Default `1`, `CHECK (quantity >= 0)` | Unidades o métrica física |
| `unit_price` | `NUMERIC(18,2)`| No | `CHECK (unit_price >= 0)` | Precio unitario neto |
| `discount` | `NUMERIC(18,2)`| No | Default `0`, `CHECK (discount >= 0)` | Descuento aplicado |
| `tax_rate` | `NUMERIC(5,2)` | No | Default `19.00` | Tasa de impuesto porcentual |
| `tax_amount` | `NUMERIC(18,2)`| No | Default `0`, `CHECK (tax_amount >= 0)` | Impuesto calculado de la línea |
| `line_total` | `NUMERIC(18,2)`| No | `CHECK (line_total >= 0)` | Total final de la línea |
| `account_id` | `UUID` | Sí | FK `accounting_accounts(id) ON DELETE SET NULL`| Pre-imputación a cuenta contable |
| `created_at` | `TIMESTAMPTZ` | No | Default `NOW()` | Creación |

- **Restricción de unicidad:** `UNIQUE (dte_invoice_id, line_number)`
- **Índices:**
  - `idx_dte_invoice_items_tenant` en `(tenant_id)`
  - `idx_dte_invoice_items_invoice` en `(tenant_id, dte_invoice_id)`
  - `idx_dte_invoice_items_account` en `(tenant_id, account_id)`
