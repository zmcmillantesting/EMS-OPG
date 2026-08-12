/**
 * Testing page — order/operator intake, QR steps, MAC assignment,
 * verification, and serial number capture.
 */

const PHASES = ["order", "qr", "mac", "verification", "serial"];

const STAGE_META = {
    order: { title: "Order & Operator", sub: "Start" },
    qr: { title: "Test QR Codes", sub: "Steps 1–4" },
    mac: { title: "MAC Addresses", sub: "Step 5" },
    verification: { title: "Verification", sub: "Step 6" },
    serial: { title: "Serial Number", sub: "Finish" },
};

const PHASE_PLACEHOLDER_IDS = {
    order: "order-operator-placeholder",
    qr: "qr-steps-placeholder",
    mac: "mac-placeholder",
    verification: "verification-placeholder",
    serial: "serial-placeholder",
};

let currentSession = null;

document.addEventListener("DOMContentLoaded", async () => {
    await initPage();
    await loadTestingComponents();
    bindActions();

    currentSession = loadSession();

    if (!currentSession) {
        render(null);
        return;
    }

    try {
        const result = await api.getWorkflow();
        currentSession = result.session;
        saveSession(currentSession);
        render(result.step);
    } catch (error) {
        console.error("Unable to load workflow:", error);
        clearSession();
        currentSession = null;
        render(null);
    }
});

function bindActions() {
    bindClick("order-operator-continue", handleOrderOperatorContinue);

    bindClick("previous-button", handlePrevious);
    bindClick("next-button", handleNext);
    bindClick("home-button", () => navigateTo("index.html"));

    bindClick("mac-assign", handleMacAssign);
    bindClick("mac-prev", handlePrevious);
    bindClick("mac-next", handleNext);

    const verifyCheckbox = document.getElementById("verify-confirm");
    if (verifyCheckbox) {
        verifyCheckbox.addEventListener("change", handleVerifyChange);
    }
    bindClick("verification-prev", handlePrevious);
    bindClick("verification-next", handleNext);

    bindClick("serial-prev", handlePrevious);
    bindClick("serial-finish", handleFinish);
function bindActions() {
    bindClick("order-operator-continue", handleOrderOperatorContinue);

    bindClick("previous-button", handlePrevious);
    bindClick("next-button", handleNext);
    bindClick("home-button", () => navigateTo("index.html"));

    bindClick("mac-assign", handleMacAssign);
    bindClick("mac-prev", handlePrevious);
    bindClick("mac-next", handleNext);

    const verifyCheckbox = document.getElementById("verify-confirm");
    if (verifyCheckbox) {
        verifyCheckbox.addEventListener("change", handleVerifyChange);
    }
    bindClick("verification-prev", handlePrevious);
    bindClick("verification-next", handleNext);

    bindClick("serial-prev", handlePrevious);
    bindClick("serial-finish", handleFinish);

    bindClick("reset-device-toggle", handleResetDeviceToggle);
}

/* ---------- Reset Device (static, not part of the standard workflow) ---------- */

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
    if (instructionsEl) {
        instructionsEl.textContent = result.instructions;
    }

    const stepsEl = document.getElementById("reset-device-steps");
    if (!stepsEl) return;

    stepsEl.innerHTML = ""

    result.steps.forEach((step, index) => {
        const stepEl = document.createElement("div");
        stepEl.className = "reset-device-step";

        const commandEl = document.createElement("p");
        commandEl.className = "reset-device-step-command";
        commandEl.textContent = `${index + 1}. ${step.command}`;

        const imageEl = document.createElement("img")
        imageEl.className = "qr-image";
        imageEl.src = step.qr_url;
        imageEl.alt = `QR Code for ${step.command}`;

        stepEl.appendChild(commandEl);
        stepEl.appendChild(imageEl);
        stepsEl.appendChild(stepsEl);
    })
}}


/* ---------- Phase derivation & shared rendering ---------- */

function derivePhase(session) {
    if (!session) return "order";
    if (session.completed) return "serial";
    if (session.current_step <= 3) return "qr";
    if (session.current_step === 4) return "mac";
    return "verification";
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
        // Stage tabs are a progress readout, not a navigation shortcut —
        // moving between phases goes through Previous/Next so session
        // state (created order, assigned MAC) always stays consistent.
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

function render(step) {
    const phase = derivePhase(currentSession);

    renderStageNav(phase);
    showPhase(phase);
    updateHeaderOperator(currentSession ? currentSession.operator : "");

    if (phase === "qr" && step) {
        renderQrStep(step);
    } else if (phase === "mac" && step) {
        renderMacPhase(step);
    } else if (phase === "verification" && step) {
        renderVerificationPhase(step);
    } else if (phase === "serial") {
        renderSerialPhase();
    }
}

/* ---------- Shared step navigation (qr / mac / verification phases) ---------- */

async function handlePrevious() {
    try {
        const result = await api.previousStep();
        currentSession = result.session;
        saveSession(currentSession);
        render(result.step);
    } catch (error) {
        console.error("Unable to go to previous step:", error);
    }
}

async function handleNext() {
    try {
        const result = await api.nextStep();
        currentSession = result.session;
        saveSession(currentSession);
        render(result.step);
    } catch (error) {
        console.error("Unable to advance workflow:", error);
    }
}

/* ---------- Phase 0: Order & Operator ---------- */

async function handleOrderOperatorContinue() {
    const orderInput = document.getElementById("order-input");
    const operatorInput = document.getElementById("operator-input");
    const order = orderInput.value.trim();
    const operator = operatorInput.value.trim();

    if (!order) {
        orderInput.focus();
        return;
    }
    if (!operator) {
        operatorInput.focus();
        return;
    }

    try {
        const result = await api.startSession({ order_number: order, operator });
        currentSession = result.session;
        saveSession(currentSession);
        render(result.step);
    } catch (error) {
        console.error("Unable to start session:", error);
        alert(error.message || "Unable to start a new test session.");
    }
}

/* ---------- Phase 1: Test QR Codes (steps 1–4) ---------- */

function renderQrStep(step) {
    const workflowName = document.getElementById("workflow-name");
    const stepIndicator = document.getElementById("step-indicator");
    const commandEl = document.getElementById("current-command");
    const qrImage = document.getElementById("qr-image");
    const previousButton = document.getElementById("previous-button");
    const nextButton = document.getElementById("next-button");

    if (workflowName) {
        workflowName.textContent = step.workflow_name;
    }

    if (stepIndicator) {
        stepIndicator.textContent = `Step ${step.step_number} of 4 — ${step.step_name}`;
    }

    if (commandEl) {
        commandEl.textContent = step.command;
    }

    if (qrImage) {
        qrImage.src = step.qr_url;
        qrImage.alt = `QR Code for ${step.step_name}`;
    }

    if (previousButton) {
        previousButton.disabled = step.step_index === 0;
    }

    if (nextButton) {
        nextButton.textContent = "Next";
        nextButton.disabled = false;
    }
}

/* ---------- Phase 2: MAC Addresses (step 5) ---------- */

function nextMacFromPool(mac) {
    // Placeholder pool assignment for the mock API — the real backend
    // reserves the next available MAC from the order's allocated pool.
    const parts = mac.split(":");
    if (parts.length !== 6) return mac;

    const last = parseInt(parts[5], 16);
    if (Number.isNaN(last)) return mac;

    parts[5] = ((last + 1) % 256).toString(16).padStart(2, "0").toUpperCase();
    return parts.join(":");
}

function renderMacPhase(step) {
    const mac1Input = document.getElementById("mac1-input");
    const nextButton = document.getElementById("mac-next");

    if (currentSession.mac1 && currentSession.mac2) {
        if (mac1Input) mac1Input.value = currentSession.mac1;
        showMacResult(step);
        if (nextButton) nextButton.disabled = false;
    } else {
        if (mac1Input) mac1Input.value = "";
        setVisible("mac-result", false);
        if (nextButton) nextButton.disabled = true;
    }
}

function showMacResult(step) {
    document.getElementById("mac1-value").textContent = currentSession.mac1;
    document.getElementById("mac2-value").textContent = currentSession.mac2;
    document.getElementById("mac-command").textContent = step.command;

    const qrImage = document.getElementById("mac-qr-image");
    qrImage.src = step.qr_url;
    qrImage.alt = "QR Code for MAC Addresses";

    setVisible("mac-result", true);
}

async function handleMacAssign() {
    const mac1Input = document.getElementById("mac1-input");
    const mac1 = mac1Input.value.trim();

    if (!mac1) {
        mac1Input.focus();
        return;
    }

    const mac2 = nextMacFromPool(mac1);

    try {
        const result = await api.setMacAddresses(mac1, mac2);
        currentSession = result.session;
        saveSession(currentSession);
        showMacResult(result.step);
        document.getElementById("mac-next").disabled = false;
    } catch (error) {
        console.error("Unable to assign MAC addresses:", error);
        alert(error.message || "Unable to assign MAC addresses.");
    }
}

/* ---------- Phase 3: Verification (step 6) ---------- */

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

/* ---------- Phase 4: Serial Number ---------- */

function renderSerialPhase() {
    document.getElementById("finish-order").textContent = currentSession.order_number || "—";
    document.getElementById("finish-mac1").textContent = currentSession.mac1 || "—";
    document.getElementById("finish-mac2").textContent = currentSession.mac2 || "—";
    document.getElementById("serial-input").value = "";
    document.getElementById("repeat-banner").classList.remove("is-visible");
    document.getElementById("serial-finish").disabled = false;
    document.getElementById("serial-prev").disabled = false;
}

async function handleFinish() {
    const serialInput = document.getElementById("serial-input");
    const serial = serialInput.value.trim();

    if (!serial) {
        serialInput.focus();
        return;
    }

    if (!isValidSerialNumber(serial)) {
        alert("Serial number must be formatted as EMyyyyww0000.");
        serialInput.focus();
        return;
    }

    try {
        await api.finishSession(serial)
    } catch (error) {
        console.error("Unable to save device:", error);
        alert(error.message || "Unable to save this device.");
        return;
    }

    document.getElementById("finish-serial").textContent = result.serial_number || "-";
    document.getElementById("repeat-banner").classList.add("is-visible");
    document.getElementById("serial-finish").disabled = true;
    document.getElementById("serial-prev").disabled = true;

    setTimeout(startNextUnit, 1400);
}

async function startNextUnit() {
    const order = currentSession.order_number;
    const operator = currentSession.operator;
    clearSession();

    try {
        const result = await api.startSession({ order_number: order, operator });
        currentSession = result.session;
        saveSession(currentSession);
        render(result.step);
    } catch (error) {
        console.error("Unable to start the next unit:", error);
        currentSession = null;
        render(null);
    }
}