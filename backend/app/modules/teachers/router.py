#======================================#
#              router.py               #
#======================================#

from typing import Annotated, TypeAlias
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies.db import DbSession
from app.core.dependencies.route_guards import get_current_tenant_user
from app.modules.subjects.schemas import SubjectListResponse, SubjectResponse
from app.modules.teachers.models import Teacher
from app.modules.teachers.schemas import (
    TeacherSelfUpdate,
    TeacherListResponse,
    TeacherResponse,
    TeacherUpdate,
)
from app.modules.teachers.service import TeacherService
from app.modules.users.models import User


router = APIRouter(
    tags=["Teachers"],
)

CurrentTenantUser: TypeAlias = Annotated[User, Depends(get_current_tenant_user)]


@router.get(
    "",
    response_model=TeacherListResponse,
    summary="List teachers",
)
async def list_teachers(
    db: DbSession,
    current_user: CurrentTenantUser,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    search: str | None = Query(default=None, min_length=1, max_length=200),
) -> TeacherListResponse:
    """List teachers."""
    teachers, total = await TeacherService.list_teachers(
        db=db,
        actor=current_user,
        skip=skip,
        limit=limit,
        search=search,
    )

    return TeacherListResponse(
        items=[TeacherResponse.model_validate(teacher) for teacher in teachers],
        total=total,
    )


@router.get(
    "/me",
    response_model=TeacherResponse,
    summary="Get my teacher profile",
)
async def get_my_teacher_profile(
    db: DbSession,
    current_user: CurrentTenantUser,
) -> Teacher:
    """Return the current teacher profile."""
    return await TeacherService.get_my_teacher_profile(
        db=db,
        actor=current_user,
    )


@router.patch(
    "/me/profile",
    response_model=TeacherResponse,
    summary="Update my teacher profile",
)
async def update_my_teacher_profile(
    payload: TeacherSelfUpdate,
    db: DbSession,
    current_user: CurrentTenantUser,
) -> Teacher:
    """Allow a teacher to update their own profile."""
    return await TeacherService.update_my_teacher_profile(
        db=db,
        actor=current_user,
        teacher_data=payload,
    )


@router.get(
    "/me/subjects",
    response_model=SubjectListResponse,
    summary="List my assigned subjects",
)
async def get_my_subjects(
    db: DbSession,
    current_user: CurrentTenantUser,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    is_active: bool | None = Query(default=None),
    search: str | None = Query(default=None, min_length=1, max_length=100),
) -> SubjectListResponse:
    """Return subjects assigned to the current teacher."""
    subjects, total = await TeacherService.get_my_subjects(
        db=db,
        actor=current_user,
        skip=skip,
        limit=limit,
        is_active=is_active,
        search=search,
    )
    return SubjectListResponse(
        items=[SubjectResponse.model_validate(subject) for subject in subjects],
        total=total,
    )


@router.get(
    "/{teacher_id}",
    response_model=TeacherResponse,
    summary="Get a teacher",
)
async def get_teacher_by_id(
    teacher_id: UUID,
    db: DbSession,
    current_user: CurrentTenantUser,
) -> Teacher:
    """Return teacher by id."""
    return await TeacherService.get_teacher(
        db=db,
        actor=current_user,
        teacher_id=teacher_id,
    )


@router.patch(
    "/{teacher_id}",
    response_model=TeacherResponse,
    summary="Update a teacher",
)
async def update_teacher(
    teacher_id: UUID,
    payload: TeacherUpdate,
    current_user: CurrentTenantUser,
    db: DbSession,
) -> Teacher:
    """Update teacher."""
    return await TeacherService.update_teacher(
        db=db,
        actor=current_user,
        teacher_id=teacher_id,
        teacher_data=payload,
    )


@router.delete(
    "/{teacher_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Archive a teacher",
)
async def delete_teacher(
    db: DbSession,
    teacher_id: UUID,
    current_user: CurrentTenantUser,
) -> None:
    """Delete teacher."""
    await TeacherService.delete_teacher(
        db=db,
        actor=current_user,
        teacher_id=teacher_id,
    )
