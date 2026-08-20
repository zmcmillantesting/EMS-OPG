import { JSDOM } from "jsdom";
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const JS_DIR = path.resolve(__dirname, "..", "..");

/**
 * Loads the real frontend script files into a fresh jsdom window, the
 * same way the browser does via <script src="js/...">: shared global
 * scope, executed in file order, no ES module transform - so the actual
 * shipped source needs zero changes to be testable.
 *
 * Scripts don't auto-run on construction (runScripts: "outside-only") -
 * call fireDomContentLoaded() once mocks (fetch, etc.) are wired up, so
 * the app's own DOMContentLoaded handlers run at a controlled time.
 */
export function loadPage(bodyHtml, scriptFiles) {
    const dom = new JSDOM(`<!doctype html><html><body>${bodyHtml}</body></html>`, {
        runScripts: "outside-only",
        url: "http://localhost/",
    });

    for (const file of scriptFiles) {
        const code = readFileSync(path.join(JS_DIR, file), "utf-8");
        dom.window.eval(code);
    }

    return dom;
}

export function fireDomContentLoaded(dom) {
    dom.window.document.dispatchEvent(
        new dom.window.Event("DOMContentLoaded", { bubbles: true, cancelable: true })
    );
}