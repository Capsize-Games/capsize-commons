"""Regression tests for the commons dependency boundary check."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.check_boundaries import (  # noqa: E402
    check_python_file,
    find_violations,
)


def test_current_source_has_no_forbidden_edges() -> None:
    assert find_violations(ROOT) == []


def test_forbidden_python_edge_is_reported(tmp_path: Path) -> None:
    source = tmp_path / "bad.py"
    source.write_text(
        "from capsize_persona import Persona\n", encoding="utf-8"
    )

    findings = check_python_file(source)

    assert "forbidden import capsize_persona" in findings[0]
