from datetime import datetime
from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from app.routers import accounting, invoicing, expenses, documents, inventory, production, auth, dte

app = FastAPI(
    title="API Pastelería Gourmet & Repostería de Autor - Fase 1 Core",
    description="Servidor FastAPI modular para Finanzas, Tributario, Egresos con insumos, Bóveda y Flujo de Producción y Costeo.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/v1/openapi.json",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Sistema: Health check funcional
@app.get("/health", tags=["Sistema"])
@app.get("/v1/health", tags=["Sistema"])
@app.get("/api/v1/health", tags=["Sistema"])
def health_check(x_tenant_id: str = Header(default="default-atelier")):
    return {
        "status": "ok",
        "service": "pasteleria-api-fase1",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "tenant_id": x_tenant_id,
    }

@app.get("/", tags=["Sistema"])
def root():
    return {
        "name": "Maison du Délice API",
        "version": "1.0.0",
        "docs": "/docs",
        "openapi": "/v1/openapi.json"
    }

# 2. Autenticación y Tenants
app.include_router(auth.router)

# 3. Finanzas: Cuentas y Asientos
app.include_router(accounting.router, prefix="/v1")
app.include_router(accounting.router)

# 4. Tributario: DTE
app.include_router(invoicing.router, prefix="/v1")
app.include_router(invoicing.router)
app.include_router(dte.router)

# 5. Egresos: Gastos con insumos
app.include_router(expenses.router, prefix="/v1")
app.include_router(expenses.router)

# 6. Bóveda: Documentos
app.include_router(documents.router, prefix="/v1")
app.include_router(documents.router)

# 7. Flujo de Producción y Costeo (NUEVO)
app.include_router(inventory.router, prefix="/v1")
app.include_router(inventory.router)

app.include_router(production.router, prefix="/v1")
app.include_router(production.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=4000, reload=True)
