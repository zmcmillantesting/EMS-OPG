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
    if (openOrdersSelect) {
        openOrdersSelect.addEventListener("change", () => {
            const orderInput = document.getElementById("order-input");
            if (orderInput && openOrdersSelect.value) {
                orderInput.value = openOrdersSelect.value;
            }
            updateDeleteOrderButton(openOrdersSelect.value);
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
    const isEmpty = Boolean(orderNumber) && orderDeviceCounts[orderNumber] === 0;
    setVisible("delete-order-button", isEmpty);
}

async function handleDeleteOrder() {
    const select = document.getElementById("open-orders-select");
    const orderInput = document.getElementById("order-input");
    const orderNumber = select?.value;

    if (!orderNumber) {
        return;
    }

    if (!confirm(`Delete empty order ${orderNumber}? This cannot be undone.`)) {
        return;
    }

    try {
        await api.deleteOrder(orderNumber);

        const option = select.querySelector(`option[value="${CSS.escape(orderNumber)}"]`);
        if (option) {
            option.remove();
        }
        delete orderDeviceCounts[orderNumber];

        select.value = "";
        if (orderInput && orderInput.value === orderNumber) {
            orderInput.value = "";
        }
        setVisible("delete-order-button", false);
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
