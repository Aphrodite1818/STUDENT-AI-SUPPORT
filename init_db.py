import asyncio
from backend.app.config.database import engine
from backend.app.shared.base_model import Base

# Import models to register with Base.metadata.
# Students are omitted until the `classes` table exists (students.class_id FK).
import backend.app.tenant_management.models  # noqa: F401
import backend.app.modules.users.models  # noqa: F401
import backend.app.modules.auth.models  # noqa: F401

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(create_tables())
    print("Tables created successfully.")
