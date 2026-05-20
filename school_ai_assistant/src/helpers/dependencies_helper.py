#==========================#
# DEPENDENCIES_HELPER SCRIPT
#==========================#
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    from ..db.engine import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        yield session
