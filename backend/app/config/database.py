#======================================#
#             database.py              #
#======================================#






"""THE MAIN ROLE OF THIS SCRIPT IS JUST TO SET UP A CONNECTION TO THE EXISTING DATABASE """


from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)
from sqlalchemy.orm import DeclarativeBase
from backend.app.config.settings import settings

class Base(DeclarativeBase):
    pass


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENV == "dev",  # logs SQL only in development
    pool_pre_ping=True,          # health checks connection before use
    pool_size=10,                # persistent connections kept open
    max_overflow=20              # extra connections allowed under load
)


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False       # keep objects readable after commit
)