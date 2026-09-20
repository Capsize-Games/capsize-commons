"""Validate release metadata and boundaries without publishing artifacts."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.check_boundaries import find_violations  # noqa: E402


def validate_metadata(
    root: Path, *, python_version: str, typescript_version: str
) -> list[str]:
    """Return metadata errors for the two published package surfaces."""
    errors: list[str] = []
    python_manifest = root / "python/pyproject.toml"
    python_data = tomllib.loads(python_manifest.read_text(encoding="utf-8"))
    python_project = python_data["project"]
    if python_project["name"] != "capsize-commons":
        errors.append("python package name is not capsize-commons")
    if python_project["version"] != python_version:
        errors.append(
            "Python version is "
            f"{python_project['version']}, expected {python_version}"
        )

    ts_manifest = root / "typescript/package.json"
    ts_data = json.loads(ts_manifest.read_text(encoding="utf-8"))
    if ts_data["name"] != "@capsizellc/commons":
        errors.append("TypeScript package name is not @capsizellc/commons")
    if ts_data["version"] != typescript_version:
        errors.append(
            "TypeScript version is "
            f"{ts_data['version']}, expected {typescript_version}"
        )
    errors.extend(find_violations(root))
    return errors


def parse_args() -> argparse.Namespace:
    """Parse release-check command-line options."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python-version", required=True)
    parser.add_argument("--typescript-version", required=True)
    parser.add_argument(
        "--full",
        action="store_true",
        help=(
            "run the repository's complete just ci suite after metadata checks"
        ),
    )
    return parser.parse_args()


def main() -> int:
    """Run the metadata and optional full release checks."""
    args = parse_args()
    errors = validate_metadata(
        ROOT,
        python_version=args.python_version,
        typescript_version=args.typescript_version,
    )
    if errors:
        print("release metadata check failed:")
        print("\n".join(errors))
        return 1
    print(
        "release metadata and commons boundaries passed "
        f"(Python {args.python_version}, TypeScript {args.typescript_version})"
    )
    if args.full:
        subprocess.run(["just", "ci"], cwd=ROOT, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
