# Definition of Done Fase 1

La Fase 1 termina cuando:

1. Un tenant puede ser creado y aislado lógicamente.
2. Existe plan de cuentas básico.
3. Se pueden registrar asientos de partida doble balanceados.
4. Se pueden emitir/registrar DTE según contrato.
5. Se pueden registrar gastos con documento adjunto.
6. Web y móvil consumen el mismo api-client generado desde OpenAPI.
7. No hay tipos duplicados manualmente entre apps.
8. No hay secretos SII, certificados ni CAF en el repositorio.
9. Existe pipeline CI para lint/typecheck/build/test.
10. Existe entorno de staging desplegable.

Esto evita que el proyecto se expanda sin control.
