/**
 * Home page behavior — operator identification and order selection.
 */

let orderDeviceCounts = {};
let orderQuantities = {};

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
            updateOrderActionButtons(openOrdersSelect.value);
        });
    }

    if (orderInputE1) {
        orderInputE1.addEventListener("input", ()=> {
            updateOrderActionButton(orderInputE1.value.trim());
        });
    }

    bindClick("delete-order-button", handleDeleteOrder);
    bindClick("edit-order-button", handleEditOrder);

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
        orderQuantities = {};

        select.querySelectorAll('option:not([value=""])').forEach((option) => option.remove());

        result.orders.forEach((order) => {
            orderDeviceCounts[order.order_number] = order.device_count ?? order.completed;
            orderQuantities[order.order_number] = order.quantity;

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

function updateOrderActionButton(orderNumber) {
    setVisible("delete-order-button", Boolean(orderNumber));
    setVisible("edit-order-button", Boolean(orderNumber));
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
        updateOrderActionButton("")

        await loadOpenOrders()
    } catch (error) {
        console.error("Unable to delete order:", error);
        alert(error.message || "Unable to delete this order.");
    }
}

async function handleEditOrder() {
    const select = document.getElementById("open-orders-select");
    const orderInput = document.getElementById("order-input");
    const operatorInput = document.getElementById("operator-input");
    const orderNumber = (orderInput?.value || select?.value || "").trim();

    if (!orderNumber) {
        return;
    }

    // Correcting a mistake on a large order (hundreds of devices) shouldn't
    // require touching devices one at a time - this only renames the order
    // number and/or adjusts the planned quantity; devices are untouched.
    const newOrderNumberRaw = prompt(
        `New order number for ${orderNumber} (leave unchanged to keep it):`,
        orderNumber
    );
    if (newOrderNumberRaw === null) {
        return;
    }
    const newOrderNumber = newOrderNumberRaw.trim();

    const currentQuantity = orderQuantities[orderNumber];
    const newQuantityRaw = prompt(
        `New quantity for ${orderNumber} (leave blank to keep it unchanged):`,
        currentQuantity ?? ""
    );
    if (newQuantityRaw === null) {
        return;
    }
    const trimmedQuantity = newQuantityRaw.trim();

    const updates = {};
    if (newOrderNumber && newOrderNumber !== orderNumber) {
        updates.new_order_number = newOrderNumber;
    }
    if (trimmedQuantity !== "" && Number(trimmedQuantity) !== currentQuantity) {
        if (!Number.isInteger(Number(trimmedQuantity)) || Number(trimmedQuantity) < 1) {
            alert("Quantity must be a whole number of at least 1.");
            return;
        }
        updates.quantity = Number(trimmedQuantity);
    }

    if (Object.keys(updates).length === 0) {
        return;
    }

    try {
        const result = await api.correctOrder(orderNumber, updates, operatorInput?.value.trim());

        if (select) select.value = "";
        if (orderInput) orderInput.value = "";
        updateOrderActionButtons("");

        await loadOpenOrders();

        alert(result.message || "Order updated.");
    } catch (error) {
        console.error("Unable to update order:", error);
        alert(error.message || "Unable to update this order.");
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
