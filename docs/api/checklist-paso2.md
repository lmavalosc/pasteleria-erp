# Checklist de Verificación — Paso 2

## Paso 2 — Contrato de API versionado

- [x] Existe `openapi/fase1.yaml`.
- [x] El OpenAPI usa versión `1.0.0-fase1`.
- [x] El server base es `/api/v1`.
- [x] Existe `docs/api/versioning.md`.
- [x] Existe `openapi/CHANGELOG.md`.
- [x] `pnpm openapi:lint` pasa sin errores.
- [x] `pnpm generate:types` genera `packages/shared-types/src/openapi.ts`.
- [x] `packages/shared-types` exporta `paths`, `components` y `operations`.
- [x] `packages/api-client` usa `openapi-fetch` tipado.
- [x] `ApiError` y `unwrap` existen.
- [x] Web consume `/health` mediante `@repo/api-client`.
- [x] Mobile consume `/health` mediante `@repo/api-client`.
- [x] No hay interfaces de negocio duplicadas manualmente en web/mobile.
- [x] Los montos son strings decimales (`NonNegativeDecimalString` / `DecimalString`).
- [x] Los errores usan `ProblemDetail` (RFC 7807).
- [x] Los listados usan paginación estándar (`page`, `page_size`, `PageMeta`).
- [x] Los endpoints de negocio requieren `X-Tenant-ID`.
- [x] Los objetos de respuesta incluyen `tenant_id`.
- [x] No se implementó lógica de SII todavía.
- [x] No hay secretos en el repo.
- [x] CI valida OpenAPI y tipos generados (`.github/workflows/contract.yml`).
