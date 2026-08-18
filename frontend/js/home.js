/**
 * Home page behavior — operator identification and order selection.
 */

let orderDeviceCounts = {};

document.addEventListener("DOMContentLoaded", async () => {
    const status = await initPage();
    bindHomeActions(status);
    await loadOpenOrders();
});

function bindHomeActions(status) {
    const form = document.getElementById("start-test-form");
    if (form) {
        form.addEventListener("submit", handleStartTest);
    }

    const openOrdersSelect = document.getElementById("open-orders-select");
    const orderInputE1 = document.getElementById("order-input");
    if (openOrdersSelect) {
        openOrdersSelect.addEventListener("change", () => {
            if (orderInputE1 && openOrdersSelect.value) {
                orderInputE1.value = openOrdersSelect.value;
            }
            updateDeleteOrderButton(openOrdersSelect.value);
        });
    }

    if (orderInputE1) {
        orderInputE1.addEventListener("input", ()=> {
            updateDeleteOrderButton(orderInputE1.value.trim());
        });
    }

    bindClick("delete-order-button", handleDeleteOrder);

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
        orderDeviceCounts = {};

        select.querySelectorAll('option:not([value="])').forEach((option) => option.remove());

        result.orders.forEach((order) => {
            orderDeviceCounts[order.order_number] = order.device_count ?? order.completed;

            const option = document.createElement("option");
            option.value = order.order_number;
            option.textContent =
                order.device_count === 0
                    ? `${order.order_number} — ${order.part_number} (empty — nothing provisioned)`
                    : `${order.order_number} — ${order.part_number} (${order.completed}/${order.quantity})`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error("Unable to load open orders:", error);
    }
}

function updateDeleteOrderButton(orderNumber) {
    setVisible("delete-order-button", Boolean(orderNumber));
}

async function handleDeleteOrder() {
    const select = document.getElementById("open-orders-select");
    const orderInput = document.getElementById("order-input");
    const operatorInput = document.getElementById("operator-input");
    const orderNumber = (orderInput?.value || select?.value || "").trim();

    if (!orderNumber) {
        return;
    }

    const knownCount = orderDeviceCounts[orderNumber];
    const confirmMessage = knownCount
        ? `Reset order ${orderNumber}? Its ${knownCount} device(s) will be marked ` +
          `available again for re-testing. Serial numbers, operators, and MAC ` +
          `assignments are kept - this does not release any MAC addresses.`
        : `Delete or reset order ${orderNumber}? If it has devices assigned, ` + 
        `they will be marked available again for retesting (serial numbers, operators, ` +
        `and MAC assignments are kept). If it's empty the order itself will be deleted. This cannot be undone`;

    if (!confirm(confirmMessage)) {
        return;
    }

    try {
        await api.deleteOrder(orderNumber, operatorInput?.value.trim());
        if (select) select.value = ""
        if (orderInput) orderInput.value = "";
        setVisible("delete-order-button", false);

        await loadOpenOrders()
    } catch (error) {
        console.error("Unable to delete order:", error);
        alert(error.message || "Unable to delete this order.");
    }
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

    // Starting fresh discards any abandoned in-progress session
    clearSession();

    try {
        const result = await api.startSession({ order_number: order, operator });
        saveSession(result.session);
        navigateTo("testing.html");
    } catch (error) {
        console.error("Unable to start session:", error);
        alert(error.message || "Unable to start a new test session.");
    }
}
