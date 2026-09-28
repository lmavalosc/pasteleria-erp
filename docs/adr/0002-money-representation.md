# ADR 0002: Representación y Conversión de Dinero (CLP y DecimalString)

## Estado
Aceptado.

## Contexto
En el ecosistema financiero y fiscal chileno:
1. El **Servicio de Impuestos Internos (SII)** exige montos en pesos enteros (CLP sin decimales) para la mayoría de los Documentos Tributarios Electrónicos (DTE como Facturas Electrónicas Tipo 33, Boletas Tipo 39, etc.). Por esta razón, las tablas de base de datos de facturación (`dte_invoices`, `dte_invoice_items`) utilizan `BigInteger` para garantizar precisión entera estricta sin discrepancias de redondeo fiscal.
2. La **Contabilidad Financiera y Libro Diario** (`journal_lines`, `expenses`) requiere precisión contable estándar de dos decimales (IFRS / PCGA) modelada con `Numeric(18,2)`.
3. El **Contrato OpenAPI Fase 1** (`openapi/fase1.yaml`) define `DecimalString` (`"1000.00"`) para transferencias HTTP, protegiendo a los clientes JavaScript / TypeScript de pérdidas de precisión con números de punto flotante de 64 bits (`IEEE 754`).

## Decisión
1. **Persistencia Híbrida Justificada**:
   - Módulo DTE/SII: Almacenamiento en `BigInteger` (pesos enteros CLP) según la normativa técnica del SII.
   - Módulo Contable y Gastos: Almacenamiento en `Numeric(18,2)` para cálculo de saldos y partidas dobles.
2. **Capa de Transporte (API REST)**:
   - Todo endpoint cuyo esquema OpenAPI declare `DecimalString` o `NonNegativeDecimalString` debe serializar strings con dos decimales fijos (ej. `"1000.00"`).
   - Nunca deben exponerse enteros crudos (`1000`) en campos definidos como `DecimalString`.
3. **Helpers de Conversión Estandarizados**:
   - `pesos enteros -> DecimalString`: `f"{Decimal(amount):.2f}"` (ej. `1500 -> "1500.00"`).
   - `DecimalString -> enteros SII`: `int(Decimal(amount_str).quantize(Decimal('1'), rounding=ROUND_HALF_UP))` (ej. `"1500.00" -> 1500`).

## Consecuencias
- Los clientes frontend (Web Next.js y Móvil Expo) reciben siempre cadenas decimales consistentes.
- La generación de XML para el SII opera sobre enteros directos sin conversión flotante.
- Las restricciones de integridad en base de datos (`journal_entries_balance`, `journal_lines_not_both_positive`) se preservan sin modificaciones estructurales de alto riesgo.
