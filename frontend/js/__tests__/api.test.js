import { describe, it, expect, vi, beforeEach } from "vitest";
import { loadPage } from "./helpers/loadPage.js";

function loadApi() {
    return loadPage("", ["common.js", "api.js"], {
        exposeGlobals: ["api", "mockAPI"]
    });
}

function mockFetch(body = { session: { state: "TESTING" }, step: null }) {
    return vi.fn(async () => ({
        ok: true,
        status: 200,
        json: async () => body,
    }));
}

describe("api - live endpoint contract", () => {
    let dom;

    beforeEach(() => {
        dom = loadApi();
        dom.window.fetch = mockFetch();
    });

    it("assignMac1 PUTs /api/workflow/mac-assign with mac1 only", async () => {
        await dom.window.api.assignMac1("00:11:22:33:44:55");

        const [url, config] = dom.window.fetch.mock.calls[0];
        expect(url).toBe("/api/workflow/mac-assign");
        expect(config.method).toBe("PUT");
        expect(JSON.parse(config.body)).toEqual({ mac1: "00:11:22:33:44:55" });
    });

    it("confirmMacAssignment POSTs /api/workflow/mac-confirm", async () => {
        await dom.window.api.confirmMacAssignment();

        const [url, config] = dom.window.fetch.mock.calls[0];
        expect(url).toBe("/api/workflow/mac-confirm");
        expect(config.method).toBe("POST");
    });

    it("confirmVerification POSTs /api/workflow/verify-confirm", async () => {
        await dom.window.api.confirmVerification();

        const [url, config] = dom.window.fetch.mock.calls[0];
        expect(url).toBe("/api/workflow/verify-confirm");
        expect(config.method).toBe("POST");
    });

    it("finishSession POSTs /api/session/finish with no body", async () => {
        await dom.window.api.finishSession();

        const [url, config] = dom.window.fetch.mock.calls[0];
        expect(url).toBe("/api/session/finish");
        expect(config.method).toBe("POST");
        expect(config.body).toBeUndefined();
    });

    it("getOrders GETs /api/orders", async () => {
        dom.window.fetch = mockFetch({ orders: [] });
        await dom.window.api.getOrders();

        const [url] = dom.window.fetch.mock.calls[0];
        expect(url).toBe("/api/orders");
    });

    it("createOrder POSTs /api/orders with order_number and quantity", async () => {
        await dom.window.api.createOrder({ order_number: "12345.6", quantity: 10 });

        const [url, config] = dom.window.fetch.mock.calls[0];
        expect(url).toBe("/api/orders");
        expect(config.method).toBe("POST");
        expect(JSON.parse(config.body)).toEqual({ order_number: "12345.6", quantity: 10 });
    });

    it("startSession forwards operator, order_number, and serial_number", async () => {
        await dom.window.api.startSession({
            operator: "4521", order_number: "12345.6", serial_number: "EM20260001",
        });

        const [url, config] = dom.window.fetch.mock.calls[0];
        expect(url).toBe("/api/session/start");
        expect(JSON.parse(config.body)).toEqual({
            operator: "4521", order_number: "12345.6", serial_number: "EM20260001",
        });
    });

    it("does not expose the removed pre-redesign methods", () => {
        expect(dom.window.api.setMacAddresses).toBeUndefined();
        expect(dom.window.api.provisionOrder).toBeUndefined();
        expect(dom.window.api.getOpenOrders).toBeUndefined();
    });

    it("exposes every method testing.js and home.js actually call", () => {
        for (const method of [
            "assignMac1", "confirmMacAssignment", "confirmVerification",
            "finishSession", "getOrders", "createOrder", "startSession",
            "getWorkflow", "nextStep", "previousStep", "setTestResult",
            "deleteOrder", "correctOrder",
        ]) {
            expect(typeof dom.window.api[method]).toBe("function");
        }
    });
});