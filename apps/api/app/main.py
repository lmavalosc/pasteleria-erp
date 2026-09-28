from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.errors import DomainError
from app.routers import accounting, documents, expenses, invoicing, system
from app.schemas.common import ErrorDetail, ProblemDetail

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Backend Fase 1: contabilidad, DTE, gastos y documentos.",
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError):
    problem = exc.to_problem_detail(instance=str(request.url.path))
    return JSONResponse(
        status_code=exc.status_code,
        content=problem.model_dump(mode="json"),
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    errors = []

    for err in exc.errors():
        loc = err.get("loc", [])
        field = ".".join(str(part) for part in loc if part not in {"body"})

        errors.append(
            ErrorDetail(
                field=field,
                message=str(err.get("msg", "Invalid value")),
                code="VALIDATION_ERROR",
            )
        )

    problem = ProblemDetail(
        type="https://errors.nucleo-contable-dte.local/validation-error",
        title="Solicitud inválida",
        status=422,
        detail="Uno o más campos fallaron la validación.",
        instance=str(request.url.path),
        errors=errors,
    )

    return JSONResponse(
        status_code=422,
        content=problem.model_dump(mode="json"),
    )


# --- Routers ERP Fase 1 bajo /api/v1 ---
app.include_router(system.router, prefix="/api/v1")
app.include_router(accounting.router, prefix="/api/v1")
app.include_router(invoicing.router, prefix="/api/v1")
app.include_router(expenses.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")

# --- Soporte directo sin prefijo para /health y /openapi.json ---
app.include_router(system.router)


@app.get("/openapi.json", include_in_schema=False)
def get_root_openapi():
    return app.openapi()


# --- Aliases /v1 para retrocompatibilidad ---
app.include_router(accounting.router, prefix="/v1")
app.include_router(invoicing.router, prefix="/v1")
app.include_router(expenses.router, prefix="/v1")
app.include_router(documents.router, prefix="/v1")


