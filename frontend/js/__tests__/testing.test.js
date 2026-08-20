import { describe, it, expect, vi } from "vitest";
import { loadPage, fireDomContentLoaded } from "./helpers/loadPage.js";

const TESTING_BODY = `
<nav id="stage-nav"></nav>
<div id="qr-steps-placeholder" class="phase">
    <h1 id="workflow-name"></h1>
    <p id="step-indicator"></p>
    <pre id="current-command"></pre>
    <img id="qr-image">
    <button id="previous-button"></button>
    <button id="next-button"></button>
</div>
<div id="mac-placeholder" class="phase">
    <input id="mac1-input">
    <button id="mac-assign" type="button"></button>
    <button id="mac-prev" type="button"></button>
    <button id="mac-next" type="button" disabled></button>
    <div id="mac-result" class="hidden">
        <span id="mac1-value"></span><span id="mac2-value"></span><pre id="mac-command"></pre>
        <img id="mac-qr-image">
    </div>
</div>
<div id="verification-placeholder" class="phase">
    <pre id="verification-command"></pre>
    <img id="verification-qr-image">
    <input type="checkbox" id="verify-confirm">
    <span id="chip-mac1"></span><span id="chip-mac2"></span>
    <button id="verification-prev" type="button"></button>
    <button id="verification-next" type="button" disabled></button>
</div>
<div id="result-placeholder" class="phase">
    <input id="result-notes">
    <div id="result-notes-row" class="hidden"></div>
    <button id="result-pass" type="button"></button>
    <button id="result-fail" type="button"></button>
    <button id="result-fail-submit" type="button"></button>
</div>
<button id="home-button" type="button"></button>
<button id="reset-device-toggle" type="button"></button>
<div id="reset-device-panel" class="hidden">
    <pre id="reset-device-instructions"></pre>
    <div id="reset-device-steps"></div>
</div>
<span id="header-operator"></span>
`;

function loadTesting(session) {
    const dom = loadPage(TESTING_BODY, ["common.js", "api.js", "testing.js"]);

    dom.window.sessionStorage.setItem("ems-opg-session", JSON.stringify(session));

    dom.window.fetch = vi.fn(async (url) => {
        if (url === "/api/status") {
            return { ok: true, status: 200, json: async () => ({ version: "1.0.0", databaseConnected: true }) };
        }
        if (url === "/api/workflow") {
            return { ok: true, status: 200, json: async () => ({ session, step: { command: "", qr_url: null, step_name: "" } }) };
        }
        return { ok: true, status: 200, json: async () => ({}) };
    });

    return dom;
}

describe("testing.js - state to phase mapping", () => {
    it("shows the QR phase for state TESTING", async () => {
        const dom = loadTesting({ state: "TESTING", current_step: 0, operator: "4521", mac1: "", mac2: "", test_result: "" });
        fireDomContentLoaded(dom);

        await vi.waitFor(() => {
            expect(dom.window.document.getElementById("qr-steps-placeholder").classList.contains("is-active")).toBe(true);
        });
        expect(dom.window.document.getElementById("mac-placeholder").classList.contains("is-active")).toBe(false);
    });

    it("shows the MAC phase for state ASSIGNING_MAC, distinct from VERIFYING_MAC", async () => {
        const dom = loadTesting({ state: "ASSIGNING_MAC", current_step: 3, operator: "4521", mac1: "AA:BB:CC:DD:EE:00", mac2: "AA:BB:CC:DD:EE:01", test_result: "PASS" });
        fireDomContentLoaded(dom);

        await vi.waitFor(() => {
            expect(dom.window.document.getElementById("mac-placeholder").classList.contains("is-active")).toBe(true);
        });
        expect(dom.window.document.getElementById("verification-placeholder").classList.contains("is-active")).toBe(false);
    });

    it("shows the verification phase for state VERIFYING_MAC", async () => {
        const dom = loadTesting({ state: "VERIFYING_MAC", current_step: 3, operator: "4521", mac1: "AA:BB:CC:DD:EE:00", mac2: "AA:BB:CC:DD:EE:01", test_result: "PASS" });
        fireDomContentLoaded(dom);

        await vi.waitFor(() => {
            expect(dom.window.document.getElementById("verification-placeholder").classList.contains("is-active")).toBe(true);
        });
        expect(dom.window.document.getElementById("mac-placeholder").classList.contains("is-active")).toBe(false);
    });

    it("shows the result phase for state AWAITING_RESULT", async () => {
        const dom = loadTesting({ state: "AWAITING_RESULT", current_step: 3, operator: "4521", mac1: "", mac2: "", test_result: "" });
        fireDomContentLoaded(dom);

        await vi.waitFor(() => {
            expect(dom.window.document.getElementById("result-placeholder").classList.contains("is-active")).toBe(true);
        });
    });
});