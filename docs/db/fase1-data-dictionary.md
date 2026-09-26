# Diccionario de Datos — Fase 1 (PostgreSQL)

## Convenciones Globales
- **Identificadores primarios:** `UUID PRIMARY KEY DEFAULT gen_random_uuid()`
- **Moneda y montos contables:** `NUMERIC(18, 2)` (estricto, sin coma flotante)
- **Cantidades físicas:** `NUMERIC(18, 3)` o `NUMERIC(12, 4)`
- **Fechas y horas:** `TIMESTAMPTZ` en UTC para eventos; `DATE` para fechas de emisión y devengo
- **Triggers automáticos:** `trg_{table}_updated_at` actualiza la columna `updated_at` antes de cada `UPDATE`

---

## 1. tenants
Empresas u organizaciones dadas de alta en la plataforma.

| Campo | Tipo | Nulo | Restricciones / Default | Descripción |
|---|---|---|---|---|
| `id` | `UUID` | No | PK, `gen_random_uuid()` | Identificador universal único |
| `name` | `TEXT` | No | — | Razón social o nombre comercial |
| `tax_id` | `TEXT` | Sí | — | Identificador fiscal (RUT en Chile) |
| `status` | `TEXT` | No | Default `'active'`, `CHECK (status IN ('active', 'suspended', 'deleted'))` | Estado operativo del tenant |
| `created_at` | `TIMESTAMPTZ` | No | Default `NOW()` | Fecha y hora de creación |
| `updated_at` | `TIMESTAMPTZ` | No | Default `NOW()` | Última actualización |

- **Índices:** `idx_tenants_status` en `(status)`

---

## 2. users
Identidades de usuario globales en el sistema.

| Campo | Tipo | Nulo | Restricciones / Default | Descripción |
|---|---|---|---|---|
| `id` | `UUID` | No | PK, `gen_random_uuid()` | Identificador de usuario |
| `email` | `TEXT` | No | Unique, `CHECK (email = LOWER(email))` | Correo normalizado en minúsculas |
| `name` | `TEXT` | Sí | — | Nombre completo del usuario |
| `password_hash` | `TEXT` | Sí | — | Hash de contraseña (NULL en desarrollo/OAuth) |
| `status` | `TEXT` | No | Default `'active'`, `CHECK (status IN ('active', 'invited', 'disabled', 'deleted'))` | Estado de la cuenta |
| `created_at` | `TIMESTAMPTZ` | No | Default `NOW()` | Fecha y hora de registro |
| `updated_at` | `TIMESTAMPTZ` | No | Default `NOW()` | Última actualización |

---

## 3. memberships
Vínculo N:M entre usuarios y empresas con control de acceso basado en roles (RBAC).

| Campo | Tipo | Nulo | Restricciones / Default | Descripción |
|---|---|---|---|---|
| `id` | `UUID` | No | PK, `gen_random_uuid()` | Identificador de membresía |
| `tenant_id` | `UUID` | No | FK `tenants(id) ON DELETE CASCADE` | Empresa a la que pertenece |
| `user_id` | `UUID` | No | FK `users(id) ON DELETE CASCADE` | Usuario asociado |
| `role` | `TEXT` | No | Default `'member'`, `CHECK (role IN ('owner', 'admin', 'accountant', 'approver', 'member', 'viewer'))` | Rol operativo |
| `created_at` | `TIMESTAMPTZ` | No | Default `NOW()` | Fecha de asignación |

- **Restricción de unicidad:** `UNIQUE (tenant_id, user_id)`
- **Índices:** `idx_memberships_tenant` en `(tenant_id)`, `idx_memberships_user` en `(user_id)`

---

## 4. accounting_accounts
Catálogo y plan de cuentas contables parametrizable por empresa.

| Campo | Tipo | Nulo | Restricciones / Default | Descripción |
|---|---|---|---|---|
| `id` | `UUID` | No | PK, `gen_random_uuid()` | Identificador de cuenta |
| `tenant_id` | `UUID` | No | FK `tenants(id) ON DELETE CASCADE` | Tenant propietario (RLS activo) |
| `parent_id` | `UUID` | Sí | FK `accounting_accounts(id) ON DELETE SET NULL` | Cuenta padre (jerarquía) |
| `code` | `TEXT` | No | `CHECK (code ~ '^[0-9.]{1,25}$')` | Código estructurado (ej. `1110101` o `1.1.01`) |
| `name` | `TEXT` | No | — | Glosa o descripción de la cuenta |
| `account_type` | `TEXT` | No | `CHECK (account_type IN ('asset', 'liability', 'equity', 'income', 'expense'))` | Clasificación bajo estándar IFRS |
| `is_active` | `BOOLEAN` | No | Default `TRUE` | Permite imputación |
| `created_at` | `TIMESTAMPTZ` | No | Default `NOW()` | Fecha de creación |
| `updated_at` | `TIMESTAMPTZ` | No | Default `NOW()` | Última actualización |

- **Restricción de unicidad:** `UNIQUE (tenant_id, code)`
- **Índices:** `idx_accounting_accounts_tenant`, `idx_accounting_accounts_type`, `idx_accounting_accounts_active`, `idx_accounting_accounts_parent`

---

## 5. journal_entries
Cabeceras de los comprobantes y asientos del libro diario.

| Campo | Tipo | Nulo | Restricciones / Default | Descripción |
|---|---|---|---|---|
| `id` | `UUID` | No | PK, `gen_random_uuid()` | Identificador del asiento |
| `tenant_id` | `UUID` | No | FK `tenants(id) ON DELETE CASCADE` | Tenant propietario (RLS activo) |
| `entry_date` | `DATE` | No | — | Fecha contable de imputación |
| `description` | `TEXT` | No | — | Glosa general del asiento |
| `status` | `TEXT` | No | Default `'draft'`, `CHECK (status IN ('draft', 'posted', 'voided'))` | Estado del comprobante |
| `total_debit` | `NUMERIC(18,2)`| No | Default `0`, `CHECK (total_debit >= 0)` | Sumatoria total de débitos |
| `total_credit`| `NUMERIC(18,2)`| No | Default `0`, `CHECK (total_credit >= 0)` | Sumatoria total de créditos |
| `posted_at` | `TIMESTAMPTZ` | Sí | — | Momento en que pasa a posted |
| `created_at` | `TIMESTAMPTZ` | No | Default `NOW()` | Creación |
| `updated_at` | `TIMESTAMPTZ` | No | Default `NOW()` | Actualización |

- **Restricción de balance:** `CHECK (total_debit = total_credit)`
- **Índices:** `idx_journal_entries_tenant_date` en `(tenant_id, entry_date)`, `idx_journal_entries_tenant_status` en `(tenant_id, status)`

---

## 6. journal_lines
Partidas contables de detalle que componen cada asiento.

| Campo | Tipo | Nulo | Restricciones / Default | Descripción |
|---|---|---|---|---|
| `id` | `UUID` | No | PK, `gen_random_uuid()` | Identificador de la partida |
| `tenant_id` | `UUID` | No | FK `tenants(id) ON DELETE CASCADE` | Tenant propietario (RLS activo) |
| `entry_id` | `UUID` | No | FK `journal_entries(id) ON DELETE CASCADE` | Asiento cabecera |
| `account_id` | `UUID` | No | FK `accounting_accounts(id) ON DELETE RESTRICT`| Cuenta contable imputada |
| `debit` | `NUMERIC(18,2)`| No | Default `0`, `CHECK (debit >= 0)` | Monto al debe |
| `credit` | `NUMERIC(18,2)`| No | Default `0`, `CHECK (credit >= 0)` | Monto al haber |
| `memo` | `TEXT` | Sí | — | Glosa específica de la línea |
| `created_at` | `TIMESTAMPTZ` | No | Default `NOW()` | Fecha de inserción |

- **Constraints de partida doble:**
  - `CHECK (NOT (debit = 0 AND credit = 0))` (prohíbe líneas neutras)
  - `CHECK (NOT (debit > 0 AND credit > 0))` (prohíbe doble imputación simultánea)
- **Índices:** `idx_journal_lines_tenant`, `idx_journal_lines_entry`, `idx_journal_lines_account`

---

## 7. documents
Metadatos de archivos adjuntos (PDFs tributarios, boletas, comprobantes bancarios).

| Campo | Tipo | Nulo | Restricciones / Default | Descripción |
|---|---|---|---|---|
| `id` | `UUID` | No | PK, `gen_random_uuid()` | Identificador del archivo |
| `tenant_id` | `UUID` | No | FK `tenants(id) ON DELETE CASCADE` | Tenant propietario (RLS activo) |
| `filename` | `TEXT` | No | — | Nombre original del archivo |
| `mime_type` | `TEXT` | No | — | Tipo de contenido (ej. `application/pdf`) |
| `size_bytes` | `BIGINT` | No | Default `0`, `CHECK (size_bytes >= 0)` | Peso en bytes |
| `checksum_sha256` | `TEXT`| Sí | `CHECK (checksum_sha256 ~ '^[a-fA-F0-9]{64}$')` | Hash de integridad SHA-256 |
| `storage_provider`| `TEXT`| No | Default `'local'`, `CHECK (storage_provider IN ('local', 's3', 'gcs', 'azure'))` | Backend de almacenamiento |
| `storage_uri`| `TEXT` | No | — | URI o ruta relativa del objeto |
| `created_at` | `TIMESTAMPTZ` | No | Default `NOW()` | Fecha de subida |

- **Índices:** `idx_documents_tenant`, `idx_documents_created_at` en `(tenant_id, created_at DESC)`

---

## 8. expenses
Rendición y control de gastos operacionales y compras no centralizadas por DTE.

| Campo | Tipo | Nulo | Restricciones / Default | Descripción |
|---|---|---|---|---|
| `id` | `UUID` | No | PK, `gen_random_uuid()` | Identificador del gasto |
| `tenant_id` | `UUID` | No | FK `tenants(id) ON DELETE CASCADE` | Tenant propietario (RLS activo) |
| `expense_date`| `DATE` | No | — | Fecha del desembolso |
| `amount` | `NUMERIC(18,2)`| No | `CHECK (amount >= 0)` | Monto del gasto |
| `currency` | `TEXT` | No | Default `'CLP'`, `CHECK (currency IN ('CLP', 'USD'))` | Moneda de registro |
| `status` | `TEXT` | No | Default `'draft'`, `CHECK (status IN ('draft', 'submitted', 'approved', 'paid', 'rejected'))` | Flujo de aprobación |
| `document_id`| `UUID` | Sí | FK `documents(id) ON DELETE SET NULL` | Comprobante digital adjunto |
| `description`| `TEXT` | Sí | — | Justificación o detalle |
| `merchant` | `TEXT` | Sí | — | Comercio o proveedor |
| `created_at` | `TIMESTAMPTZ` | No | Default `NOW()` | Creación |
| `updated_at` | `TIMESTAMPTZ` | No | Default `NOW()` | Actualización |

- **Índices:** `idx_expenses_tenant_date`, `idx_expenses_tenant_status`, `idx_expenses_document`

---

## 9. dte_invoices
Encabezados de Documentos Tributarios Electrónicos normados según normativa SII.

| Campo | Tipo | Nulo | Restricciones / Default | Descripción |
|---|---|---|---|---|
| `id` | `UUID` | No | PK, `gen_random_uuid()` | Identificador de factura/DTE |
| `tenant_id` | `UUID` | No | FK `tenants(id) ON DELETE CASCADE` | Tenant propietario (RLS activo) |
| `dte_type` | `TEXT` | No | `CHECK (dte_type IN ('33','34','39','41','43','45','46','52','56','61','110','111','112'))` | Código del tipo de documento SII |
| `folio` | `INTEGER` | No | `CHECK (folio > 0)` | Número de folio asignado |
| `issue_date` | `DATE` | No | — | Fecha de emisión tributaria |
| `status` | `TEXT` | No | Default `'draft'`, `CHECK (status IN ('draft', 'issued', 'accepted', 'rejected', 'annulled'))` | Estado ante el SII / interno |
| `currency` | `TEXT` | No | Default `'CLP'`, `CHECK (currency IN ('CLP', 'USD'))` | Moneda del DTE |
| `recipient_rut`| `TEXT` | Sí | — | RUT del receptor |
| `recipient_name`| `TEXT`| Sí | — | Razón social del receptor |
| `subtotal` | `NUMERIC(18,2)`| Sí | — | Monto neto o afecto |
| `tax_amount` | `NUMERIC(18,2)`| Sí | — | Monto del IVA (19%) o impuestos específicos |
| `total` | `NUMERIC(18,2)`| No | `CHECK (total >= 0)` | Monto bruto final facturado |
| `sii_receipt_uri`| `TEXT` | Sí | — | Enlace o referencia al acuse de recibo SII |
| `sii_track_id`| `TEXT` | Sí | — | Track ID del envío al SII |
| `emitted_at` | `TIMESTAMPTZ` | Sí | — | Estampa de tiempo de firma/timbraje |
| `created_at` | `TIMESTAMPTZ` | No | Default `NOW()` | Creación |
| `updated_at` | `TIMESTAMPTZ` | No | Default `NOW()` | Actualización |

- **Restricción de unicidad tributaria:** `UNIQUE (tenant_id, dte_type, folio)`
- **Índices:** `idx_dte_invoices_tenant_date`, `idx_dte_invoices_tenant_status`, `idx_dte_invoices_tenant_type`

---

## 10. dte_invoice_items
Detalle ítem por ítem del contenido del DTE.

| Campo | Tipo | Nulo | Restricciones / Default | Descripción |
|---|---|---|---|---|
| `id` | `UUID` | No | PK, `gen_random_uuid()` | Identificador de línea |
| `tenant_id` | `UUID` | No | FK `tenants(id) ON DELETE CASCADE` | Tenant propietario (RLS activo) |
| `dte_invoice_id`| `UUID` | No | FK `dte_invoices(id) ON DELETE CASCADE` | DTE cabecera |
| `line_number`| `INTEGER` | No | `CHECK (line_number > 0)` | Número ordinal de línea en el XML |
| `description`| `TEXT` | No | — | Nombre o descripción del ítem/servicio |
| `quantity` | `NUMERIC(18,3)`| No | Default `1`, `CHECK (quantity >= 0)` | Unidades o métrica |
| `unit_price` | `NUMERIC(18,2)`| No | `CHECK (unit_price >= 0)` | Precio unitario neto |
| `discount` | `NUMERIC(18,2)`| No | Default `0`, `CHECK (discount >= 0)` | Descuento aplicado al ítem |
| `tax_rate` | `NUMERIC(5,2)` | No | Default `19.00` | Tasa de impuesto porcentual |
| `tax_amount` | `NUMERIC(18,2)`| No | Default `0`, `CHECK (tax_amount >= 0)` | Impuesto calculado de la línea |
| `line_total` | `NUMERIC(18,2)`| No | `CHECK (line_total >= 0)` | Total final de la línea |
| `account_id` | `UUID` | Sí | FK `accounting_accounts(id) ON DELETE SET NULL`| Pre-imputación a cuenta contable |
| `created_at` | `TIMESTAMPTZ` | No | Default `NOW()` | Creación |

- **Restricción de unicidad:** `UNIQUE (dte_invoice_id, line_number)`
- **Índices:** `idx_dte_invoice_items_tenant`, `idx_dte_invoice_items_invoice`, `idx_dte_invoice_items_account`
