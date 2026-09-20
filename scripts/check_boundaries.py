"""Check that commons source does not import product or domain packages."""

from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_PYTHON_ROOTS = frozenset(
    {
        "airunner",
        "capsize_api",
        "capsize_auth",
        "capsize_django",
        "capsize_memory",
        "capsize_persona",
        "capsize_social",
        "social_manager",
        "spikeforge",
    }
)
FORBIDDEN_TS_PREFIXES = (
    "@capsizellc/api",
    "@capsizellc/auth",
    "@capsizellc/memory",
    "@capsizellc/persona",
    "@capsizellc/social",
    "@capsizellc/ui",
)
IMPORT_RE = re.compile(r"\b(?:from|import)\s+[\"']([^\"']+)[\"']")


def check_python_file(path: Path) -> list[str]:
    """Return forbidden import findings for one Python source file."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    findings: list[str] = []
    for node in ast.walk(tree):
        imported: str | None = None
        if isinstance(node, ast.Import):
            imported = node.names[0].name
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            imported = node.module
        imported_root = (
            imported.split(".", maxsplit=1)[0]
            if imported is not None
            else None
        )
        if imported_root in FORBIDDEN_PYTHON_ROOTS:
            findings.append(
                f"{path}:{node.lineno}: forbidden import {imported}"
            )
    return findings


def check_text_file(path: Path) -> list[str]:
    """Return forbidden package imports from a TypeScript source file."""
    findings: list[str] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    for line_number, line in enumerate(lines, 1):
        for imported in IMPORT_RE.findall(line):
            if imported.startswith(FORBIDDEN_TS_PREFIXES):
                findings.append(
                    f"{path}:{line_number}: forbidden import {imported}"
                )
    return findings


def find_violations(root: Path = ROOT) -> list[str]:
    """Scan Python and TypeScript public source trees for forbidden edges."""
    findings: list[str] = []
    for path in sorted((root / "python/src").rglob("*.py")):
        findings.extend(check_python_file(path))
    for path in sorted((root / "typescript/src").rglob("*.ts")):
        findings.extend(check_text_file(path))
    return findings


def main() -> int:
    """Print boundary findings and return a process status code."""
    findings = find_violations()
    if findings:
        print("forbidden commons dependency edges found:")
        print("\n".join(findings))
        return 1
    print("commons boundary check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
