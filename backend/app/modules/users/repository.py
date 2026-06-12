#======================================#
#          user repository.py          #
#======================================#

import uuid
from typing import Any

from sqlalchemy import exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession  # to be used as annotation

from app.config.logging import get_logger
from app.modules.users.models import User

logger = get_logger(__name__)


def _normalize_email(email: str) -> str:
    """Normalize the email address."""
    return email.strip().lower()


class UserRepository:
    """
    Provides database methods for performing CRUD operations
    on users.
    """

    # create
    @staticmethod
    async def create_user(db: AsyncSession, user: User) -> User:
        """Create user."""
        logger.debug(
            "Persisting new user to session",
            extra={"tenant_id": str(user.tenant_id), "email": user.email},
        )

        db.add(user)
        await db.flush()
        await db.refresh(user)

        logger.info(
            "User created successfully",
            extra={
                "tenant_id": str(user.tenant_id),
                "user_id": str(user.id),
                "email": user.email,
            },
        )

        return user

    # read
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> User | None:
        """Return user by id."""
        logger.debug(
            "Querying user by ID",
            extra={"user_id": str(user_id)},
        )

        result = await db.execute(
            select(User).where(User.id == user_id)
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
        """Return user by email."""
        normalized_email = _normalize_email(email)
        logger.debug(
            "Querying user by email",
            extra={"email": normalized_email},
        )

        result = await db.execute(
            select(User).where(func.lower(User.email) == normalized_email)
        )

        return result.scalar_one_or_none()
    

    @staticmethod
    async def get_by_phone_number(db: AsyncSession, phone_number: str) -> User | None:
        """Return the record matched by phone number."""
        logger.debug(
            "Querying user by phone number",
            extra={"phone_number": phone_number},
        )

        result = await db.execute(
            select(User).where(User.phone_number == phone_number)
        )

        return result.scalar_one_or_none()


    @staticmethod
    async def get_by_whatsapp_id(db: AsyncSession, whatsapp_id: str) -> User | None:
        """Return the record matched by whatsapp id."""
        logger.debug(
            "Querying user by WhatsApp ID",
            extra={"whatsapp_id": whatsapp_id},
        )

        result = await db.execute(
            select(User).where(User.whatsapp_id == whatsapp_id)
        )

        return result.scalar_one_or_none()


    @staticmethod
    async def get_all_users(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        tenant_id: uuid.UUID | None = None,
        role: str | None = None,
    ) -> list[User]:
        """Return all users."""
        log_extra: dict[str, Any] = {"skip": skip, "limit": limit}
        if tenant_id is not None:
            log_extra["tenant_id"] = str(tenant_id)
        if role is not None:
            log_extra["role"] = str(role)

        logger.debug("Querying users", extra=log_extra)

        statement = select(User)
        if tenant_id is not None:
            statement = statement.where(User.tenant_id == tenant_id)
        if role is not None:
            statement = statement.where(User.role == role)

        result = await db.execute(
            statement.offset(skip).limit(limit)
        )

        users = list(result.scalars().all())

        info_extra: dict[str, Any] = {
            "count": len(users),
            "skip": skip,
            "limit": limit,
        }
        if tenant_id is not None:
            info_extra["tenant_id"] = str(tenant_id)

        logger.info("Fetched user list", extra=info_extra)

        return users


    @staticmethod
    async def check_email_exists(db: AsyncSession, email: str) -> bool:
        """Perform check email exists."""
        normalized_email = _normalize_email(email)
        result = await db.execute(
            select(exists().where(func.lower(User.email) == normalized_email))
        )

        return bool(result.scalar())

    @staticmethod
    async def save_user(db: AsyncSession, user: User) -> User:
        """Perform save user."""
        logger.debug(
            "Flushing user changes",
            extra={"tenant_id": str(user.tenant_id), "user_id": str(user.id)},
        )

        db.add(user)
        await db.flush()
        # Hydrate server-managed fields such as updated_at before the ORM
        # instance leaves the async session boundary and FastAPI serializes it.
        await db.refresh(user)

        logger.info(
            "User persisted successfully",
            extra={"tenant_id": str(user.tenant_id), "user_id": str(user.id)},
        )

        return user

    @staticmethod
    async def delete_user(db: AsyncSession, user: User) -> None:
        """Delete user."""
        logger.debug(
            "Deleting user",
            extra={"tenant_id": str(user.tenant_id), "user_id": str(user.id)},
        )

        await db.delete(user)
        await db.flush()

        logger.info(
            "User deleted",
            extra={"tenant_id": str(user.tenant_id), "user_id": str(user.id)},
        )
