# Release checklist

This checklist verifies a release candidate without publishing from a local
shell. Run it from a clean checkout with the intended version arguments:

```bash
just release-check python_version=0.1.2 typescript_version=0.1.1
```

The command checks package names, version authorities, and forbidden dependency
edges. For the full pre-publish gate, run:

```bash
python scripts/release_check.py \
  --python-version 0.1.2 \
  --typescript-version 0.1.1 \
  --full
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
   permissions are documented and tested in the release workflow. No token is
   printed, committed, or copied into a consumer repository.
7. Repeating an existing tag fails safely or is idempotent without overwriting
   the published artifact.
8. The release note records the tag, artifact links, checksums, clean-install
   commands, and rollback path.

The current repository can execute the metadata and boundary portions. The
tag-only trusted-publishing proof is intentionally not claimed until the
shared workflow authority and package trust configuration are restored under
`hq#23` and `hq#43`.
