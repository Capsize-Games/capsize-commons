import { defineConfig } from "tsup";

// One entry per public subpath export so a consumer importing only
// `@capsize/commons/result` never pulls in the HTTP or logging code.
export default defineConfig({
  entry: [
    "src/index.ts",
    "src/result.ts",
    "src/env.ts",
    "src/logging/index.ts",
    "src/http/index.ts",
    "src/string/index.ts",
    "src/object/index.ts"
  ],
  format: ["esm", "cjs"],
  dts: true,
  clean: true,
  sourcemap: true,
  treeshake: true,
  target: "es2022"
});
