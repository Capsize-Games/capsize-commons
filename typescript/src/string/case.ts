/**
 * Case conversion implementing the fleet's naming rules (§3.1).
 *
 * Mirrors the Python `capsize_commons.text.case` so a value normalized on one
 * side of the wire matches the other.
 */

const SEPARATORS = /[^0-9A-Za-z]+/g;
const CAMEL_BOUNDARY = /(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])/g;
const COMBINING_MARKS = /[\u0300-\u036f]/g;

function toAscii(value: string): string {
  return value.normalize("NFKD").replace(COMBINING_MARKS, "");
}

function words(value: string): string[] {
  return toAscii(value)
    .trim()
    .replace(CAMEL_BOUNDARY, " ")
    .split(SEPARATORS)
    .filter((word) => word.length > 0);
}

export interface SlugifyOptions {
  /** Joins words; defaults to `"-"`. */
  separator?: string;
  /** Lowercases the result; defaults to `true`. */
  lowercase?: boolean;
}

/** Join the words of `value` with `separator`. */
export function slugify(value: string, options: SlugifyOptions = {}): string {
  const separator = options.separator ?? "-";
  const lowercase = options.lowercase ?? true;
  const parts = words(value);
  const normalized = lowercase
    ? parts.map((word) => word.toLowerCase())
    : parts;
  return normalized.join(separator);
}

/** Return `value` as `kebab-case` (the repo/file convention). */
export function toKebabCase(value: string): string {
  return slugify(value, { separator: "-" });
}

/** Return `value` as `snake_case` (the symbol convention). */
export function toSnakeCase(value: string): string {
  return slugify(value, { separator: "_" });
}

/** Return `value` as `PascalCase` (the class convention). */
export function toPascalCase(value: string): string {
  return words(value)
    .map((word) => {
      const lower = word.toLowerCase();
      return lower.charAt(0).toUpperCase() + lower.slice(1);
    })
    .join("");
}
