import asyncio

from sqlalchemy import text

from app.config.database import engine
from app.shared.base_model import Base

# Import mounted-domain models so Base.metadata knows the current table shapes.
import app.tenant_management.models  # noqa: F401
import app.modules.auth.models  # noqa: F401
import app.modules.auth_identity.models  # noqa: F401
import app.modules.superadmin.models  # noqa: F401
import app.modules.tenant_admins.models  # noqa: F401
import app.modules.subjects.models  # noqa: F401
import app.modules.classes.models  # noqa: F401
import app.modules.teachers.models  # noqa: F401
import app.modules.parents.models  # noqa: F401
import app.modules.students.models  # noqa: F401

PUBLIC_SCHEMA = "public"


async def execute(conn, statement: str) -> None:
    await conn.execute(text(statement))


async def create_index_if_columns_exist(
    conn,
    *,
    index_name: str,
    table_name: str,
    columns: list[str],
    unique: bool = False,
) -> None:
    """Create an index only when every referenced column already exists."""

    quoted_columns = ", ".join(columns)
    existence_checks = " AND ".join(
        [
            f"""
            EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = '{PUBLIC_SCHEMA}'
                  AND table_name = '{table_name}'
                  AND column_name = '{column_name}'
            )
            """
            for column_name in columns
        ]
    )
    index_kind = "UNIQUE INDEX" if unique else "INDEX"

    await execute(
        conn,
        f"""
        DO $$
        BEGIN
            IF {existence_checks} THEN
                CREATE {index_kind} IF NOT EXISTS {index_name}
                ON {PUBLIC_SCHEMA}.{table_name} ({quoted_columns});
            END IF;
        END $$;
        """,
    )


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


async def rename_enum_value_if_needed(
    conn,
    enum_name: str,
    old_label: str,
    new_label: str,
) -> None:
    await execute(
        conn,
        f"""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM pg_type t
                JOIN pg_namespace n ON n.oid = t.typnamespace
                JOIN pg_enum e ON e.enumtypid = t.oid
                WHERE n.nspname = '{PUBLIC_SCHEMA}'
                  AND t.typname = '{enum_name}'
                  AND e.enumlabel = '{old_label}'
            ) AND NOT EXISTS (
                SELECT 1
                FROM pg_type t
                JOIN pg_namespace n ON n.oid = t.typnamespace
                JOIN pg_enum e ON e.enumtypid = t.oid
                WHERE n.nspname = '{PUBLIC_SCHEMA}'
                  AND t.typname = '{enum_name}'
                  AND e.enumlabel = '{new_label}'
            ) THEN
                ALTER TYPE {PUBLIC_SCHEMA}.{enum_name}
                RENAME VALUE '{old_label}' TO '{new_label}';
            END IF;
        END $$;
        """,
    )


async def create_enum_if_missing(conn, enum_name: str, labels: list[str]) -> None:
    quoted_labels = ", ".join(f"'{label}'" for label in labels)
    await execute(
        conn,
        f"""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_type t
                JOIN pg_namespace n ON n.oid = t.typnamespace
                WHERE n.nspname = '{PUBLIC_SCHEMA}'
                  AND t.typname = '{enum_name}'
            ) THEN
                CREATE TYPE {PUBLIC_SCHEMA}.{enum_name} AS ENUM ({quoted_labels});
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
    # SQLAlchemy enums in this codebase persist enum.value, not enum member names.
    for enum_name, old_label, new_label in (
        ("tenantstatus", "ACTIVE", "active"),
        ("tenantstatus", "INACTIVE", "inactive"),
        ("tenantstatus", "SUSPENDED", "suspended"),
        ("tenantstatus", "TRIAL", "trial"),
        ("tenantstatus", "EXPIRED", "expired"),
        ("subscriptionplan", "FREE", "free"),
        ("subscriptionplan", "STARTER", "starter"),
        ("subscriptionplan", "PRO", "pro"),
        ("subscriptionplan", "ENTERPRISE", "enterprise"),
        ("tenantverificationstatus", "PENDING_VERIFICATION", "pending_verification"),
        ("tenantverificationstatus", "ACTIVE", "active"),
        ("tenantverificationstatus", "REJECTED", "rejected"),
        ("teacherstatus", "ACTIVE", "active"),
        ("teacherstatus", "INACTIVE", "inactive"),
        ("teacherstatus", "ARCHIVED", "archived"),
        ("studentgender", "MALE", "male"),
        ("studentgender", "FEMALE", "female"),
        ("academicstatus", "ACTIVE", "active"),
        ("academicstatus", "WITHDRAWN", "withdrawn"),
        ("academicstatus", "SUSPENDED", "suspended"),
        ("academicstatus", "GRADUATED", "graduated"),
        ("parentrelationship", "FATHER", "father"),
        ("parentrelationship", "MOTHER", "mother"),
        ("parentrelationship", "GUARDIAN", "guardian"),
        ("parentrelationship", "OTHER", "other"),
        ("studentprofilestatus", "INCOMPLETE", "incomplete"),
        ("studentprofilestatus", "COMPLETE", "complete"),
        ("otppurpose", "VERIFICATION", "verification"),
        ("otppurpose", "PASSWORD_RESET", "password_reset"),
        ("otppurpose", "TENANT_ACTIVATION", "tenant_activation"),
        ("otppurpose", "USER_INVITE", "user_invite"),
        ("tenant_admin_status", "PENDING", "pending"),
        ("tenant_admin_status", "ACTIVE", "active"),
        ("tenant_admin_status", "INACTIVE", "inactive"),
        ("identifier_type", "EMAIL", "email"),
        ("identifier_type", "ADMISSION_NUMBER", "admission_number"),
        ("actor_type", "TENANT_ADMIN", "tenant_admin"),
        ("actor_type", "TEACHER", "teacher"),
        ("actor_type", "STAFF", "staff"),
        ("actor_type", "PARENT", "parent"),
        ("actor_type", "STUDENT", "student"),
    ):
        await rename_enum_value_if_needed(conn, enum_name, old_label, new_label)

    await add_enum_values(
        conn,
        "tenantstatus",
        ["active", "inactive", "suspended", "trial", "expired"],
    )
    await add_enum_values(
        conn,
        "subscriptionplan",
        ["free", "starter", "pro", "enterprise"],
    )
    await add_enum_values(
        conn,
        "tenantverificationstatus",
        ["pending_verification", "active", "rejected"],
    )
    await create_enum_if_missing(
        conn,
        "teacherstatus",
        ["active", "inactive", "archived"],
    )
    await add_enum_values(
        conn,
        "teacherstatus",
        ["active", "inactive", "archived"],
    )
    await create_enum_if_missing(
        conn,
        "studentgender",
        ["male", "female"],
    )
    await add_enum_values(
        conn,
        "studentgender",
        ["male", "female"],
    )
    await create_enum_if_missing(
        conn,
        "academicstatus",
        ["active", "withdrawn", "suspended", "graduated"],
    )
    await add_enum_values(
        conn,
        "academicstatus",
        ["active", "withdrawn", "suspended", "graduated"],
    )
    await create_enum_if_missing(
        conn,
        "parentrelationship",
        ["father", "mother", "guardian", "other"],
    )
    await add_enum_values(
        conn,
        "parentrelationship",
        ["father", "mother", "guardian", "other"],
    )
    await create_enum_if_missing(
        conn,
        "studentprofilestatus",
        ["incomplete", "complete"],
    )
    await add_enum_values(
        conn,
        "studentprofilestatus",
        ["incomplete", "complete"],
    )
    await add_enum_values(
        conn,
        "otppurpose",
        ["verification", "password_reset", "tenant_activation", "user_invite"],
    )
    await create_enum_if_missing(
        conn,
        "tenant_admin_status",
        ["pending", "active", "inactive"],
    )
    await add_enum_values(
        conn,
        "tenant_admin_status",
        ["pending", "active", "inactive"],
    )
    await create_enum_if_missing(
        conn,
        "identifier_type",
        ["email", "admission_number"],
    )
    await add_enum_values(
        conn,
        "identifier_type",
        ["email", "admission_number"],
    )
    await create_enum_if_missing(
        conn,
        "actor_type",
        ["tenant_admin", "teacher", "staff", "parent", "student"],
    )
    await add_enum_values(
        conn,
        "actor_type",
        ["tenant_admin", "teacher", "staff", "parent", "student"],
    )


async def sync_tenant_columns(conn) -> None:
    await add_column(conn, "tenants", "admission_number_prefix VARCHAR(20)")
    await add_column(conn, "tenants", "school_bot_whatssap_number VARCHAR(20)")
    await add_column(conn, "tenants", "phone VARCHAR(20)")
    await add_column(conn, "tenants", "address TEXT")
    await add_column(conn, "tenants", "city VARCHAR(100)")
    await add_column(conn, "tenants", "state VARCHAR(100)")
    await add_column(conn, "tenants", "country VARCHAR(100) DEFAULT 'Nigeria'")
    await add_column(conn, "tenants", "logo_url TEXT")
    await add_column(conn, "tenants", "status public.tenantstatus DEFAULT 'trial'")
    await add_column(conn, "tenants", "plan public.subscriptionplan DEFAULT 'free'")
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
        "verification_status public.tenantverificationstatus DEFAULT 'pending_verification'",
    )

    await set_column_default(conn, "tenants", "country", "'Nigeria'")
    await set_column_default(conn, "tenants", "status", "'trial'")
    await set_column_default(conn, "tenants", "plan", "'free'")
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
        "'pending_verification'",
    )

    await execute(
        conn,
        f"CREATE UNIQUE INDEX IF NOT EXISTS ix_tenants_admission_number_prefix ON {PUBLIC_SCHEMA}.tenants (admission_number_prefix)",
    )
    await execute(
        conn,
        f"CREATE UNIQUE INDEX IF NOT EXISTS ix_tenants_school_bot_whatssap_number ON {PUBLIC_SCHEMA}.tenants (school_bot_whatssap_number)",
    )

    await backfill_nulls(conn, "tenants", "country", "'Nigeria'")
    await backfill_nulls(conn, "tenants", "status", "'trial'")
    await backfill_nulls(conn, "tenants", "plan", "'free'")
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
        "'pending_verification'",
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


async def sync_teacher_columns(conn) -> None:
    await add_column(conn, "teachers", "staff_id VARCHAR(50)")
    await add_column(conn, "teachers", "qualification VARCHAR(100)")
    await add_column(conn, "teachers", "specialization VARCHAR(150)")
    await add_column(conn, "teachers", "status public.teacherstatus DEFAULT 'active'")

    await set_column_default(conn, "teachers", "status", "'active'")
    await execute(
        conn,
        f"CREATE UNIQUE INDEX IF NOT EXISTS uq_teachers_tenant_staff_id ON {PUBLIC_SCHEMA}.teachers (tenant_id, staff_id)",
    )
    await backfill_nulls(conn, "teachers", "status", "'active'")
    await set_not_null_if_populated(conn, "teachers", "status")


async def sync_student_columns(conn) -> None:
    await add_column(conn, "students", "admission_number VARCHAR(50)")
    await add_column(conn, "students", "date_of_birth DATE")
    await add_column(conn, "students", "gender public.studentgender")
    await set_column_default(conn, "students", "admission_date", "CURRENT_DATE")
    await add_column(conn, "students", "passport_photo_url VARCHAR(500)")
    await add_column(conn, "students", "graduation_date DATE")
    await add_column(conn, "students", "class_id UUID")
    await add_column(conn, "students", "arm VARCHAR(20)")
    await add_column(conn, "students", "status public.academicstatus DEFAULT 'active'")
    await add_column(conn, "students", "profile_status public.studentprofilestatus DEFAULT 'incomplete'")
    await execute(
        conn,
        f"CREATE UNIQUE INDEX IF NOT EXISTS uq_students_tenant_admission_number ON {PUBLIC_SCHEMA}.students (tenant_id, admission_number)",
    )
    await backfill_nulls(conn, "students", "admission_date", "CURRENT_DATE")
    await set_column_default(conn, "students", "status", "'active'")
    await set_column_default(conn, "students", "profile_status", "'incomplete'")
    await backfill_nulls(conn, "students", "status", "'active'")
    await backfill_nulls(conn, "students", "profile_status", "'incomplete'")
    await set_not_null_if_populated(conn, "students", "admission_date")
    await set_not_null_if_populated(conn, "students", "status")
    await set_not_null_if_populated(conn, "students", "profile_status")
    await add_fk_if_missing(
        conn,
        table_name="students",
        constraint_name="students_class_id_fkey",
        column_name="class_id",
        referenced_table="classes",
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
        SET tenant_id = resolved.tenant_id
        FROM (
            SELECT lower(email) AS email, tenant_id
            FROM {PUBLIC_SCHEMA}.tenant_admins
            UNION ALL
            SELECT lower(email) AS email, tenant_id
            FROM {PUBLIC_SCHEMA}.teachers
            UNION ALL
            SELECT lower(email) AS email, tenant_id
            FROM {PUBLIC_SCHEMA}.parents
            UNION ALL
            SELECT lower(email) AS email, id AS tenant_id
            FROM {PUBLIC_SCHEMA}.tenants
        ) AS resolved
        WHERE auth.tenant_id IS NULL
          AND lower(auth.email) = resolved.email;
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


async def sync_tenant_admin_columns(conn) -> None:
    await add_column(conn, "tenant_admins", "email VARCHAR(300)")
    await add_column(conn, "tenant_admins", "password_hash VARCHAR(255)")
    await add_column(
        conn,
        "tenant_admins",
        "account_status public.tenant_admin_status DEFAULT 'pending'",
    )
    await add_column(conn, "tenant_admins", "is_verified BOOLEAN DEFAULT FALSE")
    await add_column(conn, "tenant_admins", "is_active BOOLEAN DEFAULT TRUE")
    await add_column(conn, "tenant_admins", "last_login_at TIMESTAMP WITH TIME ZONE")

    await set_column_default(conn, "tenant_admins", "account_status", "'pending'")
    await set_column_default(conn, "tenant_admins", "is_verified", "FALSE")
    await set_column_default(conn, "tenant_admins", "is_active", "TRUE")

    await backfill_nulls(conn, "tenant_admins", "account_status", "'pending'")
    await backfill_nulls(conn, "tenant_admins", "is_verified", "FALSE")
    await backfill_nulls(conn, "tenant_admins", "is_active", "TRUE")

    for column_name in (
        "tenant_id",
        "email",
        "password_hash",
        "account_status",
        "is_verified",
        "is_active",
        "created_at",
        "updated_at",
    ):
        await set_not_null_if_populated(conn, "tenant_admins", column_name)

    await add_fk_if_missing(
        conn,
        table_name="tenant_admins",
        constraint_name="tenant_admins_tenant_id_fkey",
        column_name="tenant_id",
        referenced_table="tenants",
    )


async def sync_auth_identity_columns(conn) -> None:
    await add_column(conn, "auth_identities", "identifier VARCHAR(255)")
    await add_column(
        conn,
        "auth_identities",
        "identifier_type public.identifier_type",
    )
    await add_column(
        conn,
        "auth_identities",
        "actor_type public.actor_type",
    )
    await add_column(conn, "auth_identities", "actor_id UUID")
    await add_column(conn, "auth_identities", "is_active BOOLEAN DEFAULT TRUE")

    await set_column_default(conn, "auth_identities", "is_active", "TRUE")
    await backfill_nulls(conn, "auth_identities", "is_active", "TRUE")

    for column_name in (
        "tenant_id",
        "identifier",
        "identifier_type",
        "actor_type",
        "actor_id",
        "is_active",
        "created_at",
        "updated_at",
    ):
        await set_not_null_if_populated(conn, "auth_identities", column_name)

    await add_fk_if_missing(
        conn,
        table_name="auth_identities",
        constraint_name="auth_identities_tenant_id_fkey",
        column_name="tenant_id",
        referenced_table="tenants",
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
    await create_index_if_columns_exist(
        conn,
        index_name="ix_teachers_tenant_email",
        table_name="teachers",
        columns=["tenant_id", "email"],
    )
    await create_index_if_columns_exist(
        conn,
        index_name="ix_teachers_tenant_staff_id",
        table_name="teachers",
        columns=["tenant_id", "staff_id"],
    )
    await execute(
        conn,
        f"CREATE INDEX IF NOT EXISTS ix_teachers_tenant_status ON {PUBLIC_SCHEMA}.teachers (tenant_id, status)",
    )
    await execute(
        conn,
        f"CREATE INDEX IF NOT EXISTS ix_classes_tenant_teacher ON {PUBLIC_SCHEMA}.classes (tenant_id, teacher_id)",
    )
    await execute(
        conn,
        f"CREATE INDEX IF NOT EXISTS ix_classes_tenant_active ON {PUBLIC_SCHEMA}.classes (tenant_id, is_active)",
    )
    await execute(
        conn,
        f"CREATE INDEX IF NOT EXISTS ix_teacher_subjects_tenant_teacher ON {PUBLIC_SCHEMA}.teacher_subjects (tenant_id, teacher_id)",
    )
    await execute(
        conn,
        f"CREATE INDEX IF NOT EXISTS ix_teacher_subjects_tenant_subject ON {PUBLIC_SCHEMA}.teacher_subjects (tenant_id, subject_id)",
    )
    await create_index_if_columns_exist(
        conn,
        index_name="ix_parents_tenant_email",
        table_name="parents",
        columns=["tenant_id", "email"],
    )
    await create_index_if_columns_exist(
        conn,
        index_name="ix_parents_tenant_account_status",
        table_name="parents",
        columns=["tenant_id", "account_status"],
    )
    await create_index_if_columns_exist(
        conn,
        index_name="ix_students_tenant_admission_number",
        table_name="students",
        columns=["tenant_id", "admission_number"],
    )
    await create_index_if_columns_exist(
        conn,
        index_name="ix_students_tenant_account_status",
        table_name="students",
        columns=["tenant_id", "account_status"],
    )
    await execute(
        conn,
        f"CREATE INDEX IF NOT EXISTS ix_students_tenant_class ON {PUBLIC_SCHEMA}.students (tenant_id, class_id)",
    )
    await execute(
        conn,
        f"CREATE INDEX IF NOT EXISTS ix_students_tenant_status ON {PUBLIC_SCHEMA}.students (tenant_id, status)",
    )
    await execute(
        conn,
        f"CREATE INDEX IF NOT EXISTS ix_student_parent_links_tenant_student ON {PUBLIC_SCHEMA}.student_parent_links (tenant_id, student_id)",
    )
    await execute(
        conn,
        f"CREATE INDEX IF NOT EXISTS ix_student_parent_links_tenant_parent ON {PUBLIC_SCHEMA}.student_parent_links (tenant_id, parent_id)",
    )
    await execute(
        conn,
        f"CREATE INDEX IF NOT EXISTS ix_student_link_codes_tenant_student ON {PUBLIC_SCHEMA}.student_link_codes (tenant_id, student_id)",
    )
    await execute(
        conn,
        f"CREATE INDEX IF NOT EXISTS ix_student_link_codes_tenant_code ON {PUBLIC_SCHEMA}.student_link_codes (tenant_id, code)",
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
        f"CREATE INDEX IF NOT EXISTS ix_tenant_admins_email ON {PUBLIC_SCHEMA}.tenant_admins (email)",
    )
    await execute(
        conn,
        f"CREATE INDEX IF NOT EXISTS ix_tenant_admins_tenant_email ON {PUBLIC_SCHEMA}.tenant_admins (tenant_id, email)",
    )
    await execute(
        conn,
        f"CREATE INDEX IF NOT EXISTS ix_auth_identities_actor ON {PUBLIC_SCHEMA}.auth_identities (actor_type, actor_id)",
    )
    await execute(
        conn,
        f"CREATE INDEX IF NOT EXISTS ix_auth_identities_active_identifier ON {PUBLIC_SCHEMA}.auth_identities (identifier_type, identifier, is_active)",
    )
    await execute(
        conn,
        f"CREATE UNIQUE INDEX IF NOT EXISTS ix_auth_identities_identifier_unique ON {PUBLIC_SCHEMA}.auth_identities (identifier_type, identifier)",
    )
    await execute(
        conn,
        f"CREATE UNIQUE INDEX IF NOT EXISTS ix_auth_identities_actor_unique ON {PUBLIC_SCHEMA}.auth_identities (actor_type, actor_id)",
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
        await sync_teacher_columns(conn)
        await sync_student_columns(conn)
        await sync_auth_columns(conn)
        await sync_tenant_admin_columns(conn)
        await sync_auth_identity_columns(conn)
        await sync_indexes(conn)


if __name__ == "__main__":
    asyncio.run(create_tables())
    print("Tables created successfully.")
