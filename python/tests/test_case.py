"""Tests for capsize_commons.text.case."""

import pytest

from capsize_commons.text import (
    slugify,
    to_kebab_case,
    to_pascal_case,
    to_snake_case,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Capsize Persona", "capsize-persona"),
        ("capsize_persona", "capsize-persona"),
        ("HTTPServer", "http-server"),
        ("already-kebab", "already-kebab"),
        ("  spaced  out  ", "spaced-out"),
        ("MixedUP_Value", "mixed-up-value"),
        ("naïve café", "naive-cafe"),
        ("", ""),
        ("!!!", ""),
    ],
)
def test_slugify(value: str, expected: str) -> None:
    assert slugify(value) == expected


def test_slugify_separator_and_case() -> None:
    assert slugify("Hello World", separator="_") == "hello_world"
    assert slugify("Hello World", lowercase=False) == "Hello-World"


def test_named_conversions() -> None:
    assert to_kebab_case("Some Value") == "some-value"
    assert to_snake_case("Some Value") == "some_value"
    assert to_pascal_case("some value") == "SomeValue"
    assert to_pascal_case("HTTPServer") == "HttpServer"
