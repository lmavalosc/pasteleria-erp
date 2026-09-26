import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import DBAPIError

load_dotenv()

# URL de conexión con rol no dueño (app_user) para que PostgreSQL aplique RLS
APP_DATABASE_URL = os.getenv(
    "APP_DATABASE_URL",
    "postgresql+psycopg://app_user:app_password@localhost:5432/nucleo",
)
TENANT_1 = "00000000-0000-0000-0000-000000000001"
TENANT_2 = "00000000-0000-0000-0000-000000000002"


def test_rls_isolation():
    print(f"Probando Row Level Security (RLS) en: {APP_DATABASE_URL} ...")
    try:
        engine = create_engine(APP_DATABASE_URL, connect_args={"connect_timeout": 3})

        # 1. Sin contexto de tenant -> debe devolver 0 filas (aislamiento por defecto)
        print("\n--- Prueba 1: Consulta sin contexto de tenant ---")
        with engine.connect() as conn:
            count = conn.execute(text("SELECT COUNT(*) FROM accounting_accounts;")).scalar()
            print(f"  Resultado COUNT(*): {count}")
            assert count == 0, f"Fallo RLS: Se esperaban 0 filas sin tenant, pero se obtuvieron {count}"
            print("  [OK] Sin tenant_id fijado, el motor devuelve 0 filas por defecto.")

        # 2. Con Tenant 1 -> solo debe ver cuentas pertenecientes al Tenant 1 (6 cuentas del seed)
        print("\n--- Prueba 2: Consulta con contexto de Tenant 1 ---")
        with engine.connect() as conn:
            conn.execute(
                text(
                    "SELECT set_config('app.tenant_id', :t, false), "
                    "set_config('app.current_tenant_id', :t, false);"
                ),
                {"t": TENANT_1},
            )
            count_t1 = conn.execute(
                text("SELECT COUNT(*) FROM accounting_accounts;")
            ).scalar()
            print(f"  Resultado COUNT(*) para Tenant 1: {count_t1}")
            assert count_t1 == 6, f"Fallo RLS: Se esperaban 6 cuentas para Tenant 1, se obtuvieron {count_t1}"
            print("  [OK] Con app.tenant_id fijado, solo se leen las cuentas de ese tenant.")

        # 3. Inserción cruzada (Cross-tenant breach) -> Postgres debe rechazarla por política RLS WITH CHECK
        print("\n--- Prueba 3: Intento de inserción cruzada (Cross-tenant write) ---")
        violation_caught = False
        with engine.connect() as conn:
            try:
                with conn.begin():
                    conn.execute(
                        text(
                            "SELECT set_config('app.tenant_id', :t, true), "
                            "set_config('app.current_tenant_id', :t, true);"
                        ),
                        {"t": TENANT_1},
                    )
                    conn.execute(
                        text(
                            """
                            INSERT INTO expenses (
                                tenant_id, expense_date, amount, currency, status, description
                            )
                            VALUES (
                                :t2, CURRENT_DATE, 5000.00, 'CLP', 'draft', 'Intrusión no autorizada'
                            );
                            """
                        ),
                        {"t2": TENANT_2},
                    )
            except DBAPIError as e:
                error_msg = str(e).lower()
                # Acepta tanto mensajes en inglés como en español de PostgreSQL
                if (
                    "row-level security" in error_msg
                    or "seguridad de registros" in error_msg
                    or "insufficientprivilege" in error_msg
                ):
                    violation_caught = True
                    print("  [OK] Rechazo exitoso por el motor de base de datos:")
                    print(f"       {e.orig}")
                else:
                    raise

        assert violation_caught, "Fallo RLS: La política WITH CHECK debió rechazar el INSERT cruzado."

        print("\n[SUCCESS] Validación de RLS completada: el aislamiento de lectura y escritura es forzado por PostgreSQL.")
        return True

    except Exception as e:
        print(f"\n[!] Error durante la verificación de RLS: {e}")
        return False


if __name__ == "__main__":
    success = test_rls_isolation()
    sys.exit(0 if success else 1)
