# Release checklist

This checklist verifies a release candidate without publishing from a local
shell. Run it from a clean checkout with the intended version arguments:

```bash
just release-check version=0.1.3
```

The command checks package names, version authorities, and forbidden dependency
edges. For the full pre-publish gate, run:

```bash
python scripts/release_check.py --version 0.1.3 --full
```

The full gate must record:

1. `just ci` passes: Python, TypeScript, C++ tests, lint, and type checks.
2. `just build` produces the Python wheel/sdist, TypeScript bundle, and C++
   build artifacts.
3. Each artifact's name, version, supported runtime, and checksum match the
   manifest and package metadata.
4. A clean-install smoke test imports the Python package and each published
   TypeScript subpath; C++ tests run from the built target.
5. The release tag is the only publish trigger. Pull requests and ordinary
   branch pushes must not publish.
6. Trusted-publisher identities, package-owner permissions, and required OIDC
   permissions are configured for PyPI and npm, and the tag workflow reaches
   both publish jobs. No token is printed, committed, or copied into a
   consumer repository.
7. Repeating an existing tag fails safely or is idempotent without overwriting
   the published artifact.
8. The release note records the tag, artifact links, checksums, clean-install
   commands, and rollback path.

The release workflow is tag-only for publishing. A manual dispatch is a
dry-run and never publishes. The package trust configuration must be verified
before pushing the first release tag.
