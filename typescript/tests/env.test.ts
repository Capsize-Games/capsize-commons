import { afterEach, describe, expect, it, vi } from "vitest";

import {
  EnvError,
  readBooleanEnv,
  readEnv,
  readNumberEnv,
  readPublicEnv
} from "../src/env";

afterEach(() => {
  vi.unstubAllEnvs();
});

describe("readEnv", () => {
  it("returns the value when set", () => {
    vi.stubEnv("CAPSIZE_TEST", "value");
    expect(readEnv("CAPSIZE_TEST")).toBe("value");
  });

  it("returns the default when unset", () => {
    expect(readEnv("CAPSIZE_MISSING", { defaultValue: "fallback" })).toBe(
      "fallback"
    );
  });

  it("throws when required and unset", () => {
    expect(() => readEnv("CAPSIZE_MISSING", { required: true })).toThrow(
      EnvError
    );
  });
});

describe("readPublicEnv", () => {
  it("rejects non-VITE_ names", () => {
    expect(() => readPublicEnv("SECRET_KEY")).toThrow(EnvError);
  });

  it("allows VITE_ names", () => {
    vi.stubEnv("VITE_API_URL", "https://example.test");
    expect(readPublicEnv("VITE_API_URL")).toBe("https://example.test");
  });
});

describe("readBooleanEnv", () => {
  it.each(["0", "false", "no", "off", ""])("treats %s as false", (raw) => {
    vi.stubEnv("CAPSIZE_FLAG", raw);
    expect(readBooleanEnv("CAPSIZE_FLAG")).toBe(false);
  });

  it("treats a non-falsey value as true", () => {
    vi.stubEnv("CAPSIZE_FLAG", "1");
    expect(readBooleanEnv("CAPSIZE_FLAG")).toBe(true);
  });

  it("uses the default when unset", () => {
    expect(readBooleanEnv("CAPSIZE_MISSING", { defaultValue: true })).toBe(
      true
    );
  });
});

describe("readNumberEnv", () => {
  it("parses a number", () => {
    vi.stubEnv("CAPSIZE_PORT", "8080");
    expect(readNumberEnv("CAPSIZE_PORT")).toBe(8080);
  });

  it("throws on a non-numeric value", () => {
    vi.stubEnv("CAPSIZE_PORT", "not-a-number");
    expect(() => readNumberEnv("CAPSIZE_PORT")).toThrow(EnvError);
  });
});
