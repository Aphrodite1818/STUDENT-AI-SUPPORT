#======================================#
#              service.py              #
#======================================#

import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.config.security import hash_password
from backend.app.modules.users.models import User
from backend.app.modules.users.schemas import UserCreate, UserUpdate, UserAdminUpdate
from backend.app.modules.users.repository import UserRepository


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = UserRepository(session=session)

    async def register_user(self, user_data: UserCreate) -> User:
        # 1. Check if email is already taken (if provided)
        if user_data.email:
            existing_email = await self.repo.get_user_by_email(user_data.email)
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A user with this email already exists."
                )

        # 2. Check if phone number is already taken
        existing_phone = await self.repo.get_by_phone_number(user_data.phone_number)
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this phone number already exists."
            )

        # 3. Hash the password
        hashed_pw = hash_password(user_data.password)

        # 4. Create the User model instance
        user_dict = user_data.model_dump(exclude={"password"})
        user_dict["password_hash"] = hashed_pw
        
        new_user = User(**user_dict)

        # 5. Save to database via repository
        return await self.repo.create_user(new_user)

    async def get_user_by_id(self, user_id: uuid.UUID) -> User:
        user = await self.repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )
        return user

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        return await self.repo.get_all_users(skip=skip, limit=limit)

    async def update_profile(self, user_id: uuid.UUID, update_data: UserUpdate) -> User:
        updated_user = await self.repo.update_user(user_id, update_data)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )
        return updated_user

    async def update_admin_status(self, user_id: uuid.UUID, admin_data: UserAdminUpdate) -> User:
        updated_user = await self.repo.update_user_admin(user_id, admin_data)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )
        return updated_user

    async def delete_user(self, user_id: uuid.UUID) -> dict:
        success = await self.repo.delete_user(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )
        return {"detail": "User successfully deleted"}
