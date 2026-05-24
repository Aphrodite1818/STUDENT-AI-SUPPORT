#======================================#
#                db.py                 #
#======================================#

"""
Bridges the database session factory into FastAPI's dependency injection system.
Provides a per-request AsyncSession that automatically commits on success
and rolls back on failure — consumed by route handlers via DbSession.
"""

from typing import AsyncGenerator, Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.config.database import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as db:
        try:
            yield db
            await db.commit()
        except Exception:
            await db.rollback()
            raise
        finally:
            await db.close()


# reusable type alias for all your routers
DbSession = Annotated[AsyncSession, Depends(get_db)]