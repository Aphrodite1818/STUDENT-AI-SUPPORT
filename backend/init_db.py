import asyncio

from sqlalchemy import text

from app.config.database import engine
from app.shared.base_model import Base

# Import mounted-domain models so Base.metadata knows the current table shapes.
# Students are still omitted because students.class_id references public.classes,
# and the current backend does not define/register that table yet.
import app.tenant_management.models  # noqa: F401
import app.modules.users.models  # noqa: F401
import app.modules.auth.models  # noqa: F401
import app.modules.superadmin.models  # noqa: F401

PUBLIC_SCHEMA = "public"


async def execute(conn, statement: str) -> None:
    await conn.execute(text(statement))


async def add_enum_values(conn, enum_name: str, labels: list[str]) -> None:
    for label in labels:
        await execute(
            conn,
            f"""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1
                    FROM pg_type t
                    JOIN pg_namespace n ON n.oid = t.typnamespace
                    WHERE n.nspname = '{PUBLIC_SCHEMA}'
                      AND t.typname = '{enum_name}'
                ) AND NOT EXISTS (
                    SELECT 1
                    FROM pg_enum e
                    JOIN pg_type t ON t.oid = e.enumtypid
                    JOIN pg_namespace n ON n.oid = t.typnamespace
                    WHERE n.nspname = '{PUBLIC_SCHEMA}'
                      AND t.typname = '{enum_name}'
                      AND e.enumlabel = '{label}'
                ) THEN
                    ALTER TYPE {PUBLIC_SCHEMA}.{enum_name} ADD VALUE '{label}';
                END IF;
            END $$;
            """,
        )


async def add_column(conn, table_name: str, column_sql: str) -> None:
    await execute(
        conn,
        f"ALTER TABLE {PUBLIC_SCHEMA}.{table_name} ADD COLUMN IF NOT EXISTS {column_sql}",
    )


async def rename_column_if_exists(
    conn,
    table_name: str,
    old_column_name: str,
    new_column_name: str,
) -> None:
    await execute(
        conn,
        f"""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = '{PUBLIC_SCHEMA}'
                  AND table_name = '{table_name}'
                  AND column_name = '{old_column_name}'
            ) AND NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = '{PUBLIC_SCHEMA}'
                  AND table_name = '{table_name}'
                  AND column_name = '{new_column_name}'
            ) THEN
                ALTER TABLE {PUBLIC_SCHEMA}.{table_name}
                RENAME COLUMN {old_column_name} TO {new_column_name};
            END IF;
        END $$;
        """,
    )


async def set_column_default(
    conn,
    table_name: str,
    column_name: str,
    default_sql: str,
) -> None:
    await execute(
        conn,
        f"""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = '{PUBLIC_SCHEMA}'
                  AND table_name = '{table_name}'
                  AND column_name = '{column_name}'
            ) THEN
                ALTER TABLE {PUBLIC_SCHEMA}.{table_name}
                ALTER COLUMN {column_name} SET DEFAULT {default_sql};
            END IF;
        END $$;
        """,
    )


async def backfill_nulls(
    conn,
    table_name: str,
    column_name: str,
    value_sql: str,
) -> None:
    await execute(
        conn,
        f"""
        UPDATE {PUBLIC_SCHEMA}.{table_name}
        SET {column_name} = {value_sql}
        WHERE {column_name} IS NULL;
        """,
    )


async def set_not_null_if_populated(conn, table_name: str, column_name: str) -> None:
    await execute(
        conn,
        f"""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = '{PUBLIC_SCHEMA}'
                  AND table_name = '{table_name}'
                  AND column_name = '{column_name}'
                  AND is_nullable = 'YES'
            ) AND NOT EXISTS (
                SELECT 1
                FROM {PUBLIC_SCHEMA}.{table_name}
                WHERE {column_name} IS NULL
            ) THEN
                ALTER TABLE {PUBLIC_SCHEMA}.{table_name}
                ALTER COLUMN {column_name} SET NOT NULL;
            END IF;
        END $$;
        """,
    )


async def add_fk_if_missing(
    conn,
    table_name: str,
    constraint_name: str,
    column_name: str,
    referenced_table: str,
    referenced_column: str = "id",
) -> None:
    await execute(
        conn,
        f"""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = '{PUBLIC_SCHEMA}'
                  AND table_name = '{table_name}'
                  AND column_name = '{column_name}'
            ) AND NOT EXISTS (
                SELECT 1
                FROM pg_constraint
                WHERE conname = '{constraint_name}'
            ) THEN
                ALTER TABLE {PUBLIC_SCHEMA}.{table_name}
                ADD CONSTRAINT {constraint_name}
                FOREIGN KEY ({column_name})
                REFERENCES {PUBLIC_SCHEMA}.{referenced_table} ({referenced_column});
            END IF;
        END $$;
        """,
    )


async def run_legacy_migrations(conn) -> None:
    await execute(conn, f"CREATE SCHEMA IF NOT EXISTS {PUBLIC_SCHEMA}")

    await execute(
        conn,
        f"""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = '{PUBLIC_SCHEMA}'
                  AND table_name = 'otps'
            ) AND NOT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = '{PUBLIC_SCHEMA}'
                  AND table_name = 'auth'
            ) THEN
                ALTER TABLE {PUBLIC_SCHEMA}.otps RENAME TO auth;
            END IF;
        END $$;
        """,
    )

    await execute(
        conn,
        f"""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = '{PUBLIC_SCHEMA}'
                  AND table_name = 'auth'
                  AND column_name = 'hashed_code'
            ) AND NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = '{PUBLIC_SCHEMA}'
                  AND table_name = 'auth'
                  AND column_name = 'hashed_value'
            ) THEN
                ALTER TABLE {PUBLIC_SCHEMA}.auth
                RENAME COLUMN hashed_code TO hashed_value;
            END IF;
        END $$;
        """,
    )

    await execute(
        conn,
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_type WHERE typname = 'otppurpose'
            ) AND NOT EXISTS (
                SELECT 1
                FROM pg_type t
                JOIN pg_namespace n ON n.oid = t.typnamespace
                WHERE n.nspname = 'public'
                  AND t.typname = 'otppurpose'
            ) THEN
                ALTER TYPE otppurpose SET SCHEMA public;
            END IF;
        END $$;
        """,
    )


async def sync_enum_values(conn) -> None:
    # SQLAlchemy Enum persists Python enum member names by default.
    await add_enum_values(
        conn,
        "tenantstatus",
        ["ACTIVE", "INACTIVE", "SUSPENDED", "TRIAL", "EXPIRED"],
    )
    await add_enum_values(
        conn,
        "subscriptionplan",
        ["FREE", "STARTER", "PRO", "ENTERPRISE"],
    )
    await add_enum_values(
        conn,
        "tenantverificationstatus",
        ["PENDING_VERIFICATION", "ACTIVE", "REJECTED"],
    )
    await add_enum_values(
        conn,
        "userrole",
        ["TEACHER", "STUDENT", "ADMIN", "PARENT"],
    )
    await add_enum_values(
        conn,
        "accountstatus",
        ["ACTIVE", "BANNED", "SUSPENDED", "DEACTIVATED", "PENDING"],
    )
    await add_enum_values(
        conn,
        "otppurpose",
        ["VERIFICATION", "PASSWORD_RESET", "TENANT_ACTIVATION", "USER_INVITE"],
    )


async def sync_tenant_columns(conn) -> None:
    await add_column(conn, "tenants", "school_bot_whatssap_number VARCHAR(20)")
    await add_column(conn, "tenants", "phone VARCHAR(20)")
    await add_column(conn, "tenants", "address TEXT")
    await add_column(conn, "tenants", "city VARCHAR(100)")
    await add_column(conn, "tenants", "state VARCHAR(100)")
    await add_column(conn, "tenants", "country VARCHAR(100) DEFAULT 'Nigeria'")
    await add_column(conn, "tenants", "logo_url TEXT")
    await add_column(conn, "tenants", "status public.tenantstatus DEFAULT 'TRIAL'")
    await add_column(conn, "tenants", "plan public.subscriptionplan DEFAULT 'FREE'")
    await add_column(conn, "tenants", "trial_ends_at TIMESTAMP WITH TIME ZONE")
    await add_column(conn, "tenants", "subscription_ends_at TIMESTAMP WITH TIME ZONE")
    await add_column(conn, "tenants", "is_deleted BOOLEAN DEFAULT FALSE")
    await add_column(conn, "tenants", "deleted_at TIMESTAMP WITH TIME ZONE")
    await add_column(conn, "tenants", "max_students INTEGER DEFAULT 500")
    await add_column(conn, "tenants", "max_teachers INTEGER DEFAULT 50")
    await add_column(conn, "tenants", "feature_flags JSONB DEFAULT '{}'::jsonb")
    await add_column(conn, "tenants", "timezone VARCHAR(50) DEFAULT 'Africa/Lagos'")
    await add_column(conn, "tenants", "language VARCHAR(10) DEFAULT 'en'")
    await add_column(conn, "tenants", "onboarding_completed BOOLEAN DEFAULT FALSE")
    await add_column(conn, "tenants", "branches VARCHAR[]")
    await add_column(
        conn,
        "tenants",
        "verification_status public.tenantverificationstatus DEFAULT 'PENDING_VERIFICATION'",
    )

    await set_column_default(conn, "tenants", "country", "'Nigeria'")
    await set_column_default(conn, "tenants", "status", "'TRIAL'")
    await set_column_default(conn, "tenants", "plan", "'FREE'")
    await set_column_default(conn, "tenants", "is_deleted", "FALSE")
    await set_column_default(conn, "tenants", "max_students", "500")
    await set_column_default(conn, "tenants", "max_teachers", "50")
    await set_column_default(conn, "tenants", "feature_flags", "'{}'::jsonb")
    await set_column_default(conn, "tenants", "timezone", "'Africa/Lagos'")
    await set_column_default(conn, "tenants", "language", "'en'")
    await set_column_default(conn, "tenants", "onboarding_completed", "FALSE")
    await set_column_default(
        conn,
        "tenants",
        "verification_status",
        "'PENDING_VERIFICATION'",
    )

    await backfill_nulls(conn, "tenants", "country", "'Nigeria'")
    await backfill_nulls(conn, "tenants", "status", "'TRIAL'")
    await backfill_nulls(conn, "tenants", "plan", "'FREE'")
    await backfill_nulls(conn, "tenants", "is_deleted", "FALSE")
    await backfill_nulls(conn, "tenants", "max_students", "500")
    await backfill_nulls(conn, "tenants", "max_teachers", "50")
    await backfill_nulls(conn, "tenants", "feature_flags", "'{}'::jsonb")
    await backfill_nulls(conn, "tenants", "timezone", "'Africa/Lagos'")
    await backfill_nulls(conn, "tenants", "language", "'en'")
    await backfill_nulls(conn, "tenants", "onboarding_completed", "FALSE")
    await backfill_nulls(
        conn,
        "tenants",
        "verification_status",
        "'PENDING_VERIFICATION'",
    )

    for column_name in (
        "school_name",
        "slug",
        "email",
        "country",
        "status",
        "plan",
        "is_deleted",
        "max_students",
        "max_teachers",
        "timezone",
        "language",
        "onboarding_completed",
        "verification_status",
        "created_at",
        "updated_at",
    ):
        await set_not_null_if_populated(conn, "tenants", column_name)


async def sync_user_columns(conn) -> None:
    await add_column(conn, "users", "firstname VARCHAR(100)")
    await add_column(conn, "users", "lastname VARCHAR(100)")
    await add_column(conn, "users", "phone_number VARCHAR(20)")
    await add_column(conn, "users", "whatsapp_id VARCHAR(100)")
    await add_column(conn, "users", "is_verified BOOLEAN DEFAULT TRUE")

    await set_column_default(conn, "users", "is_verified", "TRUE")

    await execute(
        conn,
        f"""
        UPDATE {PUBLIC_SCHEMA}.users
        SET is_verified = CASE
            WHEN account_status = 'PENDING' THEN FALSE
            ELSE TRUE
        END
        WHERE is_verified IS NULL;
        """,
    )

    for column_name in (
        "tenant_id",
        "email",
        "password_hash",
        "account_status",
        "role",
        "is_verified",
        "created_at",
        "updated_at",
    ):
        await set_not_null_if_populated(conn, "users", column_name)

    await add_fk_if_missing(
        conn,
        table_name="users",
        constraint_name="users_tenant_id_fkey",
        column_name="tenant_id",
        referenced_table="tenants",
    )


async def sync_auth_columns(conn) -> None:
    await add_column(conn, "auth", "email VARCHAR(100)")
    await add_column(conn, "auth", "hashed_value VARCHAR(255)")
    await add_column(conn, "auth", "purpose public.otppurpose")
    await add_column(conn, "auth", "expires_at TIMESTAMP WITH TIME ZONE")
    await add_column(conn, "auth", "is_used BOOLEAN DEFAULT FALSE")
    await add_column(conn, "auth", "tenant_id UUID")

    await set_column_default(conn, "auth", "is_used", "FALSE")

    await execute(
        conn,
        f"""
        UPDATE {PUBLIC_SCHEMA}.auth AS auth
        SET tenant_id = users.tenant_id
        FROM {PUBLIC_SCHEMA}.users AS users
        WHERE auth.tenant_id IS NULL
          AND auth.email = users.email;
        """,
    )
    await backfill_nulls(conn, "auth", "is_used", "FALSE")

    for column_name in (
        "tenant_id",
        "email",
        "hashed_value",
        "purpose",
        "expires_at",
        "is_used",
        "created_at",
        "updated_at",
    ):
        await set_not_null_if_populated(conn, "auth", column_name)

    await add_fk_if_missing(
        conn,
        table_name="auth",
        constraint_name="auth_tenant_id_fkey",
        column_name="tenant_id",
        referenced_table="tenants",
    )


async def migrate_legacy_superadmins(conn) -> None:
    await rename_column_if_exists(
        conn,
        "superadmin_invites",
        "superadmin_id",
        "invited_by_superadmin_id",
    )

    # Only activated legacy superadmins belong in public.superadmins.
    # Pending legacy invitees must be re-invited under the new invite-only flow.
    await execute(
        conn,
        f"""
        INSERT INTO {PUBLIC_SCHEMA}.superadmins (
            id,
            email,
            password_hash,
            is_active,
            last_login_at,
            created_at,
            updated_at
        )
        SELECT
            users.id,
            users.email,
            users.password_hash,
            CASE WHEN users.account_status = 'ACTIVE' THEN TRUE ELSE FALSE END,
            NULL,
            users.created_at,
            users.updated_at
        FROM {PUBLIC_SCHEMA}.users AS users
        WHERE users.role::text = 'SUPERADMIN'
          AND users.account_status = 'ACTIVE'
          AND NOT EXISTS (
              SELECT 1
              FROM {PUBLIC_SCHEMA}.superadmins AS superadmins
              WHERE lower(superadmins.email) = lower(users.email)
          );
        """,
    )

    await execute(
        conn,
        f"""
        DELETE FROM {PUBLIC_SCHEMA}.auth
        WHERE purpose = 'USER_INVITE'
          AND EXISTS (
              SELECT 1
              FROM {PUBLIC_SCHEMA}.users AS users
              WHERE users.role::text = 'SUPERADMIN'
                AND lower(users.email) = lower({PUBLIC_SCHEMA}.auth.email)
          );
        """,
    )

    await execute(
        conn,
        f"DELETE FROM {PUBLIC_SCHEMA}.users WHERE role::text = 'SUPERADMIN'",
    )


async def sync_indexes(conn) -> None:
    await execute(
        conn,
        f"CREATE UNIQUE INDEX IF NOT EXISTS ix_tenants_slug ON {PUBLIC_SCHEMA}.tenants (slug)",
    )
    await execute(
        conn,
        f"CREATE UNIQUE INDEX IF NOT EXISTS ix_tenants_email ON {PUBLIC_SCHEMA}.tenants (email)",
    )
    await execute(
        conn,
        f"CREATE INDEX IF NOT EXISTS ix_tenants_is_deleted ON {PUBLIC_SCHEMA}.tenants (is_deleted)",
    )
    await execute(
        conn,
        f"CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON {PUBLIC_SCHEMA}.users (email)",
    )
    await execute(
        conn,
        f"CREATE UNIQUE INDEX IF NOT EXISTS ix_users_phone_number ON {PUBLIC_SCHEMA}.users (phone_number)",
    )
    await execute(
        conn,
        f"CREATE UNIQUE INDEX IF NOT EXISTS ix_users_whatsapp_id ON {PUBLIC_SCHEMA}.users (whatsapp_id)",
    )
    await execute(
        conn,
        f"CREATE INDEX IF NOT EXISTS ix_users_tenant_phone ON {PUBLIC_SCHEMA}.users (tenant_id, phone_number)",
    )
    await execute(
        conn,
        f"CREATE INDEX IF NOT EXISTS ix_users_tenant_role ON {PUBLIC_SCHEMA}.users (tenant_id, role)",
    )

    await execute(
        conn,
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM pg_indexes
                WHERE schemaname = 'public'
                  AND indexname = 'ix_otps_lookup'
            ) AND NOT EXISTS (
                SELECT 1
                FROM pg_indexes
                WHERE schemaname = 'public'
                  AND indexname = 'ix_auth_lookup'
            ) THEN
                ALTER INDEX public.ix_otps_lookup RENAME TO ix_auth_lookup;
            END IF;
        END $$;
        """,
    )
    await execute(
        conn,
        f"""
        CREATE INDEX IF NOT EXISTS ix_auth_lookup
        ON {PUBLIC_SCHEMA}.auth (email, purpose, is_used, created_at DESC)
        """,
    )
    await execute(
        conn,
        f"CREATE UNIQUE INDEX IF NOT EXISTS ix_superadmins_email ON {PUBLIC_SCHEMA}.superadmins (email)",
    )
    await execute(
        conn,
        f"CREATE INDEX IF NOT EXISTS ix_superadmins_last_login_at ON {PUBLIC_SCHEMA}.superadmins (last_login_at)",
    )
    await execute(
        conn,
        f"CREATE INDEX IF NOT EXISTS ix_superadmin_invites_email ON {PUBLIC_SCHEMA}.superadmin_invites (email)",
    )
    await execute(
        conn,
        f"CREATE INDEX IF NOT EXISTS ix_superadmin_invites_invited_by_superadmin_id ON {PUBLIC_SCHEMA}.superadmin_invites (invited_by_superadmin_id)",
    )


async def create_tables() -> None:
    async with engine.begin() as conn:
        await run_legacy_migrations(conn)
        await sync_enum_values(conn)

        await conn.run_sync(Base.metadata.create_all)

        await sync_enum_values(conn)
        await sync_tenant_columns(conn)
        await sync_user_columns(conn)
        await sync_auth_columns(conn)
        await migrate_legacy_superadmins(conn)
        await sync_indexes(conn)


if __name__ == "__main__":
    asyncio.run(create_tables())
    print("Tables created successfully.")
