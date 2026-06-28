#======================================#
#             database.py              #
#======================================#






"""Configure the application's async database engine and session factory."""


import logging

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.config.logging import is_development, resolve_log_level
from app.config.settings import settings

database_url = settings.DATABASE_URL
if not database_url:
    raise ValueError("DATABASE_URL must be set for the active environment.")

engine = create_async_engine(
    database_url,
    echo=is_development() or resolve_log_level() <= logging.DEBUG,
    pool_pre_ping=True,          # health checks connection before use
    pool_size=10,                # persistent connections kept open
    max_overflow=20,             # extra connections allowed under load
    # Required when DATABASE_URL points at PgBouncer (transaction/statement pool mode).
    # asyncpg caches prepared statements per connection; PgBouncer reassigns backend
    # connections across clients, causing "__asyncpg_stmt_*__ already exists" errors.
    connect_args={"statement_cache_size": 0},
)


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False       # keep objects readable after commit
)








