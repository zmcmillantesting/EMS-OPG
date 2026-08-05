/**
 * Home page behavior.
 */

document.addEventListener("DOMContentLoaded", async () => {
    const status = await initPage();
    bindHomeActions(status);
});

function bindHomeActions(status) {
    bindClick("start-test", startNewTest);

    if (status) {
        const devicesCount = document.getElementById("home-devices-count");
        const version = document.getElementById("home-version");
        const databaseStatus = document.getElementById("home-database-status");

        if (devicesCount) {
            devicesCount.textContent = status.devicesToday ?? "—";
        }

        if (version && status.version) {
            version.textContent = status.version;
        }

        if (databaseStatus) {
            databaseStatus.textContent = status.databaseConnected ? "Connected" : "Offline";
            databaseStatus.className = `status-value ${status.databaseConnected ? "status-success" : "status-error"}`;
        }
    }
}

async function startNewTest() {
    const existingSession = loadSession();

    if (!existingSession) {
        try {
            const result = await api.startSession({
                operator: "Operator",
                order_number: prompt("Enter order number:", "123456") || "123456",
                serial_number: prompt("Enter serial number:", "SN001") || "SN001",
                mac1: prompt("Enter MAC 1:", "00:60:47:12:34:01") || "00:60:47:12:34:01",
                mac2: prompt("Enter MAC 2:", "00:60:47:12:34:02") || "00:60:47:12:34:02",
            });

            saveSession(result.session);
        } catch (error) {
            console.error("Unable to start session:", error);
            alert("Unable to start a new test session.");
            return;
        }
    }

    navigateTo("testing.html");
}
