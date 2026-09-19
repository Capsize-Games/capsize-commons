import { describe, expect, it } from "vitest";

import {
  slugify,
  toKebabCase,
  toPascalCase,
  toSnakeCase
} from "../src/string/index";

describe("slugify", () => {
  it.each([
    ["Capsize Persona", "capsize-persona"],
    ["capsize_persona", "capsize-persona"],
    ["HTTPServer", "http-server"],
    ["  spaced  out  ", "spaced-out"],
    ["MixedUP_Value", "mixed-up-value"],
    ["naïve café", "naive-cafe"],
    ["!!!", ""]
  ])("slugifies %s", (input, expected) => {
    expect(slugify(input)).toBe(expected);
  });

  it("honours separator and case options", () => {
    expect(slugify("Hello World", { separator: "_" })).toBe("hello_world");
    expect(slugify("Hello World", { lowercase: false })).toBe("Hello-World");
  });
});

describe("named conversions", () => {
  it("produces the documented casings", () => {
    expect(toKebabCase("Some Value")).toBe("some-value");
    expect(toSnakeCase("Some Value")).toBe("some_value");
    expect(toPascalCase("some value")).toBe("SomeValue");
    expect(toPascalCase("HTTPServer")).toBe("HttpServer");
  });
});
