import { defineConfig } from "vitest/config";

export default defineConfig({
  // tests/e2e son de Playwright, no de Vitest.
  test: { include: ["tests/unit/**/*.test.{ts,tsx}"] },
});
