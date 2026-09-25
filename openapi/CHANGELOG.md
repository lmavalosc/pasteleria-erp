# Changelog del Contrato OpenAPI

Todas las modificaciones del contrato formal de la API (`openapi/fase1.yaml`) se documentan en este archivo siguiendo [Semantic Versioning (SemVer)](https://semver.org/lang/es/) y la metodología [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/).

---

## [1.0.0-fase1] - 2026-09-25

### Añadido (Added)
- **Especificación Formal:** Contrato base OpenAPI 3.1.0 para el núcleo transaccional de Fase 1.
- **Sistema (`/health` & `/api/v1/health`):** Endpoint de monitoreo de disponibilidad y salud del servicio por tenant.
- **Finanzas y Contabilidad (`/accounting`):**
  - `/accounting/accounts`: Catálogo y plan de cuentas (Activos, Pasivos, Patrimonio, Ingresos, Costos).
  - `/accounting/journal-entries`: Asientos de diario contable con balance de partida doble.
- **Facturación Tributaria DTE (`/invoicing/dte`):**
  - Registro interno y emisión simulada de Boletas Electrónicas (Tipo 39), Facturas Electrónicas (Tipo 33) y Notas de Crédito (Tipo 61) para el SII de Chile.
- **Egresos y Rendición de Gastos (`/expenses`):**
  - Registro de facturas y boletas de proveedores con desglose de insumos comprados (kilos, litros, precios unitarios).
  - Flujo de estados: `draft`, `pending_approval`, `approved`, `rejected`.
- **Bóveda de Documentos (`/documents`):**
  - Subida de comprobantes digitales (PDF, PNG, JPG) con huella criptográfica SHA-256 y metadata de almacenamiento por empresa.
- **Flujo de Producción y Costeo (`/inventory` & `/production`):**
  - `/inventory/ingredients`: Inventario de materias primas con actualización de Precio Promedio Ponderado (PPP).
  - `/production/recipes`: Fichas técnicas / escandallos con porcentaje de merma técnica y packaging.
  - `/production/costing/{productId}`: Análisis de rentabilidad en tiempo real (costo por porción vs. precio de venta y alerta de margen bajo).
  - `/production/orders`: Órdenes de horneado con deducción automática de stock.

### Convenciones y Seguridad (Security & Conventions)
- **Aislamiento Multi-Tenant:** Todos los endpoints de negocio requieren el encabezado `X-Tenant-ID` en Fase 1 y responden siempre con `tenant_id` en los objetos devueltos.
- **Precisión Monetaria:** Definición del tipo `NonNegativeDecimalString` con regex `^\d+(\.\d{1,2})?$` para erradicar errores de punto flotante en cálculos contables.
- **Formato Estándar de Errores:** Adopción de RFC 7807 (*Problem Details*) con desglose campo por campo en respuestas 4xx y 5xx.
- **Idempotencia:** Cabecera opcional `Idempotency-Key` (UUID v4) preparada para transacciones críticas.
