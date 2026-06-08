#======================================#
#           user service.py            #
#======================================#

import secrets
import uuid

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.logging import get_logger
from app.config.security import hash_password
from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.modules.users.models import AccountStatus, User, UserRole
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserAdminUpdate, UserInviteCreate, UserUpdate
from app.modules.auth.service import UserInviteService
from app.tenant_management.repository import TenantRepository

logger = get_logger(__name__)


def _normalize_email(email: str) -> str:
    return email.strip().lower()


class UserService:
    """Handle user-related business logic."""

    @staticmethod
    async def register_user(
        db: AsyncSession,
        actor: User,
        user_data: UserInviteCreate,
        background_tasks: BackgroundTasks | None = None,
        frontend_app_url: str | None = None,
    ) -> User:
        """Create a tenant-scoped invited user after validating uniqueness constraints."""
        logger.debug(
            "Starting tenant user invite",
            extra={"email": user_data.email, "phone_number": user_data.phone_number},
        )

        if actor.role != UserRole.ADMIN:
            raise ForbiddenException(
                detail="Only tenant admins can create invited tenant users."
            )

        if user_data.role in (UserRole.ADMIN, UserRole.SUPERADMIN):
            raise ForbiddenException(
                detail="Tenant admins can only invite normal tenant users."
            )

        existing_email = await UserRepository.get_user_by_email(db, user_data.email)
        if existing_email:
            logger.warning(
                "Registration rejected - email already in use",
                extra={"email": user_data.email},
            )
            raise BadRequestException(
                detail="A user with this email already exists."
            )

        existing_phone = await UserRepository.get_by_phone_number(db, user_data.phone_number)
        if existing_phone:
            logger.warning(
                "Registration rejected - phone number already in use",
                extra={"phone_number": user_data.phone_number},
            )
            raise BadRequestException(
                detail="A user with this phone number already exists."
            )

        if user_data.whatsapp_id:
            existing_whatsapp = await UserRepository.get_by_whatsapp_id(
                db,
                user_data.whatsapp_id,
            )
            if existing_whatsapp:
                logger.warning(
                    "Registration rejected - WhatsApp ID already in use",
                    extra={"whatsapp_id": user_data.whatsapp_id},
                )
                raise BadRequestException(
                    detail="A user with this WhatsApp ID already exists."
                )

        tenant = await TenantRepository.get_by_id(db, actor.tenant_id)
        if tenant is None:
            raise NotFoundException(detail="Tenant not found.")

        user_dict = user_data.model_dump()
        user_dict["email"] = _normalize_email(user_data.email)
        user_dict["tenant_id"] = actor.tenant_id
        user_dict["password_hash"] = hash_password(secrets.token_urlsafe(32))
        user_dict["account_status"] = AccountStatus.PENDING
        user_dict["is_verified"] = False
        new_user = User(**user_dict)

        created_user = await UserRepository.create_user(db, new_user)
        invite_link = await UserInviteService.create_invite_record(
            db,
            user=created_user,
            frontend_app_url=frontend_app_url,
        )
        await db.commit()
        await db.refresh(created_user)

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
            },
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

        if db_user.role in (UserRole.ADMIN, UserRole.SUPERADMIN):
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
    async def get_all_users(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        tenant_id: uuid.UUID | None = None,
    ) -> list[User]:
        """Return a paginated list of users."""
        log_extra = {"skip": skip, "limit": limit}
        if tenant_id is not None:
            log_extra["tenant_id"] = str(tenant_id)

        logger.debug("Fetching paginated user list", extra=log_extra)
        users = await UserRepository.get_all_users(
            db,
            skip=skip,
            limit=limit,
            tenant_id=tenant_id,
        )

        info_extra = {"count": len(users), "skip": skip, "limit": limit}
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
        db_user = await UserRepository.get_user_by_id(db, user_id)
        if not db_user:
            logger.warning(
                "Admin update failed - user not found",
                extra={"user_id": str(user_id)},
            )
            raise NotFoundException(detail="User not found.")

        requested_role = admin_data.role
        if actor.role != UserRole.SUPERADMIN:
            if db_user.role == UserRole.SUPERADMIN:
                raise ForbiddenException(
                    detail="Only superadmins can manage superadmin accounts."
                )
            if requested_role == UserRole.SUPERADMIN:
                raise ForbiddenException(
                    detail="Only superadmins can assign the superadmin role."
                )

        for key, value in update_dict.items():
            setattr(db_user, key, value)

        updated_user = await UserRepository.save_user(db, db_user)
        logger.info(
            "User updated by admin",
            extra={"user_id": str(user_id), "changed_fields": changed_fields},
        )
        return updated_user

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: uuid.UUID) -> dict:
        """Delete a user and return a confirmation payload."""
        logger.debug("Attempting user deletion", extra={"user_id": str(user_id)})
        db_user = await UserRepository.get_user_by_id(db, user_id)
        if not db_user:
            logger.warning(
                "Deletion failed - user not found",
                extra={"user_id": str(user_id)},
            )
            raise NotFoundException(detail="User not found.")

        await UserRepository.delete_user(db, db_user)
        logger.info("User deleted successfully", extra={"user_id": str(user_id)})
        return {"detail": "User successfully deleted"}
