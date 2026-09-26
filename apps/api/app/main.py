from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.errors import setup_exception_handlers
from app.routers import accounting, documents, expenses, invoicing, system

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend Fase 1: contabilidad, DTE, gastos y documentos.",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Manejo estándar de excepciones (RFC 7807)
setup_exception_handlers(app)

# Registro de routers por dominio
app.include_router(system.router, prefix=settings.API_V1_PREFIX)
app.include_router(system.router)  # Soporte directo para /health
app.include_router(accounting.router, prefix=settings.API_V1_PREFIX)
app.include_router(invoicing.router, prefix=settings.API_V1_PREFIX)
app.include_router(expenses.router, prefix=settings.API_V1_PREFIX)
app.include_router(documents.router, prefix=settings.API_V1_PREFIX)
