# Changelog de la API - Maison du Délice

Todas las modificaciones al contrato formal de la API se registran en este documento de acuerdo a [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/) y [SemVer](https://semver.org/).

---

## [1.0.0-fase1] - 2026-09-25

### Añadido (Added)
- **Versionado Unificado:** Prefijo formal `/api/v1` en todos los endpoints expuestos (`/api/v1/health`, `/api/v1/accounting/*`, `/api/v1/invoicing/*`, `/api/v1/expenses/*`, `/api/v1/documents/*`, `/api/v1/inventory/*`, `/api/v1/production/*`).
- **Encabezado Multi-Tenant:** `X-Tenant-ID` obligatorio (`required: true`) en todos los endpoints transaccionales con presencia de `tenant_id` en todas las entidades de respuesta.
- **Tipado Monetario Decimal:** Definición del esquema `NonNegativeDecimalString` con validación regex `^\d+(\.\d{1,2})?$` para montos en contabilidad, DTE, egresos, insumos y escandallos.
- **Estandarización de Errores RFC 7807:** Esquema `ProblemDetails` (`type`, `title`, `status`, `detail`, `instance`, `invalid_params`) para todas las respuestas 4xx y 5xx.
- **Estructura Uniforme de Paginación:** Envuelve listados en respuestas estructuradas con `items`, `total`, `page`, `page_size` y `total_pages`.
- **Cabecera de Idempotencia:** Soporte para el header opcional `Idempotency-Key` en operaciones de creación y mutación de estado.
- **Monitoreo de Salud:** Endpoint `/api/v1/health` que valida la respuesta del servicio y el tenant activo.
