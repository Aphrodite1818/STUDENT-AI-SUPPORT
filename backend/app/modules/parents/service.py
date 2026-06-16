from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.modules.parents.models import Parent
from app.modules.parents.repository import ParentRepository
from app.modules.parents.schemas import (
    ParentCreate,
    ParentLinkedStudentResponse,
    ParentResponse,
    ParentUpdate,
)
from app.modules.students.repository import StudentParentLinkRepository
from app.modules.students.schemas import StudentParentLinkResponse, StudentResponse
from app.modules.users.models import User, UserRole
from app.modules.users.repository import UserRepository


class ParentService:
    """Business logic for parent profiles."""

    @staticmethod
    def _ensure_tenant_user(actor: User) -> None:
        """Ensure the actor belongs to a tenant."""
        if not actor.tenant_id:
            raise ForbiddenException(detail="User is not attached to a tenant")

    @staticmethod
    def _ensure_admin(actor: User) -> None:
        """Ensure the actor is a tenant admin."""
        if actor.role != UserRole.ADMIN:
            raise ForbiddenException(detail="Only tenant admins can perform this action")

        ParentService._ensure_tenant_user(actor)

    @staticmethod
    async def create_parent_profile(
        db: AsyncSession,
        actor: User,
        payload: ParentCreate,
    ) -> ParentResponse:
        """Create a parent profile for an existing parent user."""
        ParentService._ensure_admin(actor)

        user = await UserRepository.get_user_by_id(
            db=db,
            user_id=payload.user_id,
        )
        if user is None:
            raise NotFoundException(detail="User not found")

        if user.tenant_id != actor.tenant_id:
            raise ForbiddenException(detail="You do not have access to this user")

        if user.role != UserRole.PARENT:
            raise BadRequestException(detail="User must have a parent role")

        existing_parent = await ParentRepository.get_parent_by_user_id(
            db=db,
            tenant_id=actor.tenant_id,
            user_id=payload.user_id,
        )
        if existing_parent is not None:
            raise BadRequestException(detail="Parent profile already exists for this user")

        parent = Parent(
            tenant_id=actor.tenant_id,
            user_id=payload.user_id,
            occupation=payload.occupation,
            address=payload.address,
            emergency_phone=payload.emergency_phone,
        )
        created_parent = await ParentRepository.create_parent(db=db, parent=parent)
        return ParentResponse.model_validate(created_parent)

    @staticmethod
    async def get_parent_profile(
        db: AsyncSession,
        actor: User,
        parent_id: UUID,
    ) -> ParentResponse:
        """Get a parent profile by id."""
        ParentService._ensure_tenant_user(actor)

        parent = await ParentRepository.get_parent_by_id(
            db=db,
            tenant_id=actor.tenant_id,
            parent_id=parent_id,
        )
        if parent is None:
            raise NotFoundException(detail="Parent profile not found")

        if actor.role == UserRole.PARENT and parent.user_id != actor.id:
            raise ForbiddenException(detail="You are not allowed to view this parent profile")

        return ParentResponse.model_validate(parent)

    @staticmethod
    async def get_parent_by_user_id(
        db: AsyncSession,
        actor: User,
        user_id: UUID,
    ) -> ParentResponse:
        """Get a parent profile by user id."""
        ParentService._ensure_tenant_user(actor)

        parent = await ParentRepository.get_parent_by_user_id(
            db=db,
            tenant_id=actor.tenant_id,
            user_id=user_id,
        )
        if parent is None:
            raise NotFoundException(detail="Parent profile not found")

        if actor.role == UserRole.PARENT and user_id != actor.id:
            raise ForbiddenException(detail="You are not allowed to view this parent profile")

        return ParentResponse.model_validate(parent)

    @staticmethod
    async def update_my_parent_profile(
        db: AsyncSession,
        actor: User,
        payload: ParentUpdate,
    ) -> ParentResponse:
        """Allow a parent to update their own profile."""
        ParentService._ensure_tenant_user(actor)

        if actor.role != UserRole.PARENT:
            raise ForbiddenException(detail="Only parents can update this profile")

        parent = await ParentRepository.get_parent_by_user_id(
            db=db,
            tenant_id=actor.tenant_id,
            user_id=actor.id,
        )
        if parent is None:
            raise NotFoundException(detail="Parent profile not found")

        update_data = payload.model_dump(exclude_unset=True)
        if not update_data:
            raise BadRequestException(detail="No update data provided")

        for field, value in update_data.items():
            setattr(parent, field, value)

        updated_parent = await ParentRepository.update_parent(
            db=db,
            parent=parent,
        )
        return ParentResponse.model_validate(updated_parent)

    @staticmethod
    async def get_all_parents(
        db: AsyncSession,
        actor: User,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[ParentResponse], int]:
        """Get a paginated list of parents for a tenant."""
        ParentService._ensure_admin(actor)
        limit = min(limit, 100)

        parents = await ParentRepository.get_all_parents(
            db=db,
            tenant_id=actor.tenant_id,
            skip=skip,
            limit=limit,
        )
        total = await ParentRepository.count_parents(
            db=db,
            tenant_id=actor.tenant_id,
        )

        return [ParentResponse.model_validate(parent) for parent in parents], total

    @staticmethod
    async def get_my_linked_students(
        db: AsyncSession,
        actor: User,
    ) -> tuple[list[ParentLinkedStudentResponse], int]:
        """Get students linked to the logged-in parent."""
        ParentService._ensure_tenant_user(actor)

        if actor.role != UserRole.PARENT:
            raise ForbiddenException(detail="Only parents can view linked students here")

        parent = await ParentRepository.get_parent_by_user_id(
            db=db,
            tenant_id=actor.tenant_id,
            user_id=actor.id,
        )
        if parent is None:
            raise NotFoundException(detail="Parent profile not found")

        links = await StudentParentLinkRepository.get_by_parent_id(
            db=db,
            tenant_id=actor.tenant_id,
            parent_id=parent.id,
        )

        linked_students = [
            ParentLinkedStudentResponse(
                student=StudentResponse.model_validate(link.student),
                link=StudentParentLinkResponse.model_validate(link),
            )
            for link in links
            if link.student is not None
        ]

        return linked_students, len(linked_students)

    @staticmethod
    async def update_parent_profile(
        db: AsyncSession,
        actor: User,
        parent_id: UUID,
        payload: ParentUpdate,
    ) -> ParentResponse:
        """Update a parent profile."""
        ParentService._ensure_admin(actor)

        parent = await ParentRepository.get_parent_by_id(
            db=db,
            tenant_id=actor.tenant_id,
            parent_id=parent_id,
        )
        if parent is None:
            raise NotFoundException(detail="Parent profile not found")

        update_data = payload.model_dump(exclude_unset=True)
        if not update_data:
            raise BadRequestException(detail="No update data provided")

        for field, value in update_data.items():
            setattr(parent, field, value)

        updated_parent = await ParentRepository.update_parent(
            db=db,
            parent=parent,
        )
        return ParentResponse.model_validate(updated_parent)

    @staticmethod
    async def delete_parent_profile(
        db: AsyncSession,
        actor: User,
        parent_id: UUID,
    ) -> None:
        """Delete a parent profile."""
        ParentService._ensure_admin(actor)

        parent = await ParentRepository.get_parent_by_id(
            db=db,
            tenant_id=actor.tenant_id,
            parent_id=parent_id,
        )
        if parent is None:
            raise NotFoundException(detail="Parent profile not found")

        await ParentRepository.delete_parent(
            db=db,
            parent=parent,
        )
