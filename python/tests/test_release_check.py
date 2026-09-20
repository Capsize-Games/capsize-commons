"""Regression tests for the lockstep release checklist."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.release_check import validate_metadata  # noqa: E402


def test_current_release_metadata_is_consistent() -> None:
    assert validate_metadata(ROOT, version="0.1.3") == []


def test_release_check_rejects_wrong_version() -> None:
    errors = validate_metadata(ROOT, version="9.9.9")

    assert errors == [
        "Python version is 0.1.3, expected 9.9.9",
        "TypeScript version is 0.1.3, expected 9.9.9",
        "Python __version__ does not match expected 9.9.9",
        "C++ project version does not match expected 9.9.9",
    ]
