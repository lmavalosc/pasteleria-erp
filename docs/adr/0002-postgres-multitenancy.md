# ADR 0002: Modelo de Datos Multi-Tenant en PostgreSQL

## Estado
**Aceptado** — Arquitectura de Referencia para Fase 1.

---

## 1. Contexto del Negocio y Requerimientos

La plataforma "PASTELERÍA" es una solución SaaS B2B orientada a la gestión contable, rendición de gastos y facturación electrónica (DTE ante el SII) para múltiples empresas (tenants). 

El sistema requiere:
1. **Aislamiento absoluto entre clientes:** Los datos contables, tributarios y financieros de una empresa jamás deben ser visibles ni modificables por otra.
2. **Alta integridad financiera:** Cumplimiento riguroso de partida doble contable e inmutabilidad de folios tributarios.
3. **Eficiencia en recursos y agilidad operativa:** Capacidad de desplegar, respaldar y migrar la infraestructura sin sobrecarga operacional en etapas iniciales.
4. **Soporte para usuarios multi-empresa:** Socios, directores y contadores externos que acceden a múltiples empresas con un único juego de credenciales pero con roles operativos independientes por tenant.

---

## 2. Opciones de Arquitectura Multi-Tenant Evaluadas

Se analizaron formalmente tres patrones arquitectónicos sobre PostgreSQL:

| Criterio | Opción A: Shared Schema + `tenant_id` + RLS | Opción B: Schema-per-Tenant | Opción C: Database-per-Tenant |
|---|---|---|---|
| **Aislamiento** | Físico compartido, lógico forzado por RLS a nivel de motor | Aislamiento por namespace de esquema de BD | Aislamiento físico de almacenamiento y motor |
| **Operación de Migraciones** | 1 ciclo determinista (Alembic DDL único) | N migraciones iterativas (riesgo de drift) | N migraciones sobre N bases de datos |
| **Connection Pooling (PgBouncer)** | Compatible con `transaction pooling` nativo | Requiere `session pooling` (mutación de `search_path`) | Pools separados por base de datos |
| **Consumo de Memoria & Catálogo** | Catálogo compacto (`pg_class` acotado) | Bloat del catálogo del sistema con >100 tenants | Consumo de RAM y conexiones multiplicado por N |
| **Consultas Cross-Tenant (Auditoría)** | Simples y directas (agregación vía SQL estándar) | Complejas (`UNION` dinámico entre esquemas) | Requiere `dblink` o ETL externo |
| **Complejidad en Desarrollo Local** | Mínima (`docker compose` estándar) | Media (scripts de inicialización multi-esquema) | Alta (múltiples servicios de BD) |

---

## 3. Decisión de Arquitectura

Se adopta la **Opción A: Shared Schema PostgreSQL con columna discriminadora `tenant_id`** en todas las tablas de negocio, blindada con **Row Level Security (RLS)** nativo de PostgreSQL activado y forzado a nivel de motor.

### Declaración de Rechazo Explícito:
**No se utilizará *Schema-per-Tenant* ni *Database-per-Tenant* durante la Fase 1.**

---

## 4. Fundamentos Técnicos del Rechazo de Schema-per-Tenant

Como Ingeniero Principal de Datos, se descarta *schema-per-tenant* en esta fase por los siguientes motivos de ingeniería:

1. **Incompatibilidad con Transaction Pooling:**
   En *schema-per-tenant*, la sesión debe alterar dinámicamente `SET search_path TO tenant_xxx`. Al utilizar PgBouncer en modo transacción (`pool_mode = transaction`) —la configuración óptima para APIs en la nube—, el `search_path` se resetea o contamina conexiones entre solicitudes HTTP concurrentes, obligando a usar `session pooling`, lo cual degrada la concurrencia y agota rápidamente el pool de conexiones de PostgreSQL.

2. **Degradación del Catálogo del Sistema (`pg_class` Bloat):**
   PostgreSQL almacena metadatos de cada tabla, índice y constraint en el catálogo global. Con 10 tablas de negocio y 25 índices por tenant, 500 clientes generarían más de 17.500 entradas en `pg_class`, degradando el performance del optimizador de consultas, invalidando caches de planes y alargando el tiempo de análisis de queries.

3. **Operaciones de Migración Frágiles y Asincrónicas:**
   Aplicar un cambio de esquema en *schema-per-tenant* requiere un bucle procedimental sobre cada esquema. Si falla en el tenant #348, la base de datos queda en estado inconsistente (drift de esquema), exigiendo mecanismos de rollback manuales de alto riesgo. Con *shared schema*, las migraciones con Alembic son atómicas y deterministas: aplican en milisegundos para todos los tenants dentro de una única transacción DDL.

4. **Escalabilidad y Backups Unificados:**
   Las tareas de backup (`pg_dump` con `pg_restore`), vacuuming y monitoreo de fragmentación se ejecutan sobre una estructura limpia y optimizada, reduciendo el Costo Total de Propiedad (TCO) de infraestructura.

---

## 5. Estrategia de Defensa en Profundidad (Dual-Layer Isolation)

El aislamiento no depende de una sola línea de defensa; se estructura en dos capas ortogonales:

```
[ Solicitud HTTP / API Gateway ]
             │
             ▼ (Capa 1: Aplicación)
┌────────────────────────────────────────────────────────┐
│ FastAPI: Validación de Membresía & Sesión Transaccional │
│ - Valida JWT / Tenant Context                          │
│ - Aplica WHERE tenant_id = :tenant_id en queries ORM   │
│ - Ejecuta: SELECT set_config('app.tenant_id', :id, true)│
└────────────────────────────────────────────────────────┘
             │
             ▼ (Capa 2: Motor PostgreSQL)
┌────────────────────────────────────────────────────────┐
│ PostgreSQL: Row Level Security (RLS) FORZADO           │
│ - Rol no privilegiado: app_user                        │
│ - Política RLS en tablas de negocio:                   │
│   USING (tenant_id = NULLIF(                           │
│     current_setting('app.tenant_id', true),            │
│     ''                                                 │
│   )::uuid)                                             │
│ - Bloqueo físico en motor ante bugs o queries directos  │
└────────────────────────────────────────────────────────┘
```

1. **Capa 1 (Aplicación / ORM):** El código del backend (`apps/api`) incluye siempre la columna `tenant_id` en filtros de consulta e inserciones, desacoplado mediante la dependencia transaccional `get_db_with_tenant`.
2. **Capa 2 (Motor de Base de Datos - RLS):** Aunque un desarrollador cometa el error de omitir el filtro `tenant_id` en una consulta raw SQL, el motor de PostgreSQL descarta físicamente los registros pertenecientes a otros tenants basándose en la variable de sesión `app.tenant_id`.

---

## 6. Modelo de Privilegios y Segregación de Roles

PostgreSQL no aplica RLS al rol `SUPERUSER` ni al rol propietario de la tabla salvo que se configure explícitamente. Para garantizar que RLS sea ineludible, se implementa una estricta segregación de roles:

1. **Rol DDL / Migrador (`nucleo`):**
   - Propietario de los esquemas, tablas, tipos y triggers.
   - Ejecuta exclusivamente las migraciones de Alembic y tareas de mantenimiento.
   - Nunca es utilizado por la API en tiempo de ejecución.
2. **Rol de Aplicación (`app_user`):**
   - Rol con privilegios mínimos (`GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES`).
   - Sin permisos DDL ni capacidad de alterar políticas RLS.
   - Sujeto irrestricto a todas las políticas de Row Level Security.
   - Las conexiones de FastAPI operan bajo este rol.

---

## 7. Estrategia de Indexación Multi-Tenant

Para evitar lecturas secuenciales completas (`Seq Scan`) conforme el volumen de datos crezca:
- **Regla de oro de índices compuestos:** Todo índice sobre tablas de negocio incluye `tenant_id` como **primera columna** (columna líder):
  - `idx_accounting_accounts_tenant_code` -> `(tenant_id, code)`
  - `idx_journal_entries_tenant_date` -> `(tenant_id, entry_date)`
  - `idx_dte_invoices_tenant_folio` -> `(tenant_id, dte_type, folio)`
  - `idx_expenses_tenant_date` -> `(tenant_id, expense_date)`
- Esto garantiza que el planificador de PostgreSQL utilice B-Tree index scan directo delimitado al tenant, evitando el escaneo de páginas de disco de terceros.

---

## 8. Criterio de Evolución Futura (Fase 2+)

Si en etapas avanzadas de la empresa (Fase 2 o posterior) ingresa un cliente de clase Enterprise con requerimientos legales o de compliance que exijan almacenamiento físico independiente, la arquitectura actual permite migrar ese tenant puntual a una base de datos dedicada (*tenant extraction*) mediante un simple `COPY (SELECT * FROM ... WHERE tenant_id = ...)`, manteniendo la base principal bajo el modelo compartido estándar.
