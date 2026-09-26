from decimal import Decimal
from typing import Annotated, Any

from pydantic import BaseModel, Field, PlainSerializer

# Serializa Decimal como string de dos decimales (ej. "15000.00")
MoneyStr = Annotated[
    Decimal,
    PlainSerializer(lambda x: f"{x:.2f}", return_type=str, when_used="json"),
]


class ErrorDetail(BaseModel):
    field: str | None = Field(default=None, description="Campo causante del error")
    message: str = Field(..., description="Mensaje explicativo del error")
    code: str | None = Field(default=None, description="Código de error específico")


class ProblemDetail(BaseModel):
    type: str = Field(default="about:blank")
    title: str
    status: int
    detail: str
    instance: str | None = None
    code: str | None = None
    errors: list[ErrorDetail] = Field(default_factory=list)
    invalid_params: list[dict[str, Any]] | None = None
