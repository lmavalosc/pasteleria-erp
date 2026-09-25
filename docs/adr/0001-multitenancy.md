# ADR 0001: Estrategia multi-tenant

## Estado

Aceptado.

## Contexto

Necesitamos soportar múltiples empresas/tenants en la misma plataforma.

## Decisión

Usaremos un esquema PostgreSQL compartido con columna `tenant_id` en todas las tablas de negocio.

## Motivos

- Menor complejidad operativa para MVP.
- Migraciones simples.
- Desarrollo local más fácil.
- Consultas cross-tenant para soporte más simples.
- Permite evolucionar hacia Row Level Security.

## Consecuencias

- Toda consulta debe filtrar por `tenant_id`.
- El `tenant_id` no debe venir ciegamente del cliente sin validación.
- Se recomienda usar RLS en PostgreSQL como defensa adicional.
- No se usará schema-per-tenant en Fase 1 salvo cambio mayor de requisitos.
