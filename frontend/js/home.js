/**
 * Home page behavior - operator identifcation and order selection
 */

document.addEventListener("DOMContentLoaded", async () => {
    const status = await initPage();
    bindHomeActions(status);
    await loadOpenOrders();
});

function bindHomeActions(status) {
    const form = document.getElementById("start-test-form")
    if (form) {
        form.addEventListener("submit", handleStartTest)
    }

    const openOrderSelect = document.getElementById("open-orders-select")
    if (openOrderSelect) {
        openOrderSelect.addEventListener("change", () => {
            const orderInput = document.getElementById("order-input");
            if (orderInput && openOrderSelectl.value) {
                orderInput.value = openOrderSelect.value;
            }
        });
    }

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

async function loadOpenOrders() {
    const select = document.getElementById("open-orders-select");
    if (!select) return;

    try {
        const result = await api.getOpenOrders();

        result.orders.forEach((order) => {
            const option = document.createElement("option");
            option.value = order.order_number;
            option.textContent = `${order.order_number} - ${order.part_number} (${order.completed}/${order.quantity})`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error("Unable to load open orders:", error);
    s}
}

async function handleStartTest(event) {
    event.preventDefault();

    const operatorInput = document.getElementById("operator-input");
    const orderInput = document.getElementById("order-input");
    const operator = operatorInput.value.trim();
    const order = orderInput.value.trim();

    if (!operator) {
        operatorInput.focus();
        return;
    }
    if (!order) {
        orderInput.focus();
        return;
    }

    try {
        const result = await api.startSession({ order_number: order, operator })
        saveSession(result.session);
        navigateTo("testing.html")
    } catch (error) {
        console.error("Unable to start session:", error)
        alert(error.message || "Unable to start a new test session.")
    }
}

