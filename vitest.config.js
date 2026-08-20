import { defineConfig } from "vitest/config";

export default defineConfig({
    test: {
        // Tests build their own jsdom window per test file (see
        // frontend/js/__tests__/helpers/loadPage.js) rather than using
        // Vitest's shared jsdom environment - the frontend files declare
        // top-level `let`/`var` and rely on classic-script semantics, so
        // re-running them in one shared global scope would throw on
        // redeclaration between tests.
        environment: "node",
        include: ["frontend/js/__tests__/**/*.test.js"],
    },
});