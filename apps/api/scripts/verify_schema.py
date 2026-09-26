import os
import sys

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("[ERROR] DATABASE_URL no está configurada en .env")
    sys.exit(1)

EXPECTED_TABLES = [
    "accounting_accounts",
    "alembic_version",
    "documents",
    "dte_invoice_items",
    "dte_invoices",
    "expenses",
    "journal_entries",
    "journal_lines",
    "memberships",
    "tenants",
    "users",
]

RLS_TABLES = [
    "accounting_accounts",
    "documents",
    "dte_invoice_items",
    "dte_invoices",
    "expenses",
    "journal_entries",
    "journal_lines",
]


def verify_database() -> bool:
    print(f"Connecting to database: {DATABASE_URL} ...")
    try:
        engine = create_engine(DATABASE_URL, connect_args={"connect_timeout": 3})
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        print("\n[!] No se pudo conectar a la base de datos en localhost:5432.")
        print(f"Detalle: {e}")
        print("\nPara iniciar PostgreSQL:")
        print("1. Iniciar Docker Desktop y ejecutar: docker compose -f infra/docker-compose.yml up -d")
        print("2. O utilizar un servicio PostgreSQL local / cloud configurando DATABASE_URL en apps/api/.env")
        return False

    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    print("\n--- 1. Verificación de Tablas ---")
    missing_tables = [t for t in EXPECTED_TABLES if t not in existing_tables]
    for table in EXPECTED_TABLES:
        status = "[OK]" if table in existing_tables else "[MISSING]"
        print(f"  {status} {table}")

    if missing_tables:
        print("\n[!] Faltan tablas en el esquema. Ejecuta: alembic upgrade head")
        return False

    print("\n--- 2. Verificación de Row Level Security (RLS) ---")
    with engine.connect() as conn:
        result = conn.execute(
            text(
                """
                SELECT relname, relrowsecurity, relforcerowsecurity 
                FROM pg_class 
                WHERE relnamespace = 'public'::regnamespace 
                  AND relname = ANY(:tables);
                """
            ),
            {"tables": RLS_TABLES},
        ).fetchall()

        rls_status = {row[0]: (row[1], row[2]) for row in result}
        all_rls_ok = True
        for table in sorted(RLS_TABLES):
            is_rls, is_forced = rls_status.get(table, (False, False))
            status = "[OK RLS]" if is_rls else "[NO RLS]"
            print(f"  {status} {table} (relrowsecurity={is_rls})")
            if not is_rls:
                all_rls_ok = False

    if not all_rls_ok:
        print("\n[!] Algunas tablas no tienen RLS activo.")
        return False

    print("\n[SUCCESS] Todas las tablas y políticas de RLS de Fase 1 están correctamente inicializadas.")
    return True


if __name__ == "__main__":
    success = verify_database()
    sys.exit(0 if success else 1)
