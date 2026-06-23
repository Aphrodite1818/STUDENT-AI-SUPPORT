from typing import Annotated, TypeAlias
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies.db import DbSession
from app.core.dependencies.route_guards import get_current_teacher
from app.modules.subjects.schemas import SubjectListResponse, SubjectResponse
from app.modules.teachers.models import Teacher
from app.modules.teachers.schemas import (
    TeacherOnboardingStatusResponse,
    TeacherOnboardingUpdate,
    TeacherResponse,
)
from app.modules.teachers.service import TeacherService


router = APIRouter(tags=["Teachers"])

CurrentTeacher: TypeAlias = Annotated[Teacher, Depends(get_current_teacher)]





@router.get(
    "/me",
    response_model=TeacherResponse,
    summary="Get my teacher profile",
)
async def get_my_teacher_profile(
    db: DbSession,
    current_user: CurrentTeacher,
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
    payload: TeacherOnboardingUpdate,
    db: DbSession,
    current_user: CurrentTeacher,
) -> Teacher:
    """Allow a teacher to update their own profile."""

    return await TeacherService.update_my_teacher_profile(
        db=db,
        actor=current_user,
        teacher_data=payload,
    )


@router.get(
    "/me/onboarding-status",
    response_model=TeacherOnboardingStatusResponse,
    summary="Get my teacher onboarding status",
)
async def get_my_teacher_onboarding_status(
    db: DbSession,
    current_user: CurrentTeacher,
) -> TeacherOnboardingStatusResponse:
    """Return the current teacher onboarding status."""

    return await TeacherService.get_my_onboarding_status(
        db=db,
        actor=current_user,
    )


@router.get(
    "/me/subjects",
    response_model=SubjectListResponse,
    summary="List my assigned subjects",
)
async def get_my_subjects(
    db: DbSession,
    current_user: CurrentTeacher,
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



