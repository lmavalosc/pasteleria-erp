# API Changelog

## 1.0.0-fase1

Fecha: 2026-09-26

### Agregado

- Contrato inicial OpenAPI 3.1.
- Endpoint `/health`.
- Recursos de contabilidad:
  - `accounting_accounts`
  - `journal_entries`
  - `journal_lines`
- Recursos de facturación DTE:
  - `dte_invoices`
- Recursos de gastos:
  - `expenses`
- Recursos de documentos:
  - `documents`
- Paginación estándar.
- Errores estándar tipo Problem Details.
- Header `X-Tenant-ID` obligatorio en endpoints de negocio.
- Header opcional `Idempotency-Key` en creación.
- Montos como strings decimales.
