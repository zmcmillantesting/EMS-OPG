/**
 * History page — search and display device records.
 */

document.addEventListener("DOMContentLoaded", async () => {
    await initPage();
    bindHistoryActions();
    await loadHistory("");
});

function bindHistoryActions() {
    bindClick("search-button", () => {
        const query = document.getElementById("search")?.value || "";
        loadHistory(query);
    });

    const searchInput = document.getElementById("search");
    if (searchInput) {
        searchInput.addEventListener("keydown", (event) => {
            if (event.key === "Enter") {
                loadHistory(searchInput.value);
            }
        });
    }

    bindClick("export-button", exportHistory);
}

async function loadHistory(query) {
    const tbody = document.getElementById("history-body");
    const emptyMessage = document.getElementById("history-empty");

    if (!tbody) {
        return;
    }

    try {
        const result = await api.getHistory(query);
        renderHistoryTable(result.records);

        if (emptyMessage) {
            emptyMessage.classList.toggle("hidden", result.records.length > 0);
        }
    } catch (error) {
        console.error("Unable to load history:", error);
        tbody.innerHTML = "";
        if (emptyMessage) {
            emptyMessage.classList.remove("hidden");
            emptyMessage.textContent = "Unable to load history records.";
        }
    }
}

function renderHistoryTable(records) {
    const tbody = document.getElementById("history-body");
    if (!tbody) {
        return;
    }

    tbody.innerHTML = records
        .map(
            (record) => `
            <tr>
                <td>${formatDate(record.timestamp)}</td>
                <td>${escapeHtml(record.order_number)}</td>
                <td>${escapeHtml(record.serial_number)}</td>
                <td class="mono">${escapeHtml(record.ethaddr_id)}</td>
                <td class="mono">${escapeHtml(record.ethaddr1_id || "—")}</td>
                <td>${escapeHtml(record.operator)}</td>
                <td class="${record.test_result === "PASS" ? "result-pass" : "result-fail"}">${escapeHtml(record.test_result)}</td>
                <td>${record.used ? "Used" : "Available"}</td>
            </tr>
        `
        )
        .join("");
}

async function exportHistory() {
    try {
        const result = await api.exportHistory();
        downloadCsv(result.csv, result.filename);
    } catch (error) {
        console.error("Unable to export history:", error);
        alert("Unable to export history.");
    }
}

function downloadCsv(content, filename) {
    const blob = new Blob([content], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
    URL.revokeObjectURL(link.href);
}

function escapeHtml(value) {
    const div = document.createElement("div");
    div.textContent = value ?? "";
    return div.innerHTML;
}
