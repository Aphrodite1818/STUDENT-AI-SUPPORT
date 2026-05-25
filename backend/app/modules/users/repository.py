#======================================#
#          user repository.py          #
#======================================#


import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from backend.app.core.dependencies.db import DbSession
from backend.app.modules.users.models import User
from backend.app.modules.users.schemas import UserAdminUpdate, UserUpdate


class UserRepository:
    def __init__(self, session : AsyncSession):
        self.session = session


    async def create_user(self , user : User) -> User:
        self.session.add(user)
        await self.session.flush() 
        return user
    

    async def get_user_by_id(self , user_id : uuid.UUID) ->User | None:
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self , email : str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    


    async def get_by_phone_number(self , phone_number : str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.phone_number == phone_number)
        )
        return result.scalar_one_or_none()
    



    async def update_user_admin(self, user_id: uuid.UUID, user_data: UserAdminUpdate) -> User | None:
        current_user = select(User).where(User.id == user_id)
        result = await self.session.execute(current_user)
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            return None
            
        update_dict = user_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(db_user, key, value)
            
        self.session.add(db_user)
        return db_user
    




    async def update_user(self, user_id: uuid.UUID, user_data: UserUpdate) -> User | None:
        current_user = select(User).where(User.id == user_id)
        result = await self.session.execute(current_user)
        db_user = result.scalar_one_or_none()


        if not db_user:
            return None
        
        update_dict = user_data.model_dump(exclude_unset=True) #exclude_unset returns only what was changed
        for key, value in update_dict.items():
            setattr(db_user, key, value)

        self.session.add(db_user)
        return db_user
    



    async def get_all_users(self , skip : int = 0 , limit : int = 100) -> list[User]:
        result = await self.session.execute(
            select(User).offset(skip).limit(limit)
        )
        return result.scalars().all()
    


    async def delete_user(self , user_id : uuid.UUID) -> bool:
        current_user = select(User).where(User.id == user_id)
        result = await self.session.execute(current_user)
        db_user = result.scalar_one_or_none()

        if not db_user:
            return False
        
        await self.session.delete(db_user)
        return True