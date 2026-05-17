# schemas/common.py

from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field
from pydantic.generics import GenericModel


T = TypeVar("T")


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class PaginationParams(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)


class PaginatedResponse(GenericModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    pages: int


class SuccessResponse(BaseSchema):
    message: str
    data: Optional[Any] = None


class ErrorResponse(BaseSchema):
    detail: str
    code: str
    field: Optional[str] = None