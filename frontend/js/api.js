/**
 * API communication layer for EMS-OPG frontend.
 * Falls back to local mock data when the Python server is unavailable.
 */

const API_BASE = "/api";

const WORKFLOW_STEPS = [
    { name: "username", commandKey: "step1" },
    { name: "password", commandKey: "step2" },
    { name: "multi-step", commandKey: "step3" },
    { name: "emd -i sysfs -c 4", commandKey: "step4" },
    { name: "MAC Addresses", commandKey: "step5" },
    { name: "Verify MAC Addresses", commandKey: "step6" },
];

const QR_COMMANDS = {
    step1: "root",
    step2: "default",
    step3: "ls /dev/sd[a-e]; timeout 2s loopback /dev/port0[2-4] -q; timeout 2s loopback /dev/port0[5-8] -q;  emd -i sysfs -c 4; ifconfig eth1 up && sleep 5 && ethtool eth1",
    step4: "emd -i sysfs -c 4",
    step5: "setfset -u ethaddr={mac1} && setfset -u eth1addr={mac2}",
    step6: "setfset | grep eth0 && setfset | grep eth1",
};

const MOCK_HISTORY = [
    {
        id: 1,
        timestamp: "2026-08-01T14:22:00Z",
        order_number: "123456",
        serial_number: "SN001",
        ethaddr_id: "00:60:47:12:34:01",
        eth1addr_id: "00:60:47:12:34:02",
        operator: "Zach",
        test_result: "PASS",
        used: true,
    },
    {
        id: 2,
        timestamp: "2026-08-02T09:15:00Z",
        order_number: "123457",
        serial_number: "SN002",
        ethaddr_id: "00:60:47:12:34:03",
        eth1addr_id: "00:60:47:12:34:04",
        operator: "Vanessa",
        test_result: "PASS",
        used: true,
    },
    {
        id: 3,
        timestamp: "2026-08-03T16:40:00Z",
        order_number: "123456",
        serial_number: "SN003",
        ethaddr_id: "00:60:47:12:34:05",
        eth1addr_id: "00:60:47:12:34:06",
        operator: "Zach",
        test_result: "FAIL",
        used: false,
    },
];

let mockSession = null;
let useMock = false;

class ApiUnreachableError extends Error {}

async function request(path, options = {}) {
    const config = {
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {}),
        },
        ...options,
    };

    let response;

    try {
        response = await fetch(`${API_BASE}${path}`, config);
    } catch (error) {
        throw new ApiUnreachableError(error.message);
    }

    if (!response.ok) {
        let message = `API error: ${response.status}`;
        try {
            const body = await response.json()
            if (body && body.error) {
                message = body.error;
            }
        } catch {

        }
        throw new Error(message);
    }

    if (response.status === 204) {
        return null;
    }

    return response.json();
}

function formatCommand(commandKey, session) {
    let command = QR_COMMANDS[commandKey] || "";

    if (session) {
        command = command
            .replace("{mac1}", session.mac1 || "")
            .replace("{mac2}", session.mac2 || "");
    }

    return command;
}

function buildStepPayload(session) {
    const stepIndex = session.current_step;
    const step = WORKFLOW_STEPS[stepIndex];
    const command = formatCommand(step.commandKey, session);

    return {
        workflow_name: "Functional Test",
        step_index: stepIndex,
        step_number: stepIndex + 1,
        total_steps: WORKFLOW_STEPS.length,
        step_name: step.name,
        command,
        qr_url: buildQrUrl(command),
    };
}

function buildQrUrl(command) {
    const qr = qrcode(0, "L");
    qr.addData(command || "");
    qr.make();
    return qr.createDataURL(8, 16)
}

function filterHistory(query) {
    const normalized = query.trim().toLowerCase();
    if (!normalized) {
        return [...MOCK_HISTORY];
    }

    return MOCK_HISTORY.filter((record) => {
        const haystack = [
            record.order_number,
            record.serial_number,
            record.ethaddr_id,
            record.eth1addr_id,
            record.operator,
            record.test_result,
        ]
            .join(" ")
            .toLowerCase();

        return haystack.includes(normalized);
    });
}

function findDeviceBySerial(serial) {
    return MOCK_HISTORY.find(
        (record) => record.serial_number.toLowerCase() === serial.toLowerCase()
    );
}

function findDeviceByMac(mac) {
    const normalized = mac.toLowerCase();
    return MOCK_HISTORY.find(
        (record) =>
            record.ethaddr_id.toLowerCase() === normalized ||
            record.eth1addr_id.toLowerCase() === normalized
    );
}

const mockApi = {
    getStatus() {
        return Promise.resolve({
            version: "1.0.0",
            databaseConnected: true,
            workflowReady: true,
            devicesToday: MOCK_HISTORY.length,
        });
    },

    startSession(payload) {
        mockSession = {
            operator: payload.operator || "",
            order_number: payload.order_number || "",
            serial_number: payload.serial_number || "",
            mac1: payload.mac1 || "",
            mac2: payload.mac2 || "",
            current_step: 0,
            total_steps: WORKFLOW_STEPS.length,
            completed: false,
            cancelled: false,
        };

        return Promise.resolve({
            session: { ...mockSession },
            step: buildStepPayload(mockSession),
        });
    },

    setMacAddresses(mac1, mac2) {
        if (!mockSession) {
            return Promise.reject(new Error("No active session"));
        }
        
        mockSession.mac1 = mac1
        mockSession.mac2 = mac2

        return Promise.resolve({
            session: { ...mockSession },
        step: buildStepPayload(mockSession),
         });
    },

    setTestResult(result, notes) {
        if (!mockSession) {
            return Promise.reject(new Error("No active session"));
        }
        if (!mockSession.completed) {
            return Promise.reject(new Error("Complete all test steps before recording a result"));
        }
        if (result === "FAIL" && !notes) {
            return Promise.reject(new Error("Notes are required when recording a failed test"));
        }

        mockSession.test_result = result;
        mockSession.test_notes = notes || "";

        return Promise.resolve({
            session: { ...mockSession },
            step: buildStepPayload(mockSession),
        });
    },



    finishSession(serialNumber) {
        if (!mockSession) {
            return Promise.reject(new Error("No active session"));
        }

        mockSession.serial_number = serialNumber;

        return Promise.resolve({
            session: { ...mockSession },
            message: "Device saved to trace log",
            serial_number: serialNumber,
        });
    },

    getWorkflow() {
        const session = mockSession || loadSession();
        if (!session) {
            return Promise.reject(new Error("No active session"));
        }

        mockSession = session;
        return Promise.resolve({
            session: { ...session },
            step: buildStepPayload(session),
        });
    },

    nextStep() {
        if (!mockSession) {
            return Promise.reject(new Error("No active session"));
        }

        if (mockSession.current_step < WORKFLOW_STEPS.length - 1) {
            mockSession.current_step += 1;
        } else {
            mockSession.completed = true;
        }

        return Promise.resolve({
            session: { ...mockSession },
            step: buildStepPayload(mockSession),
        });
    },

    previousStep() {
        if (!mockSession) {
            return Promise.reject(new Error("No active session"));
        }

        if (mockSession.completed) {
            mockSession.completed = false;
        } else if (mockSession.current_step > 0) {
            mockSession.current_step -= 1;
        }

        return Promise.resolve({
            session: { ...mockSession },
            step: buildStepPayload(mockSession),
        });
    },

    cancelSession() {
        if (mockSession) {
            mockSession.cancelled = true;
        }

        return Promise.resolve({ success: true });
    },

    getHistory(query = "") {
        return Promise.resolve({
            records: filterHistory(query),
        });
    },

    exportHistory() {
        const records = filterHistory("");
        const headers = [
            "Date",
            "Order",
            "Serial",
            "MAC1",
            "MAC2",
            "Operator",
            "Result",
            "Status",
        ];

        const rows = records.map((record) => [
            record.timestamp,
            record.order_number,
            record.serial_number,
            record.ethaddr_id,
            record.eth1addr_id || "",
            record.operator,
            record.test_result,
            record.used ? "Used" : "Available",
        ]);

        const csv = [headers, ...rows]
            .map((row) => row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(","))
            .join("\n");

        return Promise.resolve({ csv, filename: "ems-opg-history.csv" });
    },

    lookupDevice(serial) {
        const device = findDeviceBySerial(serial);
        if (!device) {
            return Promise.reject(new Error("Device not found"));
        }

        return Promise.resolve({ device });
    },

    lookupMac(mac) {
        const device = findDeviceByMac(mac);
        if (!device) {
            return Promise.reject(new Error("Device not found"));
        }

        return Promise.resolve({ device });
    },

    updateDevice(serial, updates) {
        const device = findDeviceBySerial(serial);
        if (!device) {
            return Promise.reject(new Error("Device not found"));
        }

        Object.assign(device, {
            order_number: updates.order_number ?? device.order_number,
            serial_number: updates.serial_number ?? device.serial_number,
            operator: updates.operator ?? device.operator,
            ethaddr_id: updates.mac1 ?? device.ethaddr_id,
            eth1addr_id: updates.mac2 ?? device.eth1addr_id,
        });

        return Promise.resolve({ device, message: "Device updated successfully." });
    },

    resetMac(serial, reason) {
        const device = findDeviceBySerial(serial);
        if (!device) {
            return Promise.reject(new Error("Device not found"));
        }
        if (!reason) {
            return Promise.reject(new Error("A reason is required to reset a MAC address."));
        }

        device.used = false;
        return Promise.resolve({ device, message: "MAC reset successfully." });
    },

    getMacPool() {
        const records = MOCK_HISTORY.map((record) => ({
            mac_address: record.ethaddr_id,
            used: record.used,
            order_number: record.used ? record.order_number : null,
            serial_number: record.used ? record.serial_number : null,
        }));
        return Promise.resolve({ records });
    },

    getResetDeviceSteps() {
        return Promise.resolve({
            instructions:
                "RESET INSTRUCTIONS\n\n" +
                "1. Press and hold the erase button\n\n" +
                "2. With button pressed, apply power\n\n" +
                "3. Once text is seen press any arrow key to cancel the boot " +
                "(only a few seconds to do so)\n\n" +
                "4. scan the following barcodes",
            steps: [
                { command: "set do_factory_setup 1", qr_url: buildQrUrl("set do_factory_setup 1") },
                { command: "saveenv", qr_url: buildQrUrl("saveenv") },
                { command: "reset", qr_url: buildQrUrl("reset") },
            ],
        });
    },

    backupDatabase() {
        return Promise.resolve({ message: "Database backup started." });
    },

    restoreDatabase() {
        return Promise.resolve({ message: "Database restore started." });
    },

    verifyDatabase() {
        return Promise.resolve({ message: "Database verification passed." });
    },

    reloadConfig() {
        return Promise.resolve({ message: "Configuration reloaded." });
    },

    regenerateCache() {
        return Promise.resolve({ message: "QR cache regenerated." });
    },

    setLogLevel(level) {
        return Promise.resolve({ message: `Log level set to ${level}.` });
    },

    provisionOrder(payload) {
        return Promise.resolve({
            message: `Provisioned ${payload.quantity} device(s) for order ${payload.order_number}.`,
        });
    },

    getOpenOrders() {
        return Promise.resolve({
            orders: [
                { order_number: "12345.6", part_number: "Demo Part A", quantity: 10, completed: 3, device_count:3 },
                { order_number: "54321.1", part_number: "Demo Part B", quantity: 5, completed: 1, device_count: 1 },
            ],
        });
    },

    deleteOrder(orderNumber) {
        return Promise.resolve({ message: `Order ${orderNumber} deleted.` });
    },

    correctOrder(orderNumber, updates) {
        return Promise.resolve({
            message: `Order ${orderNumber} updated.`,
            order_number: updates.new_order_number ||
            orderNumber, 
            quantity: updates.quantity
        });
    },
};

async function withFallback(liveCall, mockCall) {
    if (useMock) {
        return mockCall();
    }

    try {
        return await liveCall();
    } catch (error) {
        if (error instanceof ApiUnreachableError) {
            useMock = true;
            return mockCall();
        }
        throw error;
    }
}

const api = {
    getStatus() {
        return withFallback(
            () => request("/status"),
            () => mockApi.getStatus()
        );
    },

    startSession(payload) {
        return withFallback(
            () => request("/session/start", { method: "POST", body: JSON.stringify(payload) }),
            () => mockApi.startSession(payload)
        );
    },

    getWorkflow() {
        return withFallback(
            () => request("/workflow"),
            () => mockApi.getWorkflow()
        );
    },

    nextStep() {
        return withFallback(
            () => request("/workflow/next", { method: "POST" }),
            () => mockApi.nextStep()
        );
    },

     previousStep() {
         return withFallback(
             () => request("/workflow/previous", { method: "POST" }),
             () => mockApi.previousStep()
         );
     },

    setMacAddresses(mac1, mac2) {
        return withFallback(
            () => request("/workflow/mac", { method: "PUT", body: JSON.stringify({ mac1, mac2 }) }),
            () => mockApi.setMacAddresses(mac1, mac2)
        );
    },

    setTestResult(result, notes) {
        return withFallback(
            () => request("/workflow/result", { method: "PUT", body: JSON.stringify({ result, notes }) }),
            () => mockApi.setTestResult(result, notes)
        );
    },    

    finishSession(serialNumber) {
        return withFallback(
            () => request("/session/finish", { method: "POST", body: JSON.stringify({ serial_number: serialNumber }) }),
            () => mockApi.finishSession(serialNumber)
        );
    },

    cancelSession() {
        return withFallback(
            () => request("/session/cancel", { method: "POST" }),
            () => mockApi.cancelSession()
        );
    },

    getHistory(query = "") {
        return withFallback(
            () => request(`/history?q=${encodeURIComponent(query)}`),
            () => mockApi.getHistory(query)
        );
    },

    exportHistory() {
        return withFallback(
            () => request("/history/export"),
            () => mockApi.exportHistory()
        );
    },

    lookupDevice(serial, orderNumber) {
        const query = orderNumber ? `?order_number=${encodeURIComponent(orderNumber)}` : "";
        return withFallback(
            () => request(`/devices/${encodeURIComponent(serial)}${query}`),
            () => mockApi.lookupDevice(serial)
        );
    },

    lookupMac(mac) {
        return withFallback(
            () => request(`/mac/${encodeURIComponent(mac)}`),
            () => mockApi.lookupMac(mac)
        );
    },

    updateDevice(serial, updates, currentOrderNumber) {
        return withFallback(
            () =>
                request(`/devices/${encodeURIComponent(serial)}`, {
                    method: "PUT",
                    body: JSON.stringify({
                        ...updates, current_order_number: currentOrderNumber
                    }),
                }),
            () => mockApi.updateDevice(serial, updates)
        );
    },

    resetMac(serial, reason, currentOrderNumber) {
        return withFallback(
            () =>
                request(`/devices/${encodeURIComponent(serial)}/reset-mac`, {
                    method: "POST",
                    body: JSON.stringify({ reason, current_order_number: currentOrderNumber  }),
                }),
            () => mockApi.resetMac(serial, reason)
        );
    },

    getMacPool() {
        return withFallback(
            () => request("/mac-pool"),
            () => mockApi.getMacPool()
        );
    },

    getResetDeviceSteps() {
        return withFallback(
            () => request("/reset-device"),
            () => mockApi.getResetDeviceSteps()
        );
    },

    backupDatabase() {
        return withFallback(
            () => request("/database/backup", { method: "POST" }),
            () => mockApi.backupDatabase()
        );
    },

    restoreDatabase() {
        return withFallback(
            () => request("/database/restore", { method: "POST" }),
            () => mockApi.restoreDatabase()
        );
    },

    verifyDatabase() {
        return withFallback(
            () => request("/database/verify", { method: "POST" }),
            () => mockApi.verifyDatabase()
        );
    },

    reloadConfig() {
        return withFallback(
            () => request("/config/reload", { method: "POST" }),
            () => mockApi.reloadConfig()
        );
    },

    regenerateCache() {
        return withFallback(
            () => request("/cache/regenerate", { method: "POST" }),
            () => mockApi.regenerateCache()
        );
    },

    setLogLevel(level) {
        return withFallback(
            () =>
                request("/logging/level", {
                    method: "PUT",
                    body: JSON.stringify({ level }),
                }),
            () => mockApi.setLogLevel(level)
        );
    },

    provisionOrder(payload) {
        return withFallback(
            () => request("/orders/provision", { method: "POST", body: JSON.stringify(payload) }),
            () => mockApi.provisionOrder(payload)
        );
    },

    getOpenOrders() {
        return withFallback(
            () => request("/orders/open"),
            () => mockApi.getOpenOrders()
        );
    },

    deleteOrder(orderNumber, operator) {
        return withFallback(
            () =>
                request(`/orders/${encodeURIComponent(orderNumber)}`, {
                    method: "DELETE",
                    body: JSON.stringify({ operator }),
                }),
            () => mockApi.deleteOrder(orderNumber)
        );
    },

    correctOrder(orderNumber, updates, operator) {
        return withFallback(
            () =>
                request(`/orders/${encodeURIComponent(orderNumber)}`, {
                    method: "PATCH",
                    body: JSON.stringify({ ...updates, operator }),
                }),
            () => mockApi.correctOrder(orderNumber, updates)
        );
    },

};
