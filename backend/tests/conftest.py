"""Pytest bootstrap for shared fixtures."""

# Keep plugin registration explicit so CI loads the shared fixtures in a stable order.
pytest_plugins = [
    "tests.fixtures.database",
    "tests.fixtures.auth",
    "tests.fixtures.tenants",
    "tests.fixtures.users",
    "tests.fixtures.teachers",
    "tests.fixtures.subjects",
]
