# ADR 0002: Modelo multi-tenant en PostgreSQL

## Estado

Aceptado para Fase 1.

## Contexto

La plataforma debe dar soporte a múltiples empresas/tenants dentro del mismo sistema. Cada tenant requiere aislamiento lógico y estricto sobre:

- Plan de cuentas contable (`accounting_accounts`).
- Asientos y partidas contables (`journal_entries`, `journal_lines`).
- Documentos tributarios electrónicos (`dte_invoices`, `dte_invoice_items`).
- Rendición y gestión de gastos (`expenses`).
- Archivos y respaldos asociados (`documents`).

Se evaluaron tres arquitecturas de multi-tenancy:
1. **Shared schema con discriminador `tenant_id`:** Una única base de datos y esquema (`public`), con columna `tenant_id UUID NOT NULL` en todas las tablas de negocio.
2. **Schema-per-tenant:** Una única base de datos con esquemas PostgreSQL aislados (`tenant_001`, `tenant_002`, etc.).
3. **Database-per-tenant:** Una base de datos física/lógica independiente por cliente.

## Decisión

Se adopta **Shared schema PostgreSQL con columna `tenant_id`** en todas las tablas de negocio como modelo principal, complementado con **Row Level Security (RLS)** activado en PostgreSQL como salvaguarda a nivel de motor.

No se utilizará *schema-per-tenant* ni *database-per-tenant* durante la Fase 1.

## Motivos

1. **Simplicidad operativa y de despliegue:** Una sola base de datos y un único ciclo de migraciones con Alembic. Se eliminan los bucles DDL multi-esquema y el riesgo de migraciones parciales/rotas.
2. **Compatibilidad nativa con PgBouncer:** Permite el uso de pooling en modo transacción (`pool_mode = transaction`) sin problemas derivados de la mutación de `search_path`.
3. **Optimización de recursos:** Evita el bloat del catálogo del sistema (`pg_class`) que ocurre al mantener cientos de esquemas repetidos.
4. **Agilidad en desarrollo local:** Todo el equipo corre una instancia estándar de PostgreSQL sin complejidad de aprovisionamiento por script.
5. **Consultas cross-tenant y reportería:** Permite a usuarios multi-empresa (contadores, auditores) alternar contextos o generar agregaciones sin saltar entre conexiones o esquemas.

## Consecuencias

- **Diseño relacional:** Toda tabla de negocio debe incluir `tenant_id UUID NOT NULL REFERENCES tenants(id)`.
- **Índices obligatorios:** Las claves foráneas y búsquedas recurrentes deben indexarse con prefijo de tenant: `(tenant_id, created_at)`, `(tenant_id, account_id)`.
- **Seguridad en backend:** 
  - La aplicación nunca debe confiar ciegamente en cabeceras arbitrarias (como `X-Tenant-ID`) en producción; el `tenant_id` debe validarse contra la autenticación del usuario y la tabla `memberships`.
  - Las transacciones de FastAPI deben inyectar el contexto de tenant en la sesión (`SET LOCAL app.current_tenant_id = :tenant_id`).
- **Defensa en profundidad con RLS:** Las tablas de negocio contarán con políticas RLS (`FOR ALL USING (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid)`).
- **Separación de roles:**
  - Migraciones y DDL se ejecutan con el usuario administrador/owner (`nucleo`).
  - La aplicación en runtime operará con un usuario de privilegios acotados (`app_user`), garantizando que RLS no sea omitido como ocurriría con un superusuario.
