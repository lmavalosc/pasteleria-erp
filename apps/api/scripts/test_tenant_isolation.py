import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("[ERROR] DATABASE_URL no configurada en .env")
    sys.exit(1)


def test_tenant_isolation() -> bool:
    print("Iniciando prueba de aislamiento multi-tenant sin RLS (Paso 3.9)...")
    try:
        engine = create_engine(DATABASE_URL, connect_args={"connect_timeout": 3})
        with engine.begin() as conn:
            # 1. Crear segundo tenant si no existe
            conn.execute(
                text(
                    """
                    INSERT INTO tenants (id, name, tax_id, status)
                    VALUES (
                        '00000000-0000-0000-0000-000000000002',
                        'Demo Two SpA',
                        '77000000-8',
                        'active'
                    )
                    ON CONFLICT (id) DO NOTHING;
                    """
                )
            )

            # 2. Insertar misma cuenta contable '1110101' para segundo tenant
            conn.execute(
                text(
                    """
                    INSERT INTO accounting_accounts (tenant_id, code, name, account_type)
                    VALUES (
                        '00000000-0000-0000-0000-000000000002',
                        '1110101',
                        'Caja',
                        'asset'
                    )
                    ON CONFLICT (tenant_id, code) DO NOTHING;
                    """
                )
            )

            # 3. Verificar coexistencia de la cuenta para ambos tenants
            result = conn.execute(
                text(
                    """
                    SELECT tenant_id, code, name, account_type
                    FROM accounting_accounts
                    WHERE code = '1110101'
                    ORDER BY tenant_id;
                    """
                )
            ).fetchall()

            print("\nCuentas encontradas con código '1110101':")
            for row in result:
                print(f"  Tenant: {row[0]} | Código: {row[1]} | Nombre: {row[2]} | Tipo: {row[3]}")

            tenants_with_code = [str(row[0]) for row in result]
            if "00000000-0000-0000-0000-000000000001" not in tenants_with_code or \
               "00000000-0000-0000-0000-000000000002" not in tenants_with_code:
                print("\n[!] Error: No se encontraron cuentas en ambos tenants.")
                return False

            print("\n[OK] Mismo código contable coexiste en múltiples tenants gracias a UNIQUE(tenant_id, code).")

        # 4. Prueba de colisión: insertar duplicado en el MISMO tenant debe fallar
        print("\nProbando constraint negativo (duplicado en el mismo tenant)...")
        with engine.begin() as conn:
            try:
                conn.execute(
                    text(
                        """
                        INSERT INTO accounting_accounts (tenant_id, code, name, account_type)
                        VALUES (
                            '00000000-0000-0000-0000-000000000001',
                            '1110101',
                            'Caja Duplicada',
                            'asset'
                        );
                        """
                    )
                )
                print("[!] ERROR: La inserción duplicada en el mismo tenant debió fallar.")
                return False
            except IntegrityError as ie:
                print("[OK] Error esperado de violación de unicidad capturado exitosamente:")
                print(f"     {ie.orig}")

        print("\n[SUCCESS] Todas las pruebas de aislamiento a nivel relacional pasaron correctamente.")
        return True

    except Exception as e:
        print(f"\n[!] Error durante la ejecución de la prueba: {e}")
        return False


if __name__ == "__main__":
    success = test_tenant_isolation()
    sys.exit(0 if success else 1)
