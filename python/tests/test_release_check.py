"""Regression tests for the metadata-only release checklist."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.release_check import validate_metadata  # noqa: E402


def test_current_release_metadata_is_consistent() -> None:
    assert (
        validate_metadata(
            ROOT, python_version="0.1.2", typescript_version="0.1.1"
        )
        == []
    )


def test_release_check_rejects_wrong_version() -> None:
    errors = validate_metadata(
        ROOT, python_version="9.9.9", typescript_version="0.1.1"
    )

    assert errors == ["Python version is 0.1.2, expected 9.9.9"]
