import { describe, expect, it } from "vitest";

import { createLogger } from "../src/logging/index";

function collector(): { lines: string[]; sink: (line: string) => void } {
  const lines: string[] = [];
  return { lines, sink: (line) => lines.push(line) };
}

describe("createLogger", () => {
  it("emits the §14 JSON shape", () => {
    const { lines, sink } = collector();
    createLogger({ name: "svc", json: true, sink }).info("hello", {
      attempt: 2
    });
    const payload = JSON.parse(lines[0] ?? "{}");
    expect(payload.level).toBe("INFO");
    expect(payload.logger).toBe("svc");
    expect(payload.message).toBe("hello");
    expect(payload.fields).toEqual({ attempt: 2 });
    expect(payload.timestamp).toMatch(/^\d{4}-\d{2}-\d{2}T/);
  });

  it("nests caller fields so they cannot overwrite base fields", () => {
    const { lines, sink } = collector();
    createLogger({ name: "svc", json: true, sink }).info("m", {
      level: "HACKED"
    });
    const payload = JSON.parse(lines[0] ?? "{}");
    expect(payload.level).toBe("INFO");
    expect(payload.fields).toEqual({ level: "HACKED" });
  });

  it("filters below the configured level", () => {
    const { lines, sink } = collector();
    const logger = createLogger({ name: "svc", level: "warn", sink });
    logger.debug("d");
    logger.info("i");
    logger.warn("w");
    expect(lines).toHaveLength(1);
    expect(lines[0]).toContain("w");
  });

  it("child loggers extend the name", () => {
    const { lines, sink } = collector();
    const child = createLogger({ name: "svc", json: true, sink }).child("db");
    child.info("connected");
    expect(JSON.parse(lines[0] ?? "{}").logger).toBe("svc.db");
  });

  it("renders a human line when json is false", () => {
    const { lines, sink } = collector();
    createLogger({ name: "svc", sink }).info("plain");
    expect(lines[0]).toContain("INFO svc plain");
  });
});
