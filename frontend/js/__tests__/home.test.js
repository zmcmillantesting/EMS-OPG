import { describe, it, expect, vi } from "vitest";
import { loadPage } from "./helpers/loadPage.js";

const HOME_BODY = `
<form id="start-test-form">
    <input id="operator-input">
    <select id="order-select"><option value="">— Select an order —</option></select>
    <button id="new-order-toggle" type="button"></button>
    <button id="edit-order-button" type="button" class="hidden"></button>
    <button id="delete-order-button" type="button" class="hidden"></button>
    <div id="new-order-panel" class="hidden">
        <input id="new-order-number-input">
        <input id="new-order-quantity-input" type="number">
        <button id="new-order-create" type="button"></button>
    </div>
    <input id="serial-input">
    <button id="start-test" type="submit"></button>
</form>
<span id="home-devices-count"></span>
<span id="home-version"></span>
<span id="home-database-status"></span>
`;

function jsonResponse(body) {
    return { ok: true, status: 200, json: async () => body, text: async () => JSON.stringify(body) };
}

function loadHome({ orders = [] } = {}) {
    const fetchMock = vi.fn(async (url) => {
        if (url === "/api/status") {
            return jsonResponse({ version: "1.0.0", databaseConnected: true, devicesToday: 3 });
        }
        if (url === "/api/orders") {
            return jsonResponse({ orders });
        }
        // header.html/footer.html component fetches, or anything else.
        return { ok: true, status: 200, text: async () => "", json: async () => ({}) };
    });

    const dom = loadPage(HOME_BODY, ["common.js", "api.js", "home.js"], {
        beforeParse(window) {
            window.fetch = fetchMock;
        },
    });

    return dom;
}

async function afterOrdersLoaded(dom, expectedOptionCount) {
    await vi.waitFor(() => {
        expect(dom.window.document.querySelectorAll("#order-select option").length).toBe(expectedOptionCount);
    });
}

describe("home.js", () => {
    it("populates the order dropdown with passed/quantity from GET /api/orders", async () => {
        const dom = loadHome({
            orders: [{ order_number: "12345.6", quantity: 10, passed: 3, remaining: 7 }],
        });

        await afterOrdersLoaded(dom, 2);

        const option = dom.window.document.querySelector('#order-select option[value="12345.6"]');
        expect(option.textContent).toContain("3/10 passed");
    });

    it("rejects an invalid serial number without calling startSession", async () => {
        const dom = loadHome({ orders: [{ order_number: "12345.6", quantity: 10, passed: 0, remaining: 10 }] });
        await afterOrdersLoaded(dom, 2);

        dom.window.document.getElementById("operator-input").value = "4521";
        dom.window.document.getElementById("order-select").value = "12345.6";
        dom.window.document.getElementById("serial-input").value = "not-a-serial";
        dom.window.alert = vi.fn();

        dom.window.document.getElementById("start-test-form")
            .dispatchEvent(new dom.window.Event("submit", { bubbles: true, cancelable: true }));

        await vi.waitFor(() => expect(dom.window.alert).toHaveBeenCalledWith(expect.stringContaining("EMyyww0000")));

        const startCalls = dom.window.fetch.mock.calls.filter(([url]) => url === "/api/session/start");
        expect(startCalls).toHaveLength(0);
    });

    it("starts a session with operator, order, and serial when the form is valid", async () => {
        const dom = loadHome({ orders: [{ order_number: "12345.6", quantity: 10, passed: 0, remaining: 10 }] });
        await afterOrdersLoaded(dom, 2);

        // navigateTo() would otherwise set window.location.href, which
        // jsdom logs as "Not implemented: navigation" - stub it, since
        // this test only cares that startSession was called correctly.
        dom.window.navigateTo = vi.fn();

        dom.window.document.getElementById("operator-input").value = "4521";
        dom.window.document.getElementById("order-select").value = "12345.6";
        dom.window.document.getElementById("serial-input").value = "EM20260001";

        dom.window.document.getElementById("start-test-form")
            .dispatchEvent(new dom.window.Event("submit", { bubbles: true, cancelable: true }));

        await vi.waitFor(() => {
            const calls = dom.window.fetch.mock.calls.filter(([url]) => url === "/api/session/start");
            expect(calls).toHaveLength(1);
        });

        const [, config] = dom.window.fetch.mock.calls.find(([url]) => url === "/api/session/start");
        expect(JSON.parse(config.body)).toEqual({
            order_number: "12345.6", operator: "4521", serial_number: "EM20260001",
        });
    });

    it("rejects a malformed new-order number without POSTing /api/orders", async () => {
        const dom = loadHome({ orders: [] });
        await afterOrdersLoaded(dom, 1);

        dom.window.document.getElementById("new-order-number-input").value = "not-an-order-number";
        dom.window.document.getElementById("new-order-quantity-input").value = "10";
        dom.window.alert = vi.fn();

        dom.window.document.getElementById("new-order-create").click();

        await vi.waitFor(() => expect(dom.window.alert).toHaveBeenCalled());

        const postCalls = dom.window.fetch.mock.calls.filter(
            ([url, config]) => url === "/api/orders" && config?.method === "POST"
        );
        expect(postCalls).toHaveLength(0);
    });
});