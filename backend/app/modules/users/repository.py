#======================================#
#          user repository.py          #
#======================================#


import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.modules.users.models import User
from backend.app.modules.users.schemas import UserAdminUpdate, UserUpdate
from backend.app.config.logging import get_logger


logger = get_logger(__name__)


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session



    """create"""
    async def create_user(self, user: User) -> User:
        logger.debug(
            "Persisting new user to session",
            extra={"email": user.email},
        )
        self.session.add(user)
        await self.session.flush()
        logger.info(
            "User created successfully",
            extra={
                "user_id": str(user.id),
                "email": user.email,
                "name": f"{user.firstname} {getattr(user, 'lastname', '')}".strip(),
            },
        )
        return user






    """read"""
    async def get_user_by_id(self, user_id: uuid.UUID) -> User | None:
        logger.debug("Querying user by ID", extra={"user_id": str(user_id)})
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if user is None:
            logger.warning(
                "User not found by ID", extra={"user_id": str(user_id)}
            )
        else:
            logger.debug(
                "User fetched by ID",
                extra={"user_id": str(user_id), "email": user.email},
            )
        return user

    async def get_user_by_email(self, email: str) -> User | None:
        logger.debug("Querying user by email", extra={"email": email})
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        if user is None:
            logger.warning("User not found by email", extra={"email": email})
        else:
            logger.debug(
                "User fetched by email",
                extra={"user_id": str(user.id), "email": email},
            )
        return user

    async def get_by_phone_number(self, phone_number: str) -> User | None:
        logger.debug(
            "Querying user by phone number",
            extra={"phone_number": phone_number},
        )
        result = await self.session.execute(
            select(User).where(User.phone_number == phone_number)
        )
        user = result.scalar_one_or_none()
        if user is None:
            logger.warning(
                "User not found by phone number",
                extra={"phone_number": phone_number},
            )
        else:
            logger.debug(
                "User fetched by phone number",
                extra={"user_id": str(user.id), "phone_number": phone_number},
            )
        return user

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        logger.debug(
            "Querying all users", extra={"skip": skip, "limit": limit}
        )
        result = await self.session.execute(
            select(User).offset(skip).limit(limit)
        )
        users = result.scalars().all()
        logger.info(
            "Fetched user list",
            extra={"count": len(users), "skip": skip, "limit": limit},
        )
        return users
    

    async def check_email_exists(self, email: str) -> bool:
        result = await self.session.execute(
            select(User).where(
                User.email == email
            )
        )
        return result.scalar_one_or_none() is not None
    





    """update"""
    async def update_user(
        self, user_id: uuid.UUID, user_data: UserUpdate
    ) -> User | None:
        logger.debug(
            "Attempting user self-update", extra={"user_id": str(user_id)}
        )
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        db_user = result.scalar_one_or_none()

        if db_user is None:
            logger.warning(
                "Update aborted — user not found",
                extra={"user_id": str(user_id)},
            )
            return None

        update_dict = user_data.model_dump(exclude_unset=True)
        changed_fields = list(update_dict.keys())

        for key, value in update_dict.items():
            setattr(db_user, key, value)

        self.session.add(db_user)
        logger.info(
            "User updated",
            extra={"user_id": str(user_id), "changed_fields": changed_fields},
        )
        return db_user

    async def update_user_admin(
        self, user_id: uuid.UUID, user_data: UserAdminUpdate
    ) -> User | None:
        logger.debug(
            "Attempting admin user update", extra={"user_id": str(user_id)}
        )
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        db_user = result.scalar_one_or_none()

        if db_user is None:
            logger.warning(
                "Admin update aborted — user not found",
                extra={"user_id": str(user_id)},
            )
            return None

        update_dict = user_data.model_dump(exclude_unset=True)
        changed_fields = list(update_dict.keys())

        for key, value in update_dict.items():
            setattr(db_user, key, value)

        self.session.add(db_user)
        logger.info(
            "User updated by admin",
            extra={"user_id": str(user_id), "changed_fields": changed_fields},
        )
        return db_user







    """delete"""
    async def delete_user(self, user_id: uuid.UUID) -> bool:
        logger.debug(
            "Attempting user deletion", extra={"user_id": str(user_id)}
        )
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        db_user = result.scalar_one_or_none()

        if db_user is None:
            logger.warning(
                "Delete aborted — user not found",
                extra={"user_id": str(user_id)},
            )
            return False

        await self.session.delete(db_user)
        logger.info(
            "User deleted", extra={"user_id": str(user_id), "email": db_user.email}
        )
        return True