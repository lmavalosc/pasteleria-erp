import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# En runtime de API conectar con app_user para que PostgreSQL fuerce RLS estrictamente
database_url = os.getenv("APP_DATABASE_URL", settings.database_url)
if "nucleo:nucleo" in database_url:
    app_db = os.getenv("APP_DATABASE_URL")
    database_url = app_db if app_db else database_url.replace("nucleo:nucleo", "app_user:app_password")

engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    future=True,
)
