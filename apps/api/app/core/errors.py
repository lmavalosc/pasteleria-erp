import uuid
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.schemas.common import ErrorDetail, ProblemDetail


class DomainError(Exception):
    def __init__(
        self,
        status_code: int = 400,
        title: str = "Error de dominio",
        detail: str = "",
        code: str | None = None,
        errors: list[ErrorDetail] | None = None,
    ):
        self.status_code = status_code
        self.title = title
        self.detail = detail
        self.code = code
        self.errors = errors or []
        super().__init__(detail)

    def to_problem_detail(self, instance: str | None = None) -> ProblemDetail:
        return ProblemDetail(
            type=f"https://errors.nucleo-contable-dte.local/{self.code or 'domain-error'}",
            title=self.title,
            status=self.status_code,
            detail=self.detail,
            instance=instance,
            code=self.code,
            errors=self.errors,
        )


class DomainException(DomainError):
    """Clase compatible con las implementaciones iniciales de servicios."""
    def __init__(
        self,
        title: str,
        detail: str,
        status_code: int = 400,
        invalid_params: list[dict[str, Any]] | None = None,
        code: str | None = None,
    ):
        errors_list: list[ErrorDetail] = []
        if invalid_params:
            for p in invalid_params:
                errors_list.append(ErrorDetail(field=p.get("name"), message=p.get("reason", "")))
        super().__init__(
            status_code=status_code,
            title=title,
            detail=detail,
            code=code,
            errors=errors_list,
        )
        self.invalid_params = invalid_params


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError):
        problem = exc.to_problem_detail(instance=str(request.url.path))
        if hasattr(exc, "invalid_params") and exc.invalid_params:
            problem.invalid_params = exc.invalid_params
        return JSONResponse(
            status_code=exc.status_code,
            content=problem.model_dump(exclude_none=True),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        error_details = [
            ErrorDetail(
                field=" -> ".join(str(loc) for loc in err["loc"] if loc != "body"),
                message=err["msg"],
                code=err.get("type"),
            )
            for err in exc.errors()
        ]
        invalid_params = [
            {"name": " -> ".join(str(loc) for loc in err["loc"]), "reason": err["msg"]}
            for err in exc.errors()
        ]
        problem = ProblemDetail(
            type="https://errors.nucleo-contable-dte.local/validation-error",
            title="Error de validación en la solicitud",
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Uno o más campos enviados no cumplen con el formato requerido.",
            instance=str(request.url.path),
            code="VALIDATION_ERROR",
            errors=error_details,
            invalid_params=invalid_params,
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=problem.model_dump(exclude_none=True),
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        error_id = str(uuid.uuid4())
        problem = ProblemDetail(
            type="https://errors.nucleo-contable-dte.local/internal-server-error",
            title="Error interno del servidor",
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ha ocurrido un error inesperado. Código de seguimiento: {error_id}",
            instance=str(request.url.path),
            code="INTERNAL_SERVER_ERROR",
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=problem.model_dump(exclude_none=True),
        )


# Alias de retrocompatibilidad
setup_exception_handlers = register_exception_handlers
