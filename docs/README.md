# capsize-commons documentation

| Document | Contents |
|---|---|
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Repository layout, module map, design rules |
| [`ADOPTION_PLAN.md`](ADOPTION_PLAN.md) | Audit of the fleet + phased plan for adopting commons |
| [`adr/`](adr/) | Architecture Decision Records |

## Guides

- **Using the Python package** — see [`../python/README.md`](../python/README.md).
- **Using the TypeScript package** — see [`../typescript/README.md`](../typescript/README.md).
- **Using the C++ library** — see [`../cpp/README.md`](../cpp/README.md).

## Contributing a primitive

1. Confirm it is generic (no domain nouns) and duplicated somewhere in the
   fleet; note the projects it is meant to replace in the ADR or PR.
2. Add it to **every** language where an equivalent need exists, or record why
   it is language-specific.
3. Export it from the language's public surface only (`__all__`, barrel,
   `namespace capsize::commons`).
4. Add tests in the same change.
5. Run `just ci` and `just sync-rules`.
