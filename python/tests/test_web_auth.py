"""Tests for capsize_commons.web.auth."""

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from capsize_commons.web import check_api_key, make_api_key_dependency


def test_check_api_key_fails_closed_on_empty_expected() -> None:
    assert not check_api_key("anything", "")
    assert not check_api_key("", "")


def test_check_api_key_matches_only_equal_non_empty_keys() -> None:
    assert check_api_key("secret", "secret")
    assert not check_api_key("secret", "other")
    assert not check_api_key("", "secret")


def _client(expected: str) -> TestClient:
    app = FastAPI()
    dependency = make_api_key_dependency(lambda: expected)

    @app.get("/protected", dependencies=[Depends(dependency)])
    def protected() -> dict[str, bool]:
        return {"ok": True}

    return TestClient(app)


def test_missing_key_is_rejected() -> None:
    assert _client("secret").get("/protected").status_code == 401


def test_wrong_key_is_rejected() -> None:
    response = _client("secret").get(
        "/protected", headers={"X-API-Key": "nope"}
    )
    assert response.status_code == 401


def test_correct_key_is_accepted() -> None:
    response = _client("secret").get(
        "/protected", headers={"X-API-Key": "secret"}
    )
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_unconfigured_service_rejects_every_key() -> None:
    assert (
        _client("")
        .get("/protected", headers={"X-API-Key": "anything"})
        .status_code
        == 401
    )
