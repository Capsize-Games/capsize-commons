# @capsizellc/commons (TypeScript / JavaScript)

The TypeScript distribution of [`capsize-commons`](../README.md). It is
tree-shakeable, marked `sideEffects: false`, and exposes one subpath export per
module so a consumer imports only what it uses.

## Install

```bash
pnpm add @capsizellc/commons
```

## Subpath exports

| Import                        | Provides                                                      |
| ----------------------------- | ------------------------------------------------------------- |
| `@capsizellc/commons/result`  | `Result<T, E>`, `ok`, `err`, `unwrap`, `mapResult`, …         |
| `@capsizellc/commons/env`     | Typed environment access with a `VITE_` guard for client code |
| `@capsizellc/commons/logging` | `createLogger` emitting the §14 JSON line shape               |
| `@capsizellc/commons/http`    | `fetchJson<T>` with timeout and `HttpError`                   |
| `@capsizellc/commons/string`  | `slugify`, `toKebabCase`, `toSnakeCase`, `toPascalCase`       |
| `@capsizellc/commons/object`  | `deepMerge`, `deepFreeze`, `isPlainObject`                    |
| `@capsizellc/commons`         | Everything above, re-exported                                 |

```ts
import { createLogger } from "@capsizellc/commons/logging";
import { fetchJson } from "@capsizellc/commons/http";
import { ok, unwrap } from "@capsizellc/commons/result";

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
