/**
 * Recursive object helpers.
 *
 * `deepMerge` merges plain objects recursively and **replaces** arrays and
 * class instances rather than merging them — merging arrays element-wise is a
 * common source of surprising config, so this refuses to guess.
 */

export type PlainObject = Record<string, unknown>;

/** Return `true` for a non-null, non-array object. */
export function isPlainObject(value: unknown): value is PlainObject {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

/** Recursively merge plain objects, later sources winning. */
export function deepMerge<T extends PlainObject>(...sources: PlainObject[]): T {
  const target: PlainObject = {};
  for (const source of sources) {
    for (const [key, value] of Object.entries(source)) {
      const existing = target[key];
      target[key] =
        isPlainObject(existing) && isPlainObject(value)
          ? deepMerge(existing, value)
          : value;
    }
  }
  return target as T;
}

/** Recursively freeze `value` and everything reachable from it. */
export function deepFreeze<T>(value: T): Readonly<T> {
  if (typeof value === "object" && value !== null) {
    for (const key of Object.keys(value)) {
      deepFreeze((value as PlainObject)[key]);
    }
    Object.freeze(value);
  }
  return value;
}
