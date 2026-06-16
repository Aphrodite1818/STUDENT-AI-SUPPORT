"""Backward-compatible schema exports for the parents module."""

from app.modules.parents.schemas import ParentCreate, ParentListResponse, ParentResponse, ParentUpdate

__all__ = [
    "ParentCreate",
    "ParentListResponse",
    "ParentResponse",
    "ParentUpdate",
]
