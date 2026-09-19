import { describe, expect, it } from "vitest";

import {
  err,
  isErr,
  isOk,
  mapResult,
  ok,
  toResult,
  toResultAsync,
  unwrap,
  unwrapOr
} from "../src/result";

describe("Result", () => {
  it("constructs and narrows both branches", () => {
    const success = ok(1);
    const failure = err("bad");
    expect(isOk(success)).toBe(true);
    expect(isErr(success)).toBe(false);
    expect(isErr(failure)).toBe(true);
    expect(isOk(failure)).toBe(false);
  });

  it("unwrap returns the value or throws the error", () => {
    expect(unwrap(ok("v"))).toBe("v");
    expect(() => unwrap(err(new Error("boom")))).toThrow("boom");
  });

  it("unwrap wraps non-Error failures", () => {
    expect(() => unwrap(err("plain"))).toThrow("plain");
  });

  it("unwrapOr falls back on error", () => {
    expect(unwrapOr(ok(2), 9)).toBe(2);
    expect(unwrapOr(err("x"), 9)).toBe(9);
  });

  it("mapResult transforms only the success value", () => {
    expect(
      unwrapOr(
        mapResult(ok(2), (n) => n * 3),
        0
      )
    ).toBe(6);
    expect(isErr(mapResult(err("x"), (n: number) => n * 3))).toBe(true);
  });

  it("toResult captures thrown values", () => {
    expect(isOk(toResult(() => 1))).toBe(true);
    const captured = toResult(() => {
      throw new Error("nope");
    });
    expect(isErr(captured)).toBe(true);
  });

  it("toResultAsync captures rejections", async () => {
    await expect(
      toResultAsync(async () => 5).then((r) => unwrap(r))
    ).resolves.toBe(5);
    const rejected = await toResultAsync(async () => {
      throw new Error("async nope");
    });
    expect(isErr(rejected)).toBe(true);
  });
});
