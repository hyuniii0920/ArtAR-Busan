from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginationMeta(BaseModel):
    total: int
    page: int
    per_page: int


class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T
    meta: PaginationMeta | None = None


class ApiError(BaseModel):
    success: bool = False
    error: dict[str, str]


class I18nField(BaseModel):
    ko: str = ""
    en: str = ""
    jp: str = ""
    cn: str = ""

    def to_dict(self) -> dict[str, str]:
        return self.model_dump(exclude_none=False)
