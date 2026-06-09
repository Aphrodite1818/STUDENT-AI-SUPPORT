#======================================#
#                db.py                 #
#======================================#

"""Provide database session dependencies for FastAPI routes."""

from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import AsyncSessionLocal
from app.config.logging import get_logger

logger = get_logger(__name__)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield a request-scoped async database session."""
    async with AsyncSessionLocal() as db:
        try:
            yield db
            await db.commit()
        except Exception:
            logger.warning("Database session rollback due to exception", exc_info=True)
            await db.rollback()
            raise
        finally:
            await db.close()


DbSession = Annotated[AsyncSession, Depends(get_db)] #reusable annotation
