"""Pytest bootstrap for shared fixtures."""

pytest_plugins = [
    "tests.fixtures.database",
    "tests.fixtures.auth",
    "tests.fixtures.tenants",
    "tests.fixtures.users",
    "tests.fixtures.teachers",
    "tests.fixtures.subjects",
]