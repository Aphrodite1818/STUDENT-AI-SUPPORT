#======================================#
#       core/dependencies/auth.py      #
#======================================#

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
import uuid

from backend.app.config.settings import settings
from backend.app.config.database import get_db
from backend.app.core.exceptions import UnauthorizedException, ForbiddenException
from backend.app.modules.users.models import User, AccountStatus
from backend.app.modules.users.repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise UnauthorizedException("Could not validate credentials")
            
        user_id = uuid.UUID(user_id_str)
    except (JWTError, ValueError):
        raise UnauthorizedException("Could not validate credentials")
        
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_id(user_id)
    
    if user is None:
        raise UnauthorizedException("User not found")
        
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if current_user.account_status in [AccountStatus.BANNED, AccountStatus.DEACTIVATED, AccountStatus.SUSPENDED]:
        raise ForbiddenException("Inactive account")
    return current_user
