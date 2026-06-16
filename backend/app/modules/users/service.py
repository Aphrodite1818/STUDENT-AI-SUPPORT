#======================================#
#           user service.py            #
#======================================#

import secrets
import uuid
from typing import Any

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.logging import get_logger
from app.config.security import hash_password
from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.modules.auth.service import UserInviteService
from app.modules.parents.models import Parent
from app.modules.parents.repository import ParentRepository
from app.modules.students.models import (
    AcademicStatus,
    ParentRelationship,
    Student,
    StudentParentLink,
    StudentProfileStatus,
)
from app.modules.students.repository import StudentParentLinkRepository, StudentRepository
from app.modules.teachers.models import Teacher, TeacherStatus
from app.modules.teachers.repository import TeacherRepository
from app.modules.users.models import AccountStatus, User, UserRole
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import AuthenticatedUserResponse
from app.modules.users.schemas import UserAdminUpdate, UserInviteCreate, UserUpdate
from app.tenant_management.repository import TenantRepository

logger = get_logger(__name__)


def _normalize_email(email: str) -> str:
    """Normalize the email address."""
    return email.strip().lower()


class UserService:
    """Handle user-related business logic."""

    @staticmethod
    async def _activate_teacher_profile(
        db: AsyncSession,
        *,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Teacher:
        """Internal helper for activate teacher profile."""
        teacher = await TeacherRepository.get_teacher_by_user_id(
            db=db,
            tenant_id=tenant_id,
            user_id=user_id,
        )

        if teacher:
            teacher.status = TeacherStatus.ACTIVE
            return await TeacherRepository.update_teacher(db=db, teacher=teacher)

        return await TeacherRepository.create_teacher(
            db=db,
            teacher=Teacher(
                tenant_id=tenant_id,
                user_id=user_id,
                status=TeacherStatus.ACTIVE,
            ),
        )

    @staticmethod
    async def _archive_teacher_profile(
        db: AsyncSession,
        *,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> None:
        """Internal helper for archive teacher profile."""
        teacher = await TeacherRepository.get_teacher_by_user_id(
            db=db,
            tenant_id=tenant_id,
            user_id=user_id,
        )

        if not teacher:
            logger.warning(
                "Teacher user has no teacher profile to archive",
                extra={"tenant_id": str(tenant_id), "user_id": str(user_id)},
            )
            return

        teacher.status = TeacherStatus.ARCHIVED
        await TeacherRepository.update_teacher(db=db, teacher=teacher)
        await TeacherRepository.delete_all_teacher_subject_links(
            db=db,
            tenant_id=tenant_id,
            teacher_id=teacher.id,
        )

    @staticmethod
    async def _ensure_student_profile(
        db: AsyncSession,
        *,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Student:
        """Create the invite-time student profile if it does not already exist."""
        student = await StudentRepository.get_by_user_id(
            db=db,
            tenant_id=tenant_id,
            user_id=user_id,
        )
        if student:
            return student

        return await StudentRepository.create_student(
            db=db,
            student=Student(
                tenant_id=tenant_id,
                user_id=user_id,
                status=AcademicStatus.ACTIVE,
                profile_status=StudentProfileStatus.INCOMPLETE,
            ),
        )

    @staticmethod
    async def _ensure_parent_profile(
        db: AsyncSession,
        *,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Parent:
        """Create the invite-time parent profile if it does not already exist."""
        parent = await ParentRepository.get_parent_by_user_id(
            db=db,
            tenant_id=tenant_id,
            user_id=user_id,
        )
        if parent:
            return parent

        return await ParentRepository.create_parent(
            db=db,
            parent=Parent(
                tenant_id=tenant_id,
                user_id=user_id,
            ),
        )

    @staticmethod
    async def _ensure_invited_business_profile(
        db: AsyncSession,
        *,
        user: User,
    ) -> None:
        """Ensure the invited user's role-specific business profile exists."""
        if not user.tenant_id:
            raise BadRequestException(detail="Invited user must belong to a tenant.")

        if user.role == UserRole.TEACHER:
            await UserService._activate_teacher_profile(
                db=db,
                tenant_id=user.tenant_id,
                user_id=user.id,
            )
        elif user.role == UserRole.STUDENT:
            await UserService._ensure_student_profile(
                db=db,
                tenant_id=user.tenant_id,
                user_id=user.id,
            )
        elif user.role == UserRole.PARENT:
            await UserService._ensure_parent_profile(
                db=db,
                tenant_id=user.tenant_id,
                user_id=user.id,
            )

    @staticmethod
    async def _ensure_invite_identity_is_available(
        db: AsyncSession,
        *,
        email: str,
        phone_number: str | None = None,
        whatsapp_id: str | None = None,
        label: str = "A user",
    ) -> None:
        """Validate that the invite identity fields are available."""
        existing_email = await UserRepository.get_user_by_email(db, email)
        if existing_email:
            logger.warning(
                "Registration rejected - email already in use",
                extra={"email": email},
            )
            raise BadRequestException(detail=f"{label} with this email already exists.")

        if phone_number:
            existing_phone = await UserRepository.get_by_phone_number(
                db,
                phone_number,
            )
            if existing_phone:
                logger.warning(
                    "Registration rejected - phone number already in use",
                    extra={"phone_number": phone_number},
                )
                raise BadRequestException(
                    detail=f"{label} with this phone number already exists."
                )

        if whatsapp_id:
            existing_whatsapp = await UserRepository.get_by_whatsapp_id(
                db,
                whatsapp_id,
            )
            if existing_whatsapp:
                logger.warning(
                    "Registration rejected - WhatsApp ID already in use",
                    extra={"whatsapp_id": whatsapp_id},
                )
                raise BadRequestException(
                    detail=f"{label} with this WhatsApp ID already exists."
                )

    @staticmethod
    async def _create_pending_tenant_user(
        db: AsyncSession,
        *,
        tenant_id: uuid.UUID,
        role: UserRole,
        firstname: str | None,
        lastname: str | None,
        email: str,
        phone_number: str | None = None,
        whatsapp_id: str | None = None,
    ) -> User:
        """Create a pending tenant user and ensure its business profile exists."""
        created_user = await UserRepository.create_user(
            db,
            User(
                tenant_id=tenant_id,
                firstname=firstname,
                lastname=lastname,
                email=email,
                phone_number=phone_number,
                whatsapp_id=whatsapp_id,
                password_hash=hash_password(secrets.token_urlsafe(32)),
                account_status=AccountStatus.PENDING,
                role=role,
                is_verified=False,
            ),
        )

        await db.flush()
        await UserService._ensure_invited_business_profile(
            db=db,
            user=created_user,
        )
        return created_user

    @staticmethod
    async def _resolve_parent_for_student_invite(
        db: AsyncSession,
        *,
        tenant_id: uuid.UUID,
        student_invite: UserInviteCreate,
    ) -> tuple[User, Parent, bool]:
        """Resolve or create the parent account for a student invite."""
        parent_email = _normalize_email(student_invite.parent_email or "")
        student_email = _normalize_email(student_invite.email)

        if parent_email == student_email:
            raise BadRequestException(
                detail="parent_email must be different from the student's email."
            )

        parent_user = await UserRepository.get_user_by_email(db, parent_email)
        if parent_user is not None:
            if parent_user.tenant_id != tenant_id:
                raise BadRequestException(
                    detail="parent_email already belongs to a user in another tenant."
                )
            if parent_user.role != UserRole.PARENT:
                raise BadRequestException(
                    detail="parent_email already belongs to a non-parent user in this tenant."
                )

            parent_profile = await UserService._ensure_parent_profile(
                db=db,
                tenant_id=tenant_id,
                user_id=parent_user.id,
            )
            invite_required = (
                parent_user.account_status == AccountStatus.PENDING
                or not parent_user.is_verified
            )
            return parent_user, parent_profile, invite_required

        await UserService._ensure_invite_identity_is_available(
            db=db,
            email=parent_email,
            phone_number=student_invite.parent_phone_number,
            whatsapp_id=student_invite.parent_whatsapp_id,
            label="A parent user",
        )

        parent_user = await UserService._create_pending_tenant_user(
            db=db,
            tenant_id=tenant_id,
            role=UserRole.PARENT,
            firstname=student_invite.parent_firstname or "Parent",
            lastname=student_invite.parent_lastname or student_invite.lastname,
            email=parent_email,
            phone_number=student_invite.parent_phone_number,
            whatsapp_id=student_invite.parent_whatsapp_id,
        )
        parent_profile = await UserService._ensure_parent_profile(
            db=db,
            tenant_id=tenant_id,
            user_id=parent_user.id,
        )
        return parent_user, parent_profile, True

    @staticmethod
    async def _ensure_student_parent_link(
        db: AsyncSession,
        *,
        tenant_id: uuid.UUID,
        student_user_id: uuid.UUID,
        parent_id: uuid.UUID,
        relationship_type: ParentRelationship,
    ) -> None:
        """Ensure the student-parent relationship exists."""
        student = await StudentRepository.get_by_user_id(
            db=db,
            tenant_id=tenant_id,
            user_id=student_user_id,
        )
        if student is None:
            raise NotFoundException(detail="Student profile not found")

        existing_link = await StudentParentLinkRepository.get_by_student_and_parent(
            db=db,
            student_id=student.id,
            tenant_id=tenant_id,
            parent_id=parent_id,
        )
        if existing_link is not None:
            return

        await StudentParentLinkRepository.create_student_parent_link(
            db=db,
            link=StudentParentLink(
                tenant_id=tenant_id,
                student_id=student.id,
                parent_id=parent_id,
                relationship_type=relationship_type,
            ),
        )

    @staticmethod
    async def register_user(
        db: AsyncSession,
        actor: User,
        user_data: UserInviteCreate,
        background_tasks: BackgroundTasks | None = None,
        frontend_app_url: str | None = None,
    ) -> User:
        """Create a tenant-scoped invited user after validating uniqueness constraints."""
        normalized_email = _normalize_email(user_data.email)
        actor_id = actor.id
        actor_tenant_id = actor.tenant_id

        logger.debug(
            "Starting tenant user invite",
            extra={
                "email": normalized_email,
                "phone_number": user_data.phone_number,
                "actor_id": str(actor_id),
                "tenant_id": str(actor_tenant_id),
            },
        )

        if actor.role != UserRole.ADMIN:
            raise ForbiddenException(
                detail="Only tenant admins can create invited tenant users."
            )

        if not actor.tenant_id:
            raise ForbiddenException(
                detail="Admin user is not attached to a tenant."
            )

        if user_data.role == UserRole.ADMIN:
            raise ForbiddenException(
                detail="Tenant admins can only invite normal tenant users."
            )

        await UserService._ensure_invite_identity_is_available(
            db=db,
            email=normalized_email,
            phone_number=user_data.phone_number,
            whatsapp_id=user_data.whatsapp_id,
        )

        tenant = await TenantRepository.get_by_id(db, actor.tenant_id)
        if tenant is None:
            raise NotFoundException(detail="Tenant not found.")

        created_user: User | None = None
        parent_user: User | None = None
        parent_invite_link: str | None = None

        try:
            created_user = await UserService._create_pending_tenant_user(
                db=db,
                tenant_id=actor.tenant_id,
                role=user_data.role,
                firstname=user_data.firstname,
                lastname=user_data.lastname,
                email=normalized_email,
                phone_number=user_data.phone_number,
                whatsapp_id=user_data.whatsapp_id,
            )

            if user_data.role == UserRole.STUDENT:
                parent_user, parent_profile, parent_invite_required = (
                    await UserService._resolve_parent_for_student_invite(
                        db=db,
                        tenant_id=actor.tenant_id,
                        student_invite=user_data,
                    )
                )
                await UserService._ensure_student_parent_link(
                    db=db,
                    tenant_id=actor.tenant_id,
                    student_user_id=created_user.id,
                    parent_id=parent_profile.id,
                    relationship_type=user_data.parent_relationship_type,
                )

            invite_link = await UserInviteService.create_invite_record(
                db,
                user=created_user,
                frontend_app_url=frontend_app_url,
            )

            if parent_user is not None and parent_invite_required:
                parent_invite_link = await UserInviteService.create_invite_record(
                    db,
                    user=parent_user,
                    frontend_app_url=frontend_app_url,
                )

            await db.commit()
            await db.refresh(created_user)

        except Exception:
            await db.rollback()
            logger.exception(
                "Tenant user invite failed",
                extra={
                    "email": normalized_email,
                    "phone_number": user_data.phone_number,
                    "tenant_id": str(actor_tenant_id),
                },
            )
            raise

        if created_user is None:
            raise NotFoundException(detail="Invited user was not created.")

        user_name = " ".join(
            part for part in (created_user.firstname, created_user.lastname) if part
        ) or created_user.email

        await UserInviteService.send_invite_email(
            email=created_user.email,
            user_name=user_name,
            school_name=tenant.school_name,
            invite_link=invite_link,
            background_tasks=background_tasks,
        )

        logger.info(
            "Tenant user invited successfully",
            extra={
                "user_id": str(created_user.id),
                "email": created_user.email,
                "phone_number": created_user.phone_number,
                "tenant_id": str(created_user.tenant_id),
            },
        )

        if parent_user is not None and parent_invite_link is not None:
            parent_name = " ".join(
                part for part in (parent_user.firstname, parent_user.lastname) if part
            ) or parent_user.email
            await UserInviteService.send_invite_email(
                email=parent_user.email,
                user_name=parent_name,
                school_name=tenant.school_name,
                invite_link=parent_invite_link,
                background_tasks=background_tasks,
            )

        return created_user



    @staticmethod
    async def resend_invite(
        db: AsyncSession,
        actor: User,
        user_id: uuid.UUID,
        background_tasks: BackgroundTasks | None = None,
        frontend_app_url: str | None = None,
    ) -> dict[str, str]:
        """Perform resend invite."""
        if actor.role != UserRole.ADMIN:
            raise ForbiddenException(
                detail="Only tenant admins can resend tenant user invites."
            )

        db_user = await UserRepository.get_user_by_id(db, user_id)
        if not db_user:
            raise NotFoundException(detail="User not found.")

        if db_user.tenant_id != actor.tenant_id:
            raise ForbiddenException(
                detail="Admins can only invite users inside their own tenant."
            )

        if db_user.role == UserRole.ADMIN:
            raise BadRequestException(
                detail="Invite resend is only available for normal tenant users."
            )

        if db_user.account_status != AccountStatus.PENDING or db_user.is_verified:
            raise BadRequestException(
                detail="Only pending invited users can receive a new invite link."
            )

        tenant = await TenantRepository.get_by_id(db, actor.tenant_id)
        if tenant is None:
            raise NotFoundException(detail="Tenant not found.")

        invite_link = await UserInviteService.create_invite_record(
            db,
            user=db_user,
            frontend_app_url=frontend_app_url,
        )
        await db.commit()

        user_name = " ".join(
            part for part in (db_user.firstname, db_user.lastname) if part
        ) or db_user.email
        await UserInviteService.send_invite_email(
            email=db_user.email,
            user_name=user_name,
            school_name=tenant.school_name,
            invite_link=invite_link,
            background_tasks=background_tasks,
        )
        return {"detail": "A new invite link has been emailed to the user."}




    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> User:
        """Fetch a single user by ID or raise if it does not exist."""
        logger.debug("Fetching user by ID", extra={"user_id": str(user_id)})
        user = await UserRepository.get_user_by_id(db, user_id)
        if not user:
            logger.warning(
                "User lookup failed - not found",
                extra={"user_id": str(user_id)},
            )
            raise NotFoundException(detail="User not found.")
        logger.debug(
            "User fetched successfully",
            extra={"user_id": str(user_id), "email": user.email},
        )
        return user

    @staticmethod
    async def get_authenticated_user_context(
        db: AsyncSession,
        actor: User,
    ) -> AuthenticatedUserResponse:
        """Return the authenticated user plus tenant context."""
        tenant = None
        if actor.tenant_id is not None:
            tenant = await TenantRepository.get_by_id(db, actor.tenant_id)

        return AuthenticatedUserResponse.model_validate(
            {
                **AuthenticatedUserResponse.model_validate(actor).model_dump(),
                "tenant": tenant,
            }
        )




    @staticmethod
    async def get_all_users(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        tenant_id: uuid.UUID | None = None,
    ) -> list[User]:
        """Return a paginated list of users."""
        log_extra: dict[str, Any] = {"skip": skip, "limit": limit}
        if tenant_id is not None:
            log_extra["tenant_id"] = str(tenant_id)

        logger.debug("Fetching paginated user list", extra=log_extra)
        users = await UserRepository.get_all_users(
            db,
            skip=skip,
            limit=limit,
            tenant_id=tenant_id,
        )

        info_extra: dict[str, Any] = {
            "count": len(users),
            "skip": skip,
            "limit": limit,
        }
        if tenant_id is not None:
            info_extra["tenant_id"] = str(tenant_id)

        logger.info("User list retrieved", extra=info_extra)
        return users



    @staticmethod
    async def update_profile(
        db: AsyncSession,
        user_id: uuid.UUID,
        update_data: UserUpdate,
    ) -> User:
        """Update mutable profile fields for a user."""
        update_dict = update_data.model_dump(exclude_unset=True)
        changed_fields = list(update_dict.keys())
        logger.debug(
            "Attempting profile update",
            extra={"user_id": str(user_id), "changed_fields": changed_fields},
        )

        current_user = await UserRepository.get_user_by_id(db, user_id)
        if not current_user:
            logger.warning(
                "Profile update failed - user not found",
                extra={"user_id": str(user_id)},
            )
            raise NotFoundException(detail="User not found.")

        if update_data.email:
            normalized_email = _normalize_email(update_data.email)
            tenant = await TenantRepository.get_by_id(db, current_user.tenant_id)
            if (
                tenant is not None
                and current_user.role == UserRole.ADMIN
                and _normalize_email(current_user.email) == _normalize_email(tenant.email)
                and normalized_email != _normalize_email(current_user.email)
            ):
                raise BadRequestException(
                    detail="The primary administrator email cannot be changed from this endpoint."
                )
            if normalized_email == _normalize_email(current_user.email):
                update_dict["email"] = normalized_email
            else:
                existing_email = await UserRepository.get_user_by_email(db, normalized_email)
                if existing_email:
                    raise BadRequestException(detail="A user with this email already exists.")
                update_dict["email"] = normalized_email

        if (
            update_data.phone_number
            and update_data.phone_number != current_user.phone_number
        ):
            existing_phone = await UserRepository.get_by_phone_number(
                db,
                update_data.phone_number,
            )
            if existing_phone:
                raise BadRequestException(
                    detail="A user with this phone number already exists."
                )

        if update_data.whatsapp_id and update_data.whatsapp_id != current_user.whatsapp_id:
            existing_whatsapp = await UserRepository.get_by_whatsapp_id(
                db,
                update_data.whatsapp_id,
            )
            if existing_whatsapp:
                raise BadRequestException(
                    detail="A user with this WhatsApp ID already exists."
                )

        for key, value in update_dict.items():
            setattr(current_user, key, value)

        updated_user = await UserRepository.save_user(db, current_user)
        logger.info(
            "User profile updated",
            extra={"user_id": str(user_id), "changed_fields": changed_fields},
        )
        return updated_user





    @staticmethod
    async def update_admin_status(
        db: AsyncSession,
        actor: User,
        user_id: uuid.UUID,
        admin_data: UserAdminUpdate,
    ) -> User:
        """Update admin-managed user fields."""
        update_dict = admin_data.model_dump(exclude_unset=True)
        changed_fields = list(update_dict.keys())
        logger.debug(
            "Attempting admin-level user update",
            extra={"user_id": str(user_id), "changed_fields": changed_fields},
        )

        if actor.role != UserRole.ADMIN:
            raise ForbiddenException(
                detail="Only tenant admins can perform admin-level user updates."
            )

        if not actor.tenant_id:
            raise ForbiddenException(detail="Admin user is not attached to a tenant.")

        db_user = await UserRepository.get_user_by_id(db, user_id)
        if not db_user:
            logger.warning(
                "Admin update failed - user not found",
                extra={"user_id": str(user_id)},
            )
            raise NotFoundException(detail="User not found.")

        if db_user.tenant_id != actor.tenant_id:
            raise ForbiddenException(
                detail="Admins can only manage users inside their own tenant."
            )

        requested_role = admin_data.role
        current_role = db_user.role

        if db_user.role == UserRole.ADMIN:
            raise ForbiddenException(
                detail="Tenant admins cannot manage other administrator accounts."
            )
        if requested_role == UserRole.ADMIN:
            raise ForbiddenException(
                detail="Tenant admins cannot assign administrator roles."
            )

        try:
            for key, value in update_dict.items():
                setattr(db_user, key, value)

            updated_user = await UserRepository.save_user(db, db_user)

            if requested_role is not None and requested_role != current_role:
                if (
                    current_role != UserRole.TEACHER
                    and requested_role == UserRole.TEACHER
                ):
                    await UserService._activate_teacher_profile(
                        db=db,
                        tenant_id=actor.tenant_id,
                        user_id=db_user.id,
                    )
                elif (
                    current_role == UserRole.TEACHER
                    and requested_role != UserRole.TEACHER
                ):
                    await UserService._archive_teacher_profile(
                        db=db,
                        tenant_id=actor.tenant_id,
                        user_id=db_user.id,
                    )

            await db.commit()
            await db.refresh(updated_user)

        except Exception:
            await db.rollback()
            logger.exception(
                "Admin-level user update failed",
                extra={
                    "user_id": str(user_id),
                    "tenant_id": str(actor.tenant_id),
                    "changed_fields": changed_fields,
                },
            )
            raise

        logger.info(
            "User updated by admin",
            extra={"user_id": str(user_id), "changed_fields": changed_fields},
        )
        return updated_user




    @staticmethod
    async def delete_user(db: AsyncSession, user_id: uuid.UUID) -> dict[str, str]:
        """Delete a user and return a confirmation payload."""
        logger.debug("Attempting user deletion", extra={"user_id": str(user_id)})
        db_user = await UserRepository.get_user_by_id(db, user_id)
        if not db_user:
            logger.warning(
                "Deletion failed - user not found",
                extra={"user_id": str(user_id)},
            )
            raise NotFoundException(detail="User not found.")

        teacher_profile = await TeacherRepository.get_teacher_by_user_id(
            db=db,
            tenant_id=db_user.tenant_id,
            user_id=db_user.id,
        )
        if teacher_profile:
            raise BadRequestException(
                detail=(
                    "Users with teacher history cannot be permanently deleted. "
                    "Change their role or deactivate the account to preserve audit history."
                )
            )

        await UserRepository.delete_user(db, db_user)
        logger.info("User deleted successfully", extra={"user_id": str(user_id)})
        return {"detail": "User successfully deleted"}
