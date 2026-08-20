/**
 * Testing page — QR steps, pass/fail, and (PASS only) serial entry, MAC
 * assignment, and verification. Operator and order are captured on the
 * home page; serial number is only ever entered here, after a PASS.
 */

const PHASES = ["qr", "result", "serial", "mac", "verification"];

const STAGE_META = {
    qr: { title: "Functional Test", sub: "Steps 1–4" },
    result: { title: "Test Result", sub: "Pass/Fail" },
    serial: { title: "Serial Number", sub: "Assign" },
    mac: { title: "MAC Addresses", sub: "Assign" },
    verification: { title: "Verification", sub: "Confirm" },
};

const PHASE_PLACEHOLDER_IDS = {
    qr: "qr-steps-placeholder",
    result: "result-placeholder",
    serial: "serial-placeholder",
    mac: "mac-placeholder",
    verification: "verification-placeholder",
};

const STATE_TO_PHASE = {
    TESTING: "qr",
    AWAITING_RESULT: "result",
    AWAITING_SERIAL: "serial",
    ASSIGNING_MAC: "mac",
    VERIFYING_MAC: "verification",
};

let currentSession = null;

document.addEventListener("DOMContentLoaded", async () => {
    await initPage();

    currentSession = loadSession();
    if (!currentSession) {
        navigateTo("index.html");
        return;
    }

    await loadTestingComponents();
    bindActions();

    try {
        const result = await api.getWorkflow();
        currentSession = result.session;
        saveSession(currentSession);
        render(result.session, result.step);
    } catch (error) {
        console.error("Unable to load workflow:", error);
        clearSession();
        navigateTo("index.html");
    }
});

function bindActions() {
    bindClick("previous-button", handlePrevious);
    bindClick("next-button", handleNext);
    bindClick("home-button", () => navigateTo("index.html"));

    bindClick("result-pass", handleResultPass);
    bindClick("result-fail", handleResultFailShowNotes);
    bindClick("result-fail-submit", handleResultFailSubmit);

    bindClick("serial-prev", handlePrevious);
    bindClick("serial-next", handleSerialSubmit);

    bindClick("mac-assign", handleMacAssign);
    bindClick("mac-prev", handlePrevious);
    bindClick("mac-next", handleMacNext);

    const verifyCheckbox = document.getElementById("verify-confirm");
    if (verifyCheckbox) verifyCheckbox.addEventListener("change", handleVerifyChange);
    bindClick("verification-prev", handlePrevious);
    bindClick("verification-next", handleVerificationNext);

    bindClick("reset-device-toggle", handleResetDeviceToggle);
}

/* ---------- Reset Device (static, unchanged) ---------- */

let resetDeviceLoaded = false;

async function handleResetDeviceToggle() {
    const panel = document.getElementById("reset-device-panel");
    if (!panel) return;

    const showing = panel.classList.contains("hidden");
    setVisible("reset-device-panel", showing);

    if (showing && !resetDeviceLoaded) {
        try {
            const result = await api.getResetDeviceSteps();
            renderResetDevicePanel(result);
            resetDeviceLoaded = true;
        } catch (error) {
            console.error("Unable to load reset device steps:", error);
        }
    }
}

function renderResetDevicePanel(result) {
    const instructionsEl = document.getElementById("reset-device-instructions");
    if (instructionsEl) instructionsEl.textContent = result.instructions;

    const stepsEl = document.getElementById("reset-device-steps");
    if (!stepsEl) return;
    stepsEl.innerHTML = "";

    result.steps.forEach((step, index) => {
        const stepEl = document.createElement("div");
        stepEl.className = "reset-device-step";

        const commandEl = document.createElement("p");
        commandEl.className = "reset-device-step-command";
        commandEl.textContent = `${index + 1}. ${step.command}`;

        const imageEl = document.createElement("img");
        imageEl.className = "qr-image";
        imageEl.src = step.qr_url;
        imageEl.alt = `QR Code for ${step.command}`;

        stepEl.appendChild(commandEl);
        stepEl.appendChild(imageEl);
        stepsEl.appendChild(stepEl);
    });
}

/* ---------- Phase derivation & shared rendering ---------- */

function render(session, step) {
    const phase = STATE_TO_PHASE[session.state] || "qr";

    renderStageNav(phase);
    showPhase(phase);
    updateHeaderOperator(session.operator);

    if (phase === "qr" && step) renderQrStep(step);
    else if (phase === "result") renderResultPhase();
    else if (phase === "serial") renderSerialPhase(session);
    else if (phase === "mac") renderMacPhase(session, step);
    else if (phase === "verification") renderVerificationPhase(step);
}

function showPhase(phase) {
    Object.values(PHASE_PLACEHOLDER_IDS).forEach((id) => {
        const el = document.getElementById(id);
        if (el) el.classList.remove("is-active");
    });
    const activeEl = document.getElementById(PHASE_PLACEHOLDER_IDS[phase]);
    if (activeEl) activeEl.classList.add("is-active");
}

function renderStageNav(phase) {
    const nav = document.getElementById("stage-nav");
    if (!nav) return;

    const activeIndex = PHASES.indexOf(phase);
    nav.innerHTML = "";

    PHASES.forEach((key, index) => {
        const meta = STAGE_META[key];
        const tab = document.createElement("button");
        tab.type = "button";
        tab.className = "stage-tab";
        tab.disabled = true;
        if (index === activeIndex) tab.classList.add("is-active");
        if (index < activeIndex) tab.classList.add("is-complete");

        tab.innerHTML = `
            <span class="stage-index">${index < activeIndex ? "&#10003;" : index + 1}</span>
            <span class="stage-label">
                <span class="stage-title">${meta.title}</span>
                <span class="stage-sub">${meta.sub}</span>
            </span>`;

        nav.appendChild(tab);
    });
}

function updateHeaderOperator(operator) {
    const el = document.getElementById("header-operator");
    if (el) el.textContent = operator ? `Operator: ${operator}` : "";
}

/* ---------- Phase: QR steps (1-4) ---------- */

async function handlePrevious() {
    try {
        const result = await api.previousStep();
        currentSession = result.session;
        saveSession(currentSession);
        render(result.session, result.step);
    } catch (error) {
        console.error("Unable to go to previous step:", error);
    }
}

async function handleNext() {
    try {
        const result = await api.nextStep();
        currentSession = result.session;
        saveSession(currentSession);
        render(result.session, result.step);
    } catch (error) {
        console.error("Unable to advance workflow:", error);
    }
}

function renderQrStep(step) {
    const workflowName = document.getElementById("workflow-name");
    const stepIndicator = document.getElementById("step-indicator");
    const commandEl = document.getElementById("current-command");
    const qrImage = document.getElementById("qr-image");
    const previousButton = document.getElementById("previous-button");
    const nextButton = document.getElementById("next-button");

    if (workflowName) workflowName.textContent = step.workflow_name;
    if (stepIndicator) {
        stepIndicator.textContent = `Step ${step.step_number} of ${step.total_steps} — ${step.step_name}`;
    }
    if (commandEl) commandEl.textContent = step.command;
    if (qrImage) {
        qrImage.src = step.qr_url;
        qrImage.alt = `QR Code for ${step.step_name}`;
    }
    if (previousButton) previousButton.disabled = step.step_index === 0;
    if (nextButton) {
        nextButton.textContent = "Next";
        nextButton.disabled = false;
    }
}

/* ---------- Phase: Test Result ---------- */

function renderResultPhase() {
    document.getElementById("result-notes").value = "";
    setVisible("result-notes-row", false);
}

async function handleResultPass() {
    try {
        const result = await api.setTestResult("PASS", "");
        currentSession = result.session;
        saveSession(currentSession);
        render(result.session, result.step);
    } catch (error) {
        console.error("Unable to record test result:", error);
        alert(error.message || "Unable to record test result.");
    }
}

function handleResultFailShowNotes() {
    setVisible("result-notes-row", true);
    document.getElementById("result-notes").focus();
}

async function handleResultFailSubmit() {
    const notesInput = document.getElementById("result-notes");
    const notes = notesInput.value.trim();
    if (!notes) {
        notesInput.focus();
        return;
    }

    try {
        const result = await api.setTestResult("FAIL", notes);
        currentSession = result.session;
        saveSession(currentSession);

        // FAIL has no serial/MAC phase - save-ready the instant the
        // reason is in, and there's no device to identify, just the order.
        if (result.session.state === "READY_TO_SAVE") {
            await finishAndRestart();
        } else {
            render(result.session, result.step);
        }
    } catch (error) {
        console.error("Unable to record test result:", error);
        alert(error.message || "Unable to record test result.");
    }
}

/* ---------- Phase: Serial Number (PASS only) ---------- */

function renderSerialPhase(session) {
    document.getElementById("serial-input").value = "";
    document.getElementById("serial-order").textContent = session.order_number || "—";
}

async function handleSerialSubmit() {
    const serialInput = document.getElementById("serial-input");
    const serial = serialInput.value.trim();

    if (!isValidSerialNumber(serial)) {
        alert("Serial number must be formatted as EMyyww0000.");
        serialInput.focus();
        return;
    }

    try {
        const result = await api.setSerialNumber(serial);
        currentSession = result.session;
        saveSession(currentSession);
        render(result.session, result.step);
    } catch (error) {
        console.error("Unable to record serial number:", error);
        alert(error.message || "Unable to record serial number.");
    }
}

/* ---------- Phase: MAC Addresses (PASS only) ---------- */

function renderMacPhase(session, step) {
    const mac1Input = document.getElementById("mac1-input");
    const nextButton = document.getElementById("mac-next");

    if (session.mac1 && session.mac2) {
        if (mac1Input) mac1Input.value = session.mac1;
        showMacResult(session, step);
        if (nextButton) nextButton.disabled = false;
    } else {
        if (mac1Input) mac1Input.value = "";
        setVisible("mac-result", false);
        if (nextButton) nextButton.disabled = true;
    }
}

function showMacResult(session, step) {
    document.getElementById("mac1-value").textContent = session.mac1;
    document.getElementById("mac2-value").textContent = session.mac2;
    document.getElementById("mac-command").textContent = step.command;

    const qrImage = document.getElementById("mac-qr-image");
    qrImage.src = step.qr_url;
    qrImage.alt = "QR Code for MAC assignment";

    setVisible("mac-result", true);
}

async function handleMacAssign() {
    const mac1Input = document.getElementById("mac1-input");
    const mac1 = mac1Input.value.trim();
    if (!mac1) {
        mac1Input.focus();
        return;
    }

    try {
        const result = await api.assignMac1(mac1);
        currentSession = result.session;
        saveSession(currentSession);
        showMacResult(result.session, result.step);
        document.getElementById("mac-next").disabled = false;
    } catch (error) {
        console.error("Unable to assign MAC addresses:", error);
        alert(error.message || "Unable to assign MAC addresses.");
    }
}

async function handleMacNext() {
    try {
        const result = await api.confirmMacAssignment();
        currentSession = result.session;
        saveSession(currentSession);
        render(result.session, result.step);
    } catch (error) {
        console.error("Unable to continue to verification:", error);
        alert(error.message || "Unable to continue to verification.");
    }
}

/* ---------- Phase: Verification (PASS only) ---------- */

function renderVerificationPhase(step) {
    document.getElementById("verification-command").textContent = step.command;

    const qrImage = document.getElementById("verification-qr-image");
    qrImage.src = step.qr_url;
    qrImage.alt = "QR Code for Verification";

    const checkbox = document.getElementById("verify-confirm");
    checkbox.checked = false;

    document.getElementById("chip-mac1").classList.remove("is-verified");
    document.getElementById("chip-mac2").classList.remove("is-verified");
    document.getElementById("verification-next").disabled = true;
}

function handleVerifyChange(event) {
    const confirmed = event.target.checked;
    document.getElementById("chip-mac1").classList.toggle("is-verified", confirmed);
    document.getElementById("chip-mac2").classList.toggle("is-verified", confirmed);
    document.getElementById("verification-next").disabled = !confirmed;
}

async function handleVerificationNext() {
    try {
        const result = await api.confirmVerification();
        currentSession = result.session;
        saveSession(currentSession);

        if (result.session.state === "READY_TO_SAVE") {
            await finishAndRestart();
        } else {
            render(result.session, result.step);
        }
    } catch (error) {
        console.error("Unable to confirm verification:", error);
        alert(error.message || "Unable to confirm verification.");
    }
}

/* ---------- Save + loop to next board ---------- */

async function finishAndRestart() {
    try {
        const result = await api.finishSession();
        currentSession = result.session;
        saveSession(currentSession);
        // Operator + order stay fixed - loop straight back into the
        // next board's QR steps rather than returning to the home page.
        render(result.session, null);
    } catch (error) {
        console.error("Unable to save:", error);
        alert(error.message || "Unable to save.");
    }
}