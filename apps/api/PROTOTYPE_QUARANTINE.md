# ⚠️ CUARENTENA / PROTOTIPO — NOTA DE ARQUITECTURA

> **IMPORTANTE — ETAPA 3 EN ADELANTE:**
> 
> Los esquemas Pydantic existentes en `apps/api/schemas/` y `apps/api/app/schemas/core_models.py` (que utilizan tipos `float` para montos de dinero y enumeraciones en español como `ACTIVO`/`PASIVO`) corresponden al **prototipo inicial rápido** y **NO son la fuente de verdad** para el modelo de datos relacional de la Etapa 3 (PostgreSQL).
>
> ### Reglas para la Etapa 3 (PostgreSQL DDL) y Etapa 4 (FastAPI):
> 1. **Única Fuente de Verdad:** El contrato oficial es `openapi/fase1.yaml`.
> 2. **Tipos Monetarios:** Nunca usar `FLOAT` ni `DOUBLE PRECISION` en PostgreSQL ni en Python. Se debe usar `NUMERIC(14, 2)` en base de datos y `Decimal` de Python (`NonNegativeDecimalString` en el contrato).
> 3. **Plan de Cuentas:** Usar los enums canónicos del contrato (`asset`, `liability`, `equity`, `revenue`, `expense`), no los nombres en español del prototipo.
> 4. **No Derivación Inversa:** Las migraciones Alembic / DDL de PostgreSQL deben generarse directamente desde el contrato `openapi/fase1.yaml` y el ADR 0001, no desde las clases Pydantic del prototipo.
