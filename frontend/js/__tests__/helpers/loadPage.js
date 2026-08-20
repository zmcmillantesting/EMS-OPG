import { JSDOM } from "jsdom";
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const JS_DIR = path.resolve(__dirname, "..", "..");

/**
 * Loads the real frontend script files into a fresh jsdom window as real
 * <script> tags (runScripts: "dangerously") - the same way the browser
 * loads them via <script src="js/...">: shared global scope, executed in
 * file order, top-level const/let/class visible across files exactly
 * like multiple classic <script> tags on one page. The shipped source
 * needs zero changes to be testable this way.
 *
 * (window.eval() called from outside the realm does NOT reliably expose
 * top-level const/let across separate calls the way real <script> tags
 * do - that was the bug behind "api is not defined".)
 *
 * beforeParse(window), if given, runs before any parsing or script
 * execution and before DOMContentLoaded fires - use it to install mocks
 * (window.fetch, etc.) that need to already be in place when a page's
 * own DOMContentLoaded handler runs, since scripts execute synchronously
 * during construction here.
 */
export function loadPage(bodyHtml, scriptFiles, { beforeParse, exposeGlobals = [] } = {}) {
    const scripts = scriptFiles
        .map((file) => `<script>${readFileSync(path.join(JS_DIR, file), "utf-8")}</script>`)
        .join("\n");

    // const/let/class declared at a script's top level are visible to a
    // bare identifier from any other <script> tag on the page (that's
    // how the app's own files find each other), but never become
    // properties of window - so tests that need `dom.window.api` from
    // outside the realm need this bridge to expose it explicitly.
    const bridge = exposeGlobals.length
        ? `<script>${exposeGlobals.map((name) => `window.${name} = ${name};`).join("\n")}</script>`
        : "";

    const html = `<!doctype html><html><body>${bodyHtml}\n${scripts}\n${bridge}</body></html>`;

    return new JSDOM(html, {
        runScripts: "dangerously",
        url: "http://localhost/",
        beforeParse,
    });
}