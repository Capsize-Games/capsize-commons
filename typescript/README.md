# @capsize/commons (TypeScript / JavaScript)

The TypeScript distribution of [`capsize-commons`](../README.md). It is
tree-shakeable, marked `sideEffects: false`, and exposes one subpath export per
module so a consumer imports only what it uses.

## Install

```bash
pnpm add @capsize/commons
```

## Subpath exports

| Import                     | Provides                                                      |
| -------------------------- | ------------------------------------------------------------- |
| `@capsize/commons/result`  | `Result<T, E>`, `ok`, `err`, `unwrap`, `mapResult`, …         |
| `@capsize/commons/env`     | Typed environment access with a `VITE_` guard for client code |
| `@capsize/commons/logging` | `createLogger` emitting the §14 JSON line shape               |
| `@capsize/commons/http`    | `fetchJson<T>` with timeout and `HttpError`                   |
| `@capsize/commons/string`  | `slugify`, `toKebabCase`, `toSnakeCase`, `toPascalCase`       |
| `@capsize/commons/object`  | `deepMerge`, `deepFreeze`, `isPlainObject`                    |
| `@capsize/commons`         | Everything above, re-exported                                 |

```ts
import { createLogger } from "@capsize/commons/logging";
import { fetchJson } from "@capsize/commons/http";
import { ok, unwrap } from "@capsize/commons/result";

const log = createLogger({ name: "web", json: true });
log.info("starting", { region: "us-west" });

const data = await fetchJson<{ id: string }>("/api/v1/thing", {
  timeoutMs: 5_000
});
```

## Development

```bash
cd typescript
pnpm install
pnpm test
pnpm typecheck && pnpm lint
pnpm build
```

Or from the repository root: `just test`, `just lint`, `just typecheck`.
