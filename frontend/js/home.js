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

function startNewTest() {
    // Starting fresh discards any abandoned in-progress session
    // The testing page collects OrdNo and opID 
    clearSession()
    navigateTo("testing.html")
}
