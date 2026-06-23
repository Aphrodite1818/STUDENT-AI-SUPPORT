from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient

from app import main as main_module


def _build_app(is_development: bool):
    stub_settings = SimpleNamespace(
        ALLOWED_ORIGINS=["http://localhost:5173"],
        is_development=is_development,
    )

    with patch.object(main_module, "settings", stub_settings), patch.object(
        main_module,
        "import_model_modules",
        new=lambda: None,
    ):
        return main_module.create_app()


def test_docs_routes_are_enabled_in_development():
    client = TestClient(_build_app(is_development=True))

    assert client.get("/docs").status_code == 200
    assert client.get("/redoc").status_code == 200
    assert client.get("/openapi.json").status_code == 200


def test_docs_routes_are_disabled_outside_development():
    client = TestClient(_build_app(is_development=False))

    assert client.get("/docs").status_code == 404
    assert client.get("/redoc").status_code == 404
    assert client.get("/openapi.json").status_code == 404
