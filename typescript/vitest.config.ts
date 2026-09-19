import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    include: ["tests/**/*.test.ts"],
    environment: "node",
    coverage: {
      provider: "v8",
      reporter: ["text", "lcov"],
      thresholds: {
        // §9: 80% coverage for `library` projects.
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80
      }
    }
  }
});
