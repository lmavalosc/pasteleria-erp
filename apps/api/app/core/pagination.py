from typing import Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class PageParams(BaseModel):
    page: int = Field(default=1, ge=1, description="Número de página (1-based)")
    page_size: int = Field(default=20, ge=1, le=100, description="Registros por página")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    pages: int | None = None

    def model_post_init(self, __context) -> None:
        if self.pages is None:
            self.pages = self.total_pages
