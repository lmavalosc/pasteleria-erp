from decimal import Decimal
from typing import Annotated, Any, Generic, TypeVar

from pydantic import BaseModel, Field, PlainSerializer

T = TypeVar("T")

# Serializa Decimal como string de dos decimales (ej. "15000.00")
MoneyStr = Annotated[
    Decimal,
    PlainSerializer(lambda x: f"{x:.2f}", return_type=str, when_used="json"),
]


class ErrorDetail(BaseModel):
    field: str | None = None
    message: str
    code: str | None = None


class ProblemDetail(BaseModel):
    type: str = "about:blank"
    title: str
    status: int
    detail: str | None = None
    instance: str | None = None
    code: str | None = None
    errors: list[ErrorDetail] = Field(default_factory=list)
    invalid_params: list[dict[str, Any]] | None = None


class PageMeta(BaseModel):
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    total: int = Field(ge=0)
    total_pages: int = Field(ge=0)


class Page(BaseModel, Generic[T]):
    items: list[T]
    page: int
    page_size: int
    total: int
    total_pages: int
    pages: int | None = None

    def model_post_init(self, __context: Any, /) -> None:
        if self.pages is None:
            self.pages = self.total_pages
