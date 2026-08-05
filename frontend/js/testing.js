/**
 * Testing page — workflow navigation, QR display, and command display.
 */

let currentSession = null;

document.addEventListener("DOMContentLoaded", async () => {
    await initPage();
    await loadTestingComponents();
    bindTestingActions();

    currentSession = loadSession();

    if (!currentSession) {
        try {
            const result = await api.startSession({
                operator: "Operator",
                order_number: "123456",
                serial_number: "SN001",
                mac1: "00:60:47:12:34:01",
                mac2: "00:60:47:12:34:02",
            });
            currentSession = result.session;
            saveSession(currentSession);
            renderWorkflow(result);
        } catch (error) {
            console.error("Unable to initialize workflow:", error);
            return;
        }
    } else {
        try {
            const result = await api.getWorkflow();
            currentSession = result.session;
            saveSession(currentSession);
            renderWorkflow(result);
        } catch (error) {
            console.error("Unable to load workflow:", error);
        }
    }
});

function bindTestingActions() {
    bindClick("previous-button", handlePrevious);
    bindClick("next-button", handleNext);
    bindClick("home-button", () => navigateTo("index.html"));
}

async function handlePrevious() {
    try {
        const result = await api.previousStep();
        currentSession = result.session;
        saveSession(currentSession);
        renderWorkflow(result);
    } catch (error) {
        console.error("Unable to go to previous step:", error);
    }
}

async function handleNext() {
    try {
        const result = await api.nextStep();
        currentSession = result.session;
        saveSession(currentSession);
        renderWorkflow(result);

        if (currentSession.completed) {
            clearSession();
            setTimeout(() => navigateTo("index.html"), 1500);
        }
    } catch (error) {
        console.error("Unable to advance workflow:", error);
    }
}

function renderWorkflow(result) {
    const { session, step } = result;

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
        stepIndicator.textContent = `Step ${step.step_number} of ${step.total_steps} — ${step.step_name}`;
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
        if (session.completed) {
            nextButton.textContent = "Complete";
            nextButton.disabled = true;
        } else if (step.step_index === step.total_steps - 1) {
            nextButton.textContent = "Finish";
        } else {
            nextButton.textContent = "Next";
            nextButton.disabled = false;
        }
    }
}
