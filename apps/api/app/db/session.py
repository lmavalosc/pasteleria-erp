import os
import uuid
from typing import Generator
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Header, HTTPException

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL no configurada en .env")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db(
    x_tenant_id: str = Header(..., description="ID del Tenant para aislar la sesión")
) -> Generator[Session, None, None]:
    """
    Inyecta tenant_id en la transacción usando set_config(..., true) (equivalente a SET LOCAL).
    Garantiza aislamiento estricto mediante RLS durante el ciclo de vida de la transacción.
    """
    try:
        tenant_uuid = uuid.UUID(x_tenant_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="X-Tenant-ID header no es un UUID válido")

    session = SessionLocal()
    try:
        # set_config con is_local=true restringe la variable al contexto de la transacción actual
        session.execute(
            text(
                "SELECT set_config('app.tenant_id', :tenant_id, true), "
                "set_config('app.current_tenant_id', :tenant_id, true);"
            ),
            {"tenant_id": str(tenant_uuid)},
        )
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
