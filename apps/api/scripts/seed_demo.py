import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("[ERROR] DATABASE_URL no configurada en .env")
    sys.exit(1)

SEED_FILE = os.path.join(os.path.dirname(__file__), "..", "seed", "fase1_demo.sql")


def apply_seed() -> bool:
    if not os.path.exists(SEED_FILE):
        print(f"[ERROR] No se encontró el archivo de seed: {SEED_FILE}")
        return False

    with open(SEED_FILE, "r", encoding="utf-8") as f:
        sql = f.read()

    print(f"Aplicando seed desde {os.path.abspath(SEED_FILE)}...")
    try:
        engine = create_engine(DATABASE_URL, connect_args={"connect_timeout": 3})
        with engine.begin() as conn:
            conn.execute(text(sql))
        print("[SUCCESS] Seed de demostración aplicado con éxito.")
        return True
    except Exception as e:
        print(f"[!] Error al aplicar seed: {e}")
        return False


if __name__ == "__main__":
    success = apply_seed()
    sys.exit(0 if success else 1)
