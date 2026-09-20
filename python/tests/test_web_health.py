"""Tests for capsize_commons.web.health."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from capsize_commons.web import install_health_routes


def test_health_reports_ok() -> None:
    app = FastAPI()
    install_health_routes(app)
    assert TestClient(app).get("/health").json() == {"status": "ok"}


def test_health_preserves_a_service_body() -> None:
    app = FastAPI()
    install_health_routes(app, health_body={"ok": True})
    assert TestClient(app).get("/health").json() == {"ok": True}


def test_ready_without_predicate_is_ready() -> None:
    app = FastAPI()
    install_health_routes(app)
    response = TestClient(app).get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_ready_preserves_a_service_body() -> None:
    app = FastAPI()
    install_health_routes(app, ready_body={"ready": True})
    assert TestClient(app).get("/ready").json() == {"ready": True}


def test_ready_predicate_false_returns_503() -> None:
    app = FastAPI()
    install_health_routes(app, ready_check=lambda: False)
    assert TestClient(app).get("/ready").status_code == 503


def test_ready_predicate_true_returns_200() -> None:
    app = FastAPI()
    install_health_routes(app, ready_check=lambda: True)
    assert TestClient(app).get("/ready").status_code == 200
