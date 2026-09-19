import { afterEach, describe, expect, it, vi } from "vitest";

import { fetchJson, HttpError } from "../src/http/index";

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("fetchJson", () => {
  it("parses a JSON body", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () =>
        Promise.resolve(
          new Response(JSON.stringify({ id: "abc" }), { status: 200 })
        )
      )
    );
    await expect(fetchJson<{ id: string }>("/thing")).resolves.toEqual({
      id: "abc"
    });
  });

  it("throws HttpError on a non-2xx response", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => Promise.resolve(new Response("nope", { status: 500 })))
    );
    await expect(fetchJson("/thing")).rejects.toBeInstanceOf(HttpError);
  });

  it("exposes the status and body on HttpError", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => Promise.resolve(new Response("bad", { status: 422 })))
    );
    const error = await fetchJson("/thing").catch((e: unknown) => e);
    expect(error).toBeInstanceOf(HttpError);
    expect((error as HttpError).status).toBe(422);
    expect((error as HttpError).body).toBe("bad");
  });

  it("aborts when the timeout elapses", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(
        (_url: string, init?: RequestInit) =>
          new Promise((_resolve, reject) => {
            init?.signal?.addEventListener("abort", () =>
              reject(new DOMException("aborted", "AbortError"))
            );
          })
      )
    );
    await expect(fetchJson("/slow", { timeoutMs: 5 })).rejects.toThrow();
  });
});
