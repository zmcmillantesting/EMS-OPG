/**
 * Shared frontend utilities for EMS-OPG.
 */

const PAGE_COMPONENTS = {
    header: "components/header.html",
    footer: "components/footer.html",
    navigation: "components/navigation.html",
    qrPanel: "components/qr_panel.html",
    commandPanel: "components/command_panel.html",
    macPanel: "components/macPanel.html",
    verificationPanel: "components/verificationPanel.html",
    resultPanel: "components/resultPanel.html",
    serialPanel: "components/serialPanel.html",
};

const ORDER_NUMBER_PATTERN = /^\d{4,5}\.\d$/;
const SERIAL_NUMBER_PATTERN = /^EM\d{8}$/;

function isValidOrderNumber(value) {
    return ORDER_NUMBER_PATTERN.test(value || "");
}

function isValidSerialNumber(value) {
    return SERIAL_NUMBER_PATTERN.test(value || "");
}

/**
 * Load an HTML component into a placeholder element.
 */
async function loadComponent(placeholderId, componentPath) {
    const placeholder = document.getElementById(placeholderId);
    if (!placeholder) {
        return;
    }

    try {
        const response = await fetch(componentPath);
        if (!response.ok) {
            throw new Error(`Failed to load ${componentPath}`);
        }
        placeholder.innerHTML = await response.text();
    } catch (error) {
        console.error(error);
    }
}

/**
 * Load standard page chrome (header and footer).
 */
async function loadPageChrome() {
    await Promise.all([
        loadComponent("header-placeholder", PAGE_COMPONENTS.header),
        loadComponent("footer-placeholder", PAGE_COMPONENTS.footer),
    ]);
}

/**
 * Load testing page panels.
 */
async function loadTestingComponents() {
    await Promise.all([
        loadComponent("command-panel-placeholder", PAGE_COMPONENTS.commandPanel),
        loadComponent("qr-panel-placeholder", PAGE_COMPONENTS.qrPanel),
        loadComponent("navigation-placeholder", PAGE_COMPONENTS.navigation),
        loadComponent("result-placeholder", PAGE_COMPONENTS.resultPanel),
        loadComponent("serial-placeholder", PAGE_COMPONENTS.serialPanel),
        loadComponent("mac-placeholder", PAGE_COMPONENTS.macPanel),
        loadComponent("verification-placeholder", PAGE_COMPONENTS.verificationPanel),
    ]);
}

/**
 * Navigate to another page.
 */
function navigateTo(page) {
    window.location.href = page;
}

/**
 * Bind a click handler when the element exists.
 */
function bindClick(elementId, handler) {
    const element = document.getElementById(elementId);
    if (element) {
        element.addEventListener("click", handler);
    }
}

/**
 * Format an ISO date string for display.
 */
function formatDate(isoString) {
    if (!isoString) {
        return "—";
    }

    const date = new Date(isoString);
    if (Number.isNaN(date.getTime())) {
        return isoString;
    }

    return date.toLocaleDateString(undefined, {
        year: "numeric",
        month: "short",
        day: "numeric",
    });
}

/**
 * Update the persistent status bar in the footer.
 */
function updateStatusBar(status) {
    const versionEl = document.getElementById("status-version");
    const databaseEl = document.getElementById("status-database");
    const workflowEl = document.getElementById("status-workflow");

    if (versionEl && status.version) {
        versionEl.textContent = `EMS-OPG v${status.version}`;
    }

    if (databaseEl) {
        databaseEl.textContent = status.databaseConnected
            ? "SQLite Connected"
            : "Database Offline";
        databaseEl.className = `status-item ${status.databaseConnected ? "status-success" : "status-error"}`;
    }

    if (workflowEl) {
        workflowEl.textContent = status.workflowReady
            ? "Workflow Ready"
            : "Workflow Unavailable";
        workflowEl.className = `status-item ${status.workflowReady ? "status-success" : "status-warning"}`;
    }
}

/**
 * Show or hide an element by id.
 */
function setVisible(elementId, visible) {
    const element = document.getElementById(elementId);
    if (element) {
        element.classList.toggle("hidden", !visible);
    }
}

/**
 * Save text content to a file, choosing the right mechanism for where
 * the app is actually running:
 *  - Inside the PyWebView desktop window, browser download tricks
 *    (Blob URL + <a download>) aren't reliably supported, so this calls
 *    the native save-file dialog exposed by core/webview_api.py instead.
 *  - In a plain browser tab (e.g. local development without the
 *    PyWebView window), falls back to the standard download approach.
 * Returns true if the file was actually written, false if the operator
 * cancelled the save dialog (not an error - callers shouldn't alert on it).
 */
async function saveFile(content, filename, mimeType = "text/plain;charset=utf-8;") {
    if (window.pywebview && window.pywebview.api && window.pywebview.api.save_file) {
        const result = await window.pywebview.api.save_file(filename, content);
        return Boolean(result && result.saved);
    }

    const blob = new Blob([content], { type: mimeType });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
    URL.revokeObjectURL(link.href);
    return true;
}


/**
 * Store the active workflow session in sessionStorage.
 */
function saveSession(session) {
    sessionStorage.setItem("ems-opg-session", JSON.stringify(session));
}

/**
 * Retrieve the active workflow session.
 */
function loadSession() {
    const raw = sessionStorage.getItem("ems-opg-session");
    if (!raw) {
        return null;
    }

    try {
        return JSON.parse(raw);
    } catch {
        return null;
    }
}

/**
 * Clear the active workflow session.
 */
function clearSession() {
    sessionStorage.removeItem("ems-opg-session");
}

/**
 * Initialize common page setup: load chrome and refresh status.
 */
async function initPage() {
    await loadPageChrome();

    try {
        const status = await api.getStatus();
        updateStatusBar(status);
        return status;
    } catch (error) {
        console.error("Unable to load application status:", error);
        return null;
    }
}
