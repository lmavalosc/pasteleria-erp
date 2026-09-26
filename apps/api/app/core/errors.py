import uuid
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


class ProblemDetail(BaseModel):
    type: str = Field(default="about:blank")
    title: str
    status: int
    detail: str
    instance: str | None = None
    invalid_params: list[dict[str, Any]] | None = None
    errors: list[dict[str, Any]] | None = None


class DomainException(Exception):
    def __init__(
        self,
        title: str,
        detail: str,
        status_code: int = 400,
        invalid_params: list[dict[str, Any]] | None = None,
    ):
        self.title = title
        self.detail = detail
        self.status_code = status_code
        self.invalid_params = invalid_params
        super().__init__(detail)


def setup_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainException)
    async def domain_exception_handler(request: Request, exc: DomainException):
        problem = ProblemDetail(
            type=f"https://nucleo.local/errors/{exc.title.lower().replace(' ', '-')}",
            title=exc.title,
            status=exc.status_code,
            detail=exc.detail,
            instance=str(request.url),
            invalid_params=exc.invalid_params,
        )
        return JSONResponse(status_code=exc.status_code, content=problem.model_dump(exclude_none=True))

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        invalid_params = [
            {"name": " -> ".join(str(loc) for loc in err["loc"]), "reason": err["msg"]}
            for err in exc.errors()
        ]
        errors = [
            {"field": " -> ".join(str(loc) for loc in err["loc"]), "message": err["msg"]}
            for err in exc.errors()
        ]
        problem = ProblemDetail(
            type="https://nucleo.local/errors/validation-error",
            title="Error de validación en la solicitud",
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Uno o más campos enviados son inválidos o faltan en el cuerpo/parámetros.",
            instance=str(request.url),
            invalid_params=invalid_params,
            errors=errors,
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=problem.model_dump(exclude_none=True),
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        error_id = str(uuid.uuid4())
        problem = ProblemDetail(
            type="https://nucleo.local/errors/internal-server-error",
            title="Error interno del servidor",
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ha ocurrido un error inesperado. Código de seguimiento: {error_id}",
            instance=str(request.url),
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=problem.model_dump(exclude_none=True),
        )
