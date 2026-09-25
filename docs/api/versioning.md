# Versioning Policy - Maison du Délice API

## 1. SemVer (Semantic Versioning)
Esta API sigue el estándar [SemVer 2.0.0](https://semver.org/):
- **MAJOR (`v1` -> `v2`):** Cambios incompatibles hacia atrás (breaking changes). Por ejemplo, eliminación de campos requeridos, cambio de endpoints base, o reestructuración incompatible de modelos.
- **MINOR (`1.0` -> `1.1`):** Nuevos endpoints o atributos opcionales compatibles hacia atrás.
- **PATCH (`1.0.0` -> `1.0.1`):** Correcciones de bugs, mejoras en descripciones, o ajustes internos sin impacto en el contrato.

## 2. Prefijo en URLs
Todos los endpoints están versionados en la ruta con `/api/v1/`:
- Desarrollo Local: `http://localhost:4000/api/v1/...`
- Staging / Prod: `https://api.pasteleria-delice.com/api/v1/...`

## 3. Contrato como Fuente Única de Verdad
1. `openapi/fase1.yaml` es la única fuente de verdad para clientes y servidor.
2. Todo cambio de contrato debe reflejarse en `docs/api/changelog.md` y `openapi/fase1.yaml`.
3. Los tipos de TypeScript en `packages/shared-types` y `packages/api-client` se generan automáticamente (`npm run generate:types` y `npm run generate:api`).
4. `apps/web` y `apps/mobile` no crean tipos manuales ni rutas ad-hoc; consumen exclusivamente los tipos generados y `@pasteleria/api-client`.

## 4. Política de Aislamiento Multi-Tenant
1. Todos los endpoints operativos exigen el header `X-Tenant-ID`.
2. Las respuestas devuelven siempre el campo `tenant_id` garantizando trazabilidad y validación cruzada.
3. Se prohíbe exponer datos entre tenants distintos.

## 5. Manejo de Montos Financieros
1. Todo valor monetario debe expresarse como `NonNegativeDecimalString` con expresión regular `^\d+(\.\d{1,2})?$`.
2. Se prohíbe el uso de tipos `number` flotantes IEEE-754 para montos en moneda, previniendo errores de redondeo en cálculos contables y costos de receta.
