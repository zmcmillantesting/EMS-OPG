/**
 * Home page behavior — operator ID, order selection/creation, and serial
 * number entry. The redesigned workflow captures the serial number here,
 * before the functional test runs, rather than at the end of a session.
 */

let orderQuantities = {};

document.addEventListener("DOMContentLoaded", async () => {
    const status = await initPage();
    bindHomeActions(status);
    await loadOrders();
});

function bindHomeActions(status) {
    const form = document.getElementById("start-test-form");
    if (form) form.addEventListener("submit", handleStartTest);

    const orderSelect = document.getElementById("order-select");
    if (orderSelect) {
        orderSelect.addEventListener("change", () => {
            updateOrderActionButtons(orderSelect.value);
        });
    }

    bindClick("new-order-toggle", handleNewOrderToggle);
    bindClick("new-order-create", handleCreateOrder);
    bindClick("delete-order-button", handleDeleteOrder);
    bindClick("edit-order-button", handleEditOrder);

    if (status) {
        const devicesCount = document.getElementById("home-devices-count");
        const version = document.getElementById("home-version");
        const databaseStatus = document.getElementById("home-database-status");

        if (devicesCount) devicesCount.textContent = status.devicesToday ?? "—";
        if (version && status.version) version.textContent = status.version;
        if (databaseStatus) {
            databaseStatus.textContent = status.databaseConnected ? "Connected" : "Offline";
            databaseStatus.className = `status-value ${status.databaseConnected ? "status-success" : "status-error"}`;
        }
    }
}

async function loadOrders() {
    const select = document.getElementById("order-select");
    if (!select) return;

    try {
        const result = await api.getOrders();
        orderQuantities = {};

        select.querySelectorAll('option:not([value=""])').forEach((option) => option.remove());

        result.orders.forEach((order) => {
            orderQuantities[order.order_number] = order.quantity;

            const option = document.createElement("option");
            option.value = order.order_number;
            option.textContent = `${order.order_number} — ${order.passed}/${order.quantity} passed`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error("Unable to load orders:", error);
    }
}

function updateOrderActionButtons(orderNumber) {
    setVisible("delete-order-button", Boolean(orderNumber));
    setVisible("edit-order-button", Boolean(orderNumber));
}

function handleNewOrderToggle() {
    const panel = document.getElementById("new-order-panel");
    if (!panel) return;
    setVisible("new-order-panel", panel.classList.contains("hidden"));
}

async function handleCreateOrder() {
    const numberInput = document.getElementById("new-order-number-input");
    const quantityInput = document.getElementById("new-order-quantity-input");

    const orderNumber = numberInput.value.trim();
    const quantity = Number(quantityInput.value);

    if (!isValidOrderNumber(orderNumber)) {
        alert("Order number must be formatted as 0000.0 or 00000.0.");
        numberInput.focus();
        return;
    }
    if (!Number.isInteger(quantity) || quantity < 1) {
        alert("Quantity must be a whole number of at least 1.");
        quantityInput.focus();
        return;
    }

    try {
        await api.createOrder({ order_number: orderNumber, quantity });
        numberInput.value = "";
        quantityInput.value = "";
        setVisible("new-order-panel", false);

        await loadOrders();
        document.getElementById("order-select").value = orderNumber;
        updateOrderActionButtons(orderNumber);
    } catch (error) {
        console.error("Unable to create order:", error);
        alert(error.message || "Unable to create this order.");
    }
}

async function handleDeleteOrder() {
    const select = document.getElementById("order-select");
    const operatorInput = document.getElementById("operator-input");
    const orderNumber = (select?.value || "").trim();

    if (!orderNumber) return;

    if (!confirm(
        `Delete order ${orderNumber}? This only works if no devices have ` +
        `been recorded against it yet, and cannot be undone.`
    )) {
        return;
    }

    try {
        await api.deleteOrder(orderNumber, operatorInput?.value.trim());
        updateOrderActionButtons("");
        await loadOrders();
    } catch (error) {
        console.error("Unable to delete order:", error);
        alert(error.message || "Unable to delete this order.");
    }
}

async function handleEditOrder() {
    const select = document.getElementById("order-select");
    const operatorInput = document.getElementById("operator-input");
    const orderNumber = (select?.value || "").trim();

    if (!orderNumber) return;

    const newOrderNumberRaw = prompt(
        `New order number for ${orderNumber} (leave unchanged to keep it):`,
        orderNumber
    );
    if (newOrderNumberRaw === null) return;
    const newOrderNumber = newOrderNumberRaw.trim();

    const currentQuantity = orderQuantities[orderNumber];
    const newQuantityRaw = prompt(
        `New quantity for ${orderNumber} (leave blank to keep it unchanged):`,
        currentQuantity ?? ""
    );
    if (newQuantityRaw === null) return;
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

    if (Object.keys(updates).length === 0) return;

    try {
        const result = await api.correctOrder(orderNumber, updates, operatorInput?.value.trim());
        updateOrderActionButtons("");
        await loadOrders();
        alert(result.message || "Order updated.");
    } catch (error) {
        console.error("Unable to update order:", error);
        alert(error.message || "Unable to update this order.");
    }
}

async function handleStartTest(event) {
    event.preventDefault();

    const operatorInput = document.getElementById("operator-input");
    const orderSelect = document.getElementById("order-select");
    const serialInput = document.getElementById("serial-input");

    const operator = operatorInput.value.trim();
    const order = orderSelect.value.trim();
    const serial = serialInput.value.trim();

    if (!operator) {
        operatorInput.focus();
        return;
    }
    if (!order) {
        orderSelect.focus();
        return;
    }
    if (!isValidSerialNumber(serial)) {
        alert("Serial number must be formatted as EMyyww0000.");
        serialInput.focus();
        return;
    }

    clearSession();

    try {
        const result = await api.startSession({ order_number: order, operator, serial_number: serial });
        saveSession(result.session);
        navigateTo("testing.html");
    } catch (error) {
        console.error("Unable to start session:", error);
        alert(error.message || "Unable to start a new test session.");
    }
}