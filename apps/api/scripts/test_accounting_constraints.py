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

APP_DATABASE_URL = os.getenv(
    "APP_DATABASE_URL",
    "postgresql+psycopg://app_user:app_password@localhost:5432/nucleo",
)
TENANT_ID = "00000000-0000-0000-0000-000000000001"


def test_accounting_constraints():
    print(f"Probando restricciones contables (partida doble e integridad) en: {APP_DATABASE_URL} ...")
    engine = create_engine(APP_DATABASE_URL, connect_args={"connect_timeout": 3})

    # 1. Obtener IDs de cuentas sembradas
    with engine.connect() as conn:
        with conn.begin():
            conn.execute(
                text(
                    "SELECT set_config('app.tenant_id', :t, true), "
                    "set_config('app.current_tenant_id', :t, true);"
                ),
                {"t": TENANT_ID},
            )
            caja_id = conn.execute(
                text("SELECT id FROM accounting_accounts WHERE tenant_id = :t AND code = '1110101'"),
                {"t": TENANT_ID},
            ).scalar()
            gastos_id = conn.execute(
                text("SELECT id FROM accounting_accounts WHERE tenant_id = :t AND code = '5110101'"),
                {"t": TENANT_ID},
            ).scalar()

        assert caja_id and gastos_id, "Las cuentas 1110101 y 5110101 deben existir en el seed."

    # --- CASO 1: Desbalance en cabecera (total_debit != total_credit) ---
    print("\n--- CASO 1: Desbalance en cabecera (total_debit != total_credit) ---")
    with engine.connect() as conn:
        try:
            with conn.begin():
                conn.execute(
                    text(
                        "SELECT set_config('app.tenant_id', :t, true), "
                        "set_config('app.current_tenant_id', :t, true);"
                    ),
                    {"t": TENANT_ID},
                )
                conn.execute(
                    text(
                        """
                        INSERT INTO journal_entries (tenant_id, entry_date, description, status, total_debit, total_credit)
                        VALUES (:t, CURRENT_DATE, 'Cabecera desbalanceada', 'draft', 1000.00, 900.00);
                        """
                    ),
                    {"t": TENANT_ID},
                )
            assert False, "Fallo: Debió ser rechazado por journal_entries_balance."
        except DBAPIError as e:
            assert "journal_entries_balance" in str(e).lower(), f"Error inesperado: {e}"
            print("  [OK] Constraint 'journal_entries_balance' validado exitosamente.")

    # --- CASO 2: Débito y Crédito simultáneos en una misma línea ---
    print("\n--- CASO 2: Débito y Crédito simultáneos en una misma línea ---")
    with engine.connect() as conn:
        try:
            with conn.begin():
                conn.execute(
                    text(
                        "SELECT set_config('app.tenant_id', :t, true), "
                        "set_config('app.current_tenant_id', :t, true);"
                    ),
                    {"t": TENANT_ID},
                )
                entry_id = conn.execute(
                    text(
                        """
                        INSERT INTO journal_entries (tenant_id, entry_date, description, status, total_debit, total_credit)
                        VALUES (:t, CURRENT_DATE, 'Asiento inválido simultáneo', 'draft', 1000.00, 1000.00)
                        RETURNING id;
                        """
                    ),
                    {"t": TENANT_ID},
                ).scalar()

                conn.execute(
                    text(
                        """
                        INSERT INTO journal_lines (tenant_id, entry_id, account_id, debit, credit)
                        VALUES (:t, :eid, :aid, 1000.00, 1000.00);
                        """
                    ),
                    {"t": TENANT_ID, "eid": entry_id, "aid": caja_id},
                )
            assert False, "Fallo: Debió ser rechazado por journal_lines_not_both_positive."
        except DBAPIError as e:
            assert "journal_lines_not_both_positive" in str(e).lower(), f"Error inesperado: {e}"
            print("  [OK] Constraint 'journal_lines_not_both_positive' validado exitosamente.")

    # --- CASO 3: Línea con débito y crédito en cero simultáneamente ---
    print("\n--- CASO 3: Línea con débito y crédito en cero ---")
    with engine.connect() as conn:
        try:
            with conn.begin():
                conn.execute(
                    text(
                        "SELECT set_config('app.tenant_id', :t, true), "
                        "set_config('app.current_tenant_id', :t, true);"
                    ),
                    {"t": TENANT_ID},
                )
                entry_id = conn.execute(
                    text(
                        """
                        INSERT INTO journal_entries (tenant_id, entry_date, description, status, total_debit, total_credit)
                        VALUES (:t, CURRENT_DATE, 'Línea cero prueba', 'draft', 0.00, 0.00)
                        RETURNING id;
                        """
                    ),
                    {"t": TENANT_ID},
                ).scalar()

                conn.execute(
                    text(
                        """
                        INSERT INTO journal_lines (tenant_id, entry_id, account_id, debit, credit)
                        VALUES (:t, :eid, :aid, 0.00, 0.00);
                        """
                    ),
                    {"t": TENANT_ID, "eid": entry_id, "aid": caja_id},
                )
            assert False, "Fallo: Debió ser rechazado por journal_lines_not_both_zero."
        except DBAPIError as e:
            assert "journal_lines_not_both_zero" in str(e).lower(), f"Error inesperado: {e}"
            print("  [OK] Constraint 'journal_lines_not_both_zero' validado exitosamente.")

    # --- CASO 4: Asiento balanceado válido ---
    print("\n--- CASO 4: Asiento balanceado de dos partidas (Partida Doble) ---")
    with engine.connect() as conn:
        with conn.begin():
            conn.execute(
                text(
                    "SELECT set_config('app.tenant_id', :t, true), "
                    "set_config('app.current_tenant_id', :t, true);"
                ),
                {"t": TENANT_ID},
            )
            # Limpiar si ya existía de ejecuciones previas
            conn.execute(
                text("DELETE FROM journal_entries WHERE tenant_id = :t AND description = 'Asiento válido prueba'"),
                {"t": TENANT_ID},
            )

            entry_id = conn.execute(
                text(
                    """
                    INSERT INTO journal_entries (tenant_id, entry_date, description, status, total_debit, total_credit)
                    VALUES (:t, CURRENT_DATE, 'Asiento válido prueba', 'draft', 1000.00, 1000.00)
                    RETURNING id;
                    """
                ),
                {"t": TENANT_ID},
            ).scalar()

            conn.execute(
                text(
                    """
                    INSERT INTO journal_lines (tenant_id, entry_id, account_id, debit, credit)
                    VALUES 
                        (:t, :eid, :caja, 1000.00, 0.00),
                        (:t, :eid, :gastos, 0.00, 1000.00);
                    """
                ),
                {"t": TENANT_ID, "eid": entry_id, "caja": caja_id, "gastos": gastos_id},
            )

        # Verificación de lectura
        with conn.begin():
            conn.execute(
                text(
                    "SELECT set_config('app.tenant_id', :t, true), "
                    "set_config('app.current_tenant_id', :t, true);"
                ),
                {"t": TENANT_ID},
            )
            rows = conn.execute(
                text(
                    """
                    SELECT je.description, je.total_debit, je.total_credit, aa.code, jl.debit, jl.credit
                    FROM journal_entries je
                    JOIN journal_lines jl ON jl.entry_id = je.id
                    JOIN accounting_accounts aa ON aa.id = jl.account_id
                    WHERE je.id = :eid
                    ORDER BY jl.debit DESC;
                    """
                ),
                {"eid": entry_id},
            ).fetchall()

        assert len(rows) == 2, f"Se esperaban 2 líneas, se obtuvieron {len(rows)}"
        assert float(rows[0][4]) == 1000.00 and float(rows[0][5]) == 0.00
        assert float(rows[1][4]) == 0.00 and float(rows[1][5]) == 1000.00
        print("  [OK] Asiento balanceado insertado y verificado correctamente:")
        for row in rows:
            print(f"       Cuenta {row[3]} -> Débito: {row[4]} | Crédito: {row[5]}")

    print("\n[SUCCESS] Todos los constraints contables de partida doble fueron validados exitosamente por PostgreSQL.")
    return True


if __name__ == "__main__":
    success = test_accounting_constraints()
    sys.exit(0 if success else 1)
