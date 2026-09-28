from app.routers.accounting import router as accounting_router
from app.routers.documents import router as documents_router
from app.routers.expenses import router as expenses_router
from app.routers.invoicing import router as invoicing_router
from app.routers.system import router as system_router

from app.routers import (
    accounting,
    auth,
    documents,
    dte,
    expenses,
    inventory,
    invoicing,
    production,
    system,
)

__all__ = [
    "system_router",
    "accounting_router",
    "invoicing_router",
    "expenses_router",
    "documents_router",
    "accounting",
    "auth",
    "documents",
    "dte",
    "expenses",
    "inventory",
    "invoicing",
    "production",
    "system",
]
