/**
 * `@capsize/commons` — selectively importable common utilities.
 *
 * Prefer the subpath exports (`@capsize/commons/result`, …) so a bundle only
 * includes the modules it uses; this barrel exists for convenience.
 */

export * from "./result";
export * from "./env";
export * from "./logging/index";
export * from "./http/index";
export * from "./string/index";
export * from "./object/index";
