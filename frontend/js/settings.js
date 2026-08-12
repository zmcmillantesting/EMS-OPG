/**
 * Settings page — configuration tools and manual corrections.
 */

let activeDeviceSerial = null;

document.addEventListener("DOMContentLoaded", async () => {
    await initPage();
    bindSettingsActions();
});

function bindSettingsActions() {
    bindClick("backup-button", () => runAction(() => api.backupDatabase()));
    bindClick("restore-button", () => runAction(() => api.restoreDatabase()));
    bindClick("verify-button", () => runAction(() => api.verifyDatabase()));
    bindClick("reload-config-button", () => runAction(() => api.reloadConfig()));
    bindClick("regenerate-cache-button", () => runAction(() => api.regenerateCache()));
    bindClick("open-logs-button", () => window.open("/logs/application.log", "_blank"));

    const logLevel = document.getElementById("log-level");
    if (logLevel) {
        logLevel.addEventListener("change", async () => {
            await runAction(() => api.setLogLevel(logLevel.value));
        });
    }

    bindClick("lookup-device-button", lookupDevice);
    bindClick("lookup-mac-button", lookupDeviceByMac);

    const correctionForm = document.getElementById("correction-form");
    if (correctionForm) {
        correctionForm.addEventListener("submit", saveCorrections);
    }

    bindClick("reset-mac-button", resetMac);

    const provisionForm = document.getElementById("provision-form");
    if (provisionForm) {
        provisionForm.addEventListener("submit", provisionOrder)
    }
}

async function provisionOrder(event) {
    event.preventDefault();

    const orderNumber = getFieldValue("provision-order");
    const partNumber = getFieldValue("provision-part");
    const quantity = parseInt(getFieldValue("provision-quantity"), 10);

    const messageE1 = document.getElementById("provision-message");
    const showProvisionMessage = (text, type) => {
        if (!messageE1) return;
        messageE1.textContent = text;
        messageE1.className = `correction-message ${type}`;
        messageE1.classList.remove("hidden")
    };

    if (!orderNumber || !partNumber || !quantity || quantity < 1) {
        showProvisionMessage("Order number, Part number, and a quantity of at least 1 are required", "error");
        return;
    }

    if (!isValidOrderNumber(orderNumber)) {
        showProvisionMessage("Order number must be formateed as 0000.0 or 00000.0", "error");
        return;
    }

    try {
        const result = await api.provisionOrder({
            order_number: orderNumber,
            part_number: partNumber,
            quantity,
        });
        showProvisionMessage(result.message || "success")
    } catch (error) {
        showProvisionMessage(error.message || "Unable to provision order.", "error")
    }
}


async function runAction(action) {
    try {
        const result = await action();
        showMessage(result.message || "Action completed.", "success");
    } catch (error) {
        console.error(error);
        showMessage(error.message || "Action failed.", "error");
    }
}

async function lookupDevice() {
    const serialInput = document.getElementById("correction-serial");
    const serial = serialInput?.value.trim();

    if (!serial) {
        showMessage("Enter a serial number to lookup.", "error");
        return;
    }

    try {
        const result = await api.lookupDevice(serial);
        populateCorrectionForm(result.device);
        activeDeviceSerial = result.device.serial_number;
        setVisible("correction-fields", true);
        showMessage(`Loaded device ${result.device.serial_number}.`, "success");
    } catch (error) {
        setVisible("correction-fields", false);
        activeDeviceSerial = null;
        showMessage("Device not found.", "error");
    }
}

async function lookupDeviceByMac() {
    const macInput = document.getElementById("correction-mac");
    const mac = macInput?.value.trim();

    if (!mac) {
        showMessage("Enter a MAC address to lookup.", "error");
        return;
    }

    try {
        const result = await api.lookupMac(mac);
        populateCorrectionForm(result.device);
        activeDeviceSerial = result.device.serial_number;
        setVisible("correction-fields", true);
        showMessage(`Loaded device ${result.device.serial_number}.`, "success");
    } catch (error) {
        setVisible("correction-fields", false);
        activeDeviceSerial = null;
        showMessage("Device not found.", "error");
    }
}

function populateCorrectionForm(device) {
    setFieldValue("correction-order", device.order_number);
    setFieldValue("correction-new-serial", device.serial_number);
    setFieldValue("correction-operator", device.operator);
    setFieldValue("correction-mac1", device.ethaddr_id);
    setFieldValue("correction-mac2", device.eth1addr_id || "");
}

async function saveCorrections(event) {
    event.preventDefault();

    if (!activeDeviceSerial) {
        showMessage("Lookup a device before saving corrections.", "error");
        return;
    }

    const reason = getFieldValue("correction-reason");
    if (!reason) {
        showMessage("A reason is required for manual corrections.", "error")
        return;
    }

    const newSerial = getFieldValue("correction-new-serial");
    if (!isValidSerialNumber(newSerial)) {
        showMessage("Serial number must be formatted as EMyyyyww0000.", "error");
        return;
    }

    const updates = {
        order_number: getFieldValue("correction-order"),
        serial_number: getFieldValue("correction-new-serial"),
        operator: getFieldValue("correction-operator"),
        mac1: getFieldValue("correction-mac1"),
        mac2: getFieldValue("correction-mac2"),
        reason,
    };

    try {
        const result = await api.updateDevice(activeDeviceSerial, updates);
        activeDeviceSerial = result.device.serial_number;
        populateCorrectionForm(result.device);
        setFieldValue("correction-reason", "")
        showMessage(result.message, "success");
    } catch (error) {
        showMessage(error.message || "Unable to save corrections.", "error");
    }
}

async function resetMac() {
    if (!activeDeviceSerial) {
        showMessage("Lookup a device before resetting MAC.", "error");
        return;
    }

    const reason = getFieldValue("correction-reason");
    if (!reason) {
        showMessage("A reason is required to reset a MAC address.", "error");
        return;
    }

    if (!confirm(`Reset MAC used status for ${activeDeviceSerial}?`)) {
        return;
    }

    try {
        const result = await api.resetMac(activeDeviceSerial, serial);
        populateCorrectionForm(result.device);
        setFieldValue("correction-reason, ")
        showMessage(result.message, "success");
    } catch (error) {
        showMessage(error.message || "Unable to reset MAC.", "error");
    }
}

function showMessage(text, type) {
    const messageEl = document.getElementById("correction-message");
    if (!messageEl) {
        return;
    }

    messageEl.textContent = text;
    messageEl.className = `correction-message ${type}`;
    messageEl.classList.remove("hidden");
}

function getFieldValue(id) {
    return document.getElementById(id)?.value.trim() || "";
}

function setFieldValue(id, value) {
    const field = document.getElementById(id);
    if (field) {
        field.value = value ?? "";
    }
}
