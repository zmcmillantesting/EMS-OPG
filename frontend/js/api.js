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
        ethaddr1_id: "00:60:47:12:34:02",
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
        ethaddr1_id: "00:60:47:12:34:04",
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
        ethaddr1_id: "00:60:47:12:34:06",
        operator: "Zach",
        test_result: "FAIL",
        used: false,
    },
];

let mockSession = null;
let useMock = false;

async function request(path, options = {}) {
    const config = {
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {}),
        },
        ...options,
    };

    try {
        const response = await fetch(`${API_BASE}${path}`, config);

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        if (response.status === 204) {
            return null;
        }

        return response.json();
    } catch (error) {
        useMock = true;
        throw error;
    }
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
    const encoded = encodeURIComponent(command);
    return `https://api.qrserver.com/v1/create-qr-code/?size=400x400&data=${encoded}`;
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
            record.ethaddr1_id,
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

    finishSession(serialNumber) {
        if (!mockSession) {
            return Promise.reject(new Error("No active session"));
        }

        mockSession.serial_number = serialNumber;

        return Promise.resolve({
            session: { ...mockSession },
            message: "Device saved to trace log",
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
            record.ethaddr1_id || "",
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
            ethaddr1_id: updates.mac2 ?? device.ethaddr1_id,
        });

        return Promise.resolve({ device, message: "Device updated successfully." });
    },

    resetMac(serial) {
        const device = findDeviceBySerial(serial);
        if (!device) {
            return Promise.reject(new Error("Device not found"));
        }

        device.used = false;
        return Promise.resolve({ device, message: "MAC reset successfully." });
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
};

async function withFallback(liveCall, mockCall) {
    if (useMock) {
        return mockCall();
    }

    try {
        return await liveCall();
    } catch {
        useMock = true;
        return mockCall();
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

    lookupDevice(serial) {
        return withFallback(
            () => request(`/devices/${encodeURIComponent(serial)}`),
            () => mockApi.lookupDevice(serial)
        );
    },

    updateDevice(serial, updates) {
        return withFallback(
            () =>
                request(`/devices/${encodeURIComponent(serial)}`, {
                    method: "PUT",
                    body: JSON.stringify(updates),
                }),
            () => mockApi.updateDevice(serial, updates)
        );
    },

    resetMac(serial) {
        return withFallback(
            () =>
                request(`/devices/${encodeURIComponent(serial)}/reset-mac`, {
                    method: "POST",
                }),
            () => mockApi.resetMac(serial)
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
};
