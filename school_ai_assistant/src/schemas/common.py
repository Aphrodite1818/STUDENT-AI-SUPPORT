#==========================#
# COMMON SCRIPT
#==========================#

from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field


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


class PaginatedResponse(BaseSchema, Generic[T]):
    items: List[T]
    total: int = Field(..., ge=0)
    page: int = Field(..., ge=1)
    pages: int = Field(..., ge=0)


class SuccessResponse(BaseSchema):
    message: str
    data: Optional[Any] = None


class ErrorResponse(BaseSchema):
    detail: str
    code: str
    field: Optional[str] = None
