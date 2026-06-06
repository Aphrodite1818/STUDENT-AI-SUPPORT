import asyncio
from sqlalchemy import text
from backend.app.config.database import engine
from backend.app.shared.base_model import Base

# Import models to register with Base.metadata.
# Students are omitted until the `classes` table exists (students.class_id FK).
import backend.app.tenant_management.models  # noqa: F401
import backend.app.modules.users.models  # noqa: F401
import backend.app.modules.auth.models  # noqa: F401

async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(
            text("CREATE UNIQUE INDEX IF NOT EXISTS ix_tenants_email ON tenants (email)")
        )
        await conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_otps_lookup "
                "ON otps (email, purpose, is_used, created_at DESC)"
            )
        )

if __name__ == "__main__":
    asyncio.run(create_tables())
    print("Tables created successfully.")
