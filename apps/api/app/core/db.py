import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

# En runtime de API conectar con app_user para que PostgreSQL fuerce RLS estrictamente
DATABASE_URL = os.getenv(
    "APP_DATABASE_URL",
    os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://app_user:app_password@localhost:5432/nucleo",
    ),
)

# Si la cadena apunta al usuario dueño/migrador nucleo, enrutar a app_user para aislamiento RLS
if "nucleo:nucleo" in DATABASE_URL:
    app_db = os.getenv("APP_DATABASE_URL")
    DATABASE_URL = app_db if app_db else DATABASE_URL.replace("nucleo:nucleo", "app_user:app_password")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    future=True,
)
