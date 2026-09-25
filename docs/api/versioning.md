# Versionado de API

## Estrategia

Usamos versionado por URL.

La Fase 1 expone:

`/api/v1`

El contrato OpenAPI vive en:

`openapi/fase1.yaml`

## Reglas de versión

### Patch

Cambios compatibles y menores:

- Corrección de descripciones.
- Corrección de ejemplos.
- Corrección de errores tipográficos.
- Cambios que no afectan clientes.

Ejemplo:

`1.0.0` -> `1.0.1`

### Minor

Cambios compatibles hacia atrás:

- Nuevos endpoints.
- Nuevos campos opcionales.
- Nuevos valores en enums, si los clientes pueden tolerarlos.
- Nuevos query params opcionales.

Ejemplo:

`1.0.x` -> `1.1.0`

### Major

Cambios incompatibles:

- Eliminar endpoints.
- Eliminar campos.
- Cambiar tipo de un campo.
- Hacer obligatorio un campo que antes era opcional.
- Cambiar semántica de un recurso.

Ejemplo:

`1.x.x` -> `2.0.0`

## Política Fase 1

Durante Fase 1 se evita major.

Si un cambio rompe compatibilidad, se documenta en:

`openapi/CHANGELOG.md`

y se planifica migración a `/api/v2`.

## Tenant

En Fase 1, el tenant se transmite mediante header:

`X-Tenant-ID`

En producción, el backend debe derivar el tenant desde autenticación y membresías.

El cliente nunca debe enviar `tenant_id` en el body de creación.

## Dinero

Los montos se representan como strings decimales con hasta 2 decimales.

Ejemplo:

`"1500.00"`

No se usan números JSON para dinero.

## Errores

Todos los errores usan Problem Details.

Schema: `ProblemDetail` (RFC 7807)
