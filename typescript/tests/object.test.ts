import { describe, expect, it } from "vitest";

import { deepFreeze, deepMerge, isPlainObject } from "../src/object/index";

describe("isPlainObject", () => {
  it("rejects null and arrays", () => {
    expect(isPlainObject(null)).toBe(false);
    expect(isPlainObject([])).toBe(false);
    expect(isPlainObject({})).toBe(true);
  });
});

describe("deepMerge", () => {
  it("merges nested objects, later sources winning", () => {
    const merged = deepMerge(
      { a: 1, nested: { x: 1, y: 2 } },
      { b: 2, nested: { y: 3 } }
    );
    expect(merged).toEqual({ a: 1, b: 2, nested: { x: 1, y: 3 } });
  });

  it("replaces arrays instead of merging them", () => {
    const merged = deepMerge({ list: [1, 2] }, { list: [3] });
    expect(merged).toEqual({ list: [3] });
  });
});

describe("deepFreeze", () => {
  it("freezes nested objects", () => {
    const value = deepFreeze({ nested: { x: 1 } });
    expect(Object.isFrozen(value)).toBe(true);
    expect(Object.isFrozen(value.nested)).toBe(true);
  });
});
