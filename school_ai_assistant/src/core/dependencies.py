#==========================#
# FAST API DEPENDENCIES    #
#==========================#


from typing import AsyncGenerator
from ..db.engine import AsyncSessionLocal


async def get_db() -> AsyncGenerator:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()