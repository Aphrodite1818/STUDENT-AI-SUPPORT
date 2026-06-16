from typing import Annotated, TypeAlias
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies.db import DbSession
from app.core.dependencies.route_guards import get_current_tenant_user, require_tenant_role
from app.modules.students.models import AcademicStatus
from app.modules.students.schemas import (
    StudentCreate,
    StudentLinkCodeCreate,
    StudentLinkCodeRedeem,
    StudentLinkCodeResponse,
    StudentListResponse,
    StudentParentLinkCreate,
    StudentParentLinkListResponse,
    StudentParentLinkResponse,
    StudentParentLinkUpdate,
    StudentProfileComplete,
    StudentResponse,
    StudentSelfUpdate,
    StudentUpdate,
)
from app.modules.students.service import (
    StudentLinkCodeService,
    StudentParentLinkService,
    StudentService,
)
from app.modules.users.models import User, UserRole


router = APIRouter(tags=["Students"])

CurrentTenantUser: TypeAlias = Annotated[User, Depends(get_current_tenant_user)]
TenantAdminUser: TypeAlias = Annotated[
    User,
    Depends(require_tenant_role([UserRole.ADMIN])),
]


@router.post(
    "",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a student profile",
)
async def create_student_profile(
    payload: StudentCreate,
    db: DbSession,
    current_user: TenantAdminUser,
) -> StudentResponse:
    """Create a student profile."""
    return await StudentService.create_student_profile(
        db=db,
        actor=current_user,
        payload=payload,
    )


@router.get(
    "",
    response_model=StudentListResponse,
    summary="List students",
)
async def list_students(
    db: DbSession,
    current_user: CurrentTenantUser,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    search: str | None = Query(default=None, min_length=1, max_length=200),
    class_id: UUID | None = Query(default=None),
    status_filter: AcademicStatus | None = Query(default=None, alias="status"),
) -> StudentListResponse:
    """List student profiles."""
    students, total = await StudentService.list_students(
        db=db,
        actor=current_user,
        skip=skip,
        limit=limit,
        search=search,
        class_id=class_id,
        status=status_filter,
    )
    return StudentListResponse(items=students, total=total)


@router.get(
    "/me",
    response_model=StudentResponse,
    summary="Get my student profile",
)
async def get_my_student_profile(
    db: DbSession,
    current_user: CurrentTenantUser,
) -> StudentResponse:
    """Get the logged-in student's profile."""
    return await StudentService.get_student_by_user_id(
        db=db,
        actor=current_user,
        user_id=current_user.id,
    )


@router.patch(
    "/me/profile",
    response_model=StudentResponse,
    summary="Update my student profile",
)
async def update_my_student_profile(
    payload: StudentSelfUpdate,
    db: DbSession,
    current_user: CurrentTenantUser,
) -> StudentResponse:
    """Allow the logged-in student to update self-service profile fields."""
    return await StudentService.update_my_student_profile(
        db=db,
        actor=current_user,
        payload=payload,
    )


@router.get(
    "/me/parent-links",
    response_model=StudentParentLinkListResponse,
    summary="Get my parent links",
)
async def get_my_parent_links(
    db: DbSession,
    current_user: CurrentTenantUser,
) -> StudentParentLinkListResponse:
    """Get parent links for the logged-in student."""
    links, total = await StudentParentLinkService.list_my_parent_links(
        db=db,
        actor=current_user,
    )
    return StudentParentLinkListResponse(items=links, total=total)


@router.get(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Get a student profile",
)
async def get_student_profile(
    student_id: UUID,
    db: DbSession,
    current_user: CurrentTenantUser,
) -> StudentResponse:
    """Get a student profile by id."""
    return await StudentService.get_student_profile(
        db=db,
        actor=current_user,
        student_id=student_id,
    )


@router.patch(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Update a student profile",
)
async def update_student_profile(
    student_id: UUID,
    payload: StudentUpdate,
    db: DbSession,
    current_user: TenantAdminUser,
) -> StudentResponse:
    """Update a student profile."""
    return await StudentService.update_student_profile(
        db=db,
        actor=current_user,
        student_id=student_id,
        payload=payload,
    )


@router.patch(
    "/{student_id}/complete-profile",
    response_model=StudentResponse,
    summary="Complete a student profile",
)
async def complete_student_profile(
    student_id: UUID,
    payload: StudentProfileComplete,
    db: DbSession,
    current_user: TenantAdminUser,
) -> StudentResponse:
    """Complete an incomplete student profile."""
    return await StudentService.complete_student_profile(
        db=db,
        actor=current_user,
        student_id=student_id,
        payload=payload,
    )


@router.delete(
    "/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a student profile",
)
async def delete_student_profile(
    student_id: UUID,
    db: DbSession,
    current_user: TenantAdminUser,
) -> None:
    """Delete a student profile."""
    await StudentService.delete_student_profile(
        db=db,
        actor=current_user,
        student_id=student_id,
    )


@router.post(
    "/parent-links",
    response_model=StudentParentLinkResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a student-parent link",
)
async def create_student_parent_link(
    payload: StudentParentLinkCreate,
    db: DbSession,
    current_user: TenantAdminUser,
) -> StudentParentLinkResponse:
    """Create a student-parent link."""
    return await StudentParentLinkService.create_student_parent_link(
        db=db,
        actor=current_user,
        payload=payload,
    )


@router.patch(
    "/parent-links/{link_id}",
    response_model=StudentParentLinkResponse,
    summary="Update a student-parent link",
)
async def update_student_parent_link(
    link_id: UUID,
    payload: StudentParentLinkUpdate,
    db: DbSession,
    current_user: TenantAdminUser,
) -> StudentParentLinkResponse:
    """Update a student-parent link."""
    return await StudentParentLinkService.update_student_parent_link(
        db=db,
        actor=current_user,
        link_id=link_id,
        payload=payload,
    )


@router.delete(
    "/parent-links/{link_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a student-parent link",
)
async def delete_student_parent_link(
    link_id: UUID,
    db: DbSession,
    current_user: TenantAdminUser,
) -> None:
    """Delete a student-parent link."""
    await StudentParentLinkService.delete_student_parent_link(
        db=db,
        actor=current_user,
        link_id=link_id,
    )


@router.post(
    "/link-codes",
    response_model=StudentLinkCodeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a student link code",
)
async def create_student_link_code(
    payload: StudentLinkCodeCreate,
    db: DbSession,
    current_user: TenantAdminUser,
) -> StudentLinkCodeResponse:
    """Create a student link code."""
    return await StudentLinkCodeService.create_student_link_code(
        db=db,
        actor=current_user,
        payload=payload,
    )


@router.post(
    "/link-codes/redeem",
    response_model=StudentParentLinkResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Redeem a student link code",
)
async def redeem_student_link_code(
    payload: StudentLinkCodeRedeem,
    db: DbSession,
    current_user: CurrentTenantUser,
) -> StudentParentLinkResponse:
    """Link the logged-in parent to a student using a pairing code."""
    return await StudentLinkCodeService.redeem_student_link_code(
        db=db,
        actor=current_user,
        payload=payload,
    )
