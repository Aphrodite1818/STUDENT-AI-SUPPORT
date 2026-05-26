#======================================#
#           user service.py            #
#======================================#



import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.config.logging import get_logger
from backend.app.config.security import hash_password
from backend.app.modules.users.models import User
from backend.app.modules.users.repository import UserRepository
from backend.app.modules.users.schemas import UserAdminUpdate, UserCreate, UserUpdate


logger = get_logger(__name__)


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = UserRepository(session=session)


    """create"""
    async def register_user(self, user_data: UserCreate) -> User:
        logger.debug(
            "Starting user registration",
            extra={"email": user_data.email, "phone_number": user_data.phone_number},
        )

        # 1. Check if email is already taken
        if user_data.email:
            existing_email = await self.repo.get_user_by_email(user_data.email)
            if existing_email:
                logger.warning(
                    "Registration rejected — email already in use",
                    extra={"email": user_data.email},
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A user with this email already exists.",
                )

        # 2. Check if phone number is already taken
        existing_phone = await self.repo.get_by_phone_number(user_data.phone_number)
        if existing_phone:
            logger.warning(
                "Registration rejected — phone number already in use",
                extra={"phone_number": user_data.phone_number},
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this phone number already exists.",
            )

        # 3. Hash password and build model
        hashed_pw = hash_password(user_data.password)
        user_dict = user_data.model_dump(exclude={"password"})
        user_dict["password_hash"] = hashed_pw
        new_user = User(**user_dict)

        # 4. Persist
        created_user = await self.repo.create_user(new_user)
        logger.info(
            "User registered successfully",
            extra={
                "user_id": str(created_user.id),
                "email": created_user.email,
                "phone_number": created_user.phone_number,
            },
        )
        return created_user





    """read"""
    async def get_user_by_id(self, user_id: uuid.UUID) -> User:
        logger.debug("Fetching user by ID", extra={"user_id": str(user_id)})
        user = await self.repo.get_user_by_id(user_id)
        if not user:
            logger.warning(
                "User lookup failed — not found",
                extra={"user_id": str(user_id)},
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )
        logger.debug(
            "User fetched successfully",
            extra={"user_id": str(user_id), "email": user.email},
        )
        return user

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        logger.debug(
            "Fetching paginated user list",
            extra={"skip": skip, "limit": limit},
        )
        users = await self.repo.get_all_users(skip=skip, limit=limit)
        logger.info(
            "User list retrieved",
            extra={"count": len(users), "skip": skip, "limit": limit},
        )
        return users




    """update"""
    async def update_profile(self, user_id: uuid.UUID, update_data: UserUpdate) -> User:
        logger.debug(
            "Attempting profile update",
            extra={
                "user_id": str(user_id),
                "changed_fields": list(update_data.model_dump(exclude_unset=True).keys()),
            },
        )
        updated_user = await self.repo.update_user(user_id, update_data)
        if not updated_user:
            logger.warning(
                "Profile update failed — user not found",
                extra={"user_id": str(user_id)},
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )
        logger.info(
            "User profile updated",
            extra={
                "user_id": str(user_id),
                "changed_fields": list(update_data.model_dump(exclude_unset=True).keys()),
            },
        )
        return updated_user

    async def update_admin_status(
        self, user_id: uuid.UUID, admin_data: UserAdminUpdate
    ) -> User:
        logger.debug(
            "Attempting admin-level user update",
            extra={
                "user_id": str(user_id),
                "changed_fields": list(admin_data.model_dump(exclude_unset=True).keys()),
            },
        )
        updated_user = await self.repo.update_user_admin(user_id, admin_data)
        if not updated_user:
            logger.warning(
                "Admin update failed — user not found",
                extra={"user_id": str(user_id)},
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )
        logger.info(
            "User updated by admin",
            extra={
                "user_id": str(user_id),
                "changed_fields": list(admin_data.model_dump(exclude_unset=True).keys()),
            },
        )
        return updated_user





    """delete"""
    async def delete_user(self, user_id: uuid.UUID) -> dict:
        logger.debug(
            "Attempting user deletion", extra={"user_id": str(user_id)}
        )
        success = await self.repo.delete_user(user_id)
        if not success:
            logger.warning(
                "Deletion failed — user not found",
                extra={"user_id": str(user_id)},
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )
        logger.info(
            "User deleted successfully", extra={"user_id": str(user_id)}
        )
        return {"detail": "User successfully deleted"}