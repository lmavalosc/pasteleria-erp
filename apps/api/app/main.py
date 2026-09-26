from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import system

app = FastAPI(
    title="Núcleo Contable y DTE API",
    version="1.0.0-fase1",
    description="Backend Fase 1: contabilidad, DTE, gastos y documentos.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(system.router, prefix="/api/v1")
app.include_router(system.router)  # Soporte directo para /health
