import { createHistory, deleteHistory, getHistory, updateHistory } from "../api.js";
import { requireAuth } from "../auth.js";
import { formatDate, html, requireElement, text, toggleDisabled } from "../ui.js";
let historyItems = [];
function setActiveNav() {
    const current = window.location.pathname.split("/").pop() ?? "history.html";
    document.querySelectorAll(".app-nav-link").forEach((link) => {
        if ((link.getAttribute("href") ?? "").endsWith(current)) {
            link.classList.add("active");
            link.setAttribute("aria-current", "page");
        }
    });
}
function renderHistory() {
    if (historyItems.length === 0) {
        html("#historyList", "<p class=\"empty-panel\">No history entries yet.</p>");
        return;
    }
    const blocks = historyItems.map((entry) => {
        const top = entry.outfit_detail.top_detail?.item ?? "None";
        const bottom = entry.outfit_detail.bottom_detail?.item ?? "None";
        const shoes = entry.outfit_detail.shoes_detail?.item ?? "None";
        return `
      <article class="history-card">
        <header>
          <h3>History #${entry.id}</h3>
          <p>${formatDate(entry.created_at)}</p>
        </header>
        <p>Top: ${top} | Bottom: ${bottom} | Shoes: ${shoes}</p>
        <p>Rating: ${entry.rating ?? "Not rated"}</p>
        <p>Feedback: ${entry.feedback || "No feedback"}</p>
        <div class="item-actions">
          <button class="btn btn-secondary" data-action="load-edit" data-id="${entry.id}">Edit</button>
          <button class="btn btn-danger" data-action="delete" data-id="${entry.id}">Delete</button>
        </div>
      </article>
    `;
    }).join("");
    html("#historyList", blocks);
}
async function loadHistory() {
    text("#historyStatus", "Loading history...");
    try {
        historyItems = await getHistory();
        renderHistory();
        text("#historyStatus", `${historyItems.length} entry(ies) loaded.`);
    }
    catch (error) {
        const message = error instanceof Error ? error.message : "Failed to load history.";
        text("#historyStatus", message);
    }
}
async function submitForm(event) {
    event.preventDefault();
    const idValue = requireElement("#historyId").value.trim();
    const outfitValue = requireElement("#historyOutfitId").value.trim();
    const ratingValue = requireElement("#historyRating").value.trim();
    const feedback = requireElement("#historyFeedback").value.trim();
    const rating = ratingValue ? Number(ratingValue) : null;
    if (rating !== null && (Number.isNaN(rating) || rating < 1 || rating > 5)) {
        text("#historyError", "Rating must be 1-5.");
        return;
    }
    toggleDisabled("#historySubmit", true);
    text("#historyError", "");
    try {
        if (idValue) {
            await updateHistory(Number(idValue), rating, feedback);
        }
        else {
            const outfitId = Number(outfitValue);
            if (Number.isNaN(outfitId)) {
                throw new Error("Outfit ID is required for manual history create.");
            }
            await createHistory(outfitId, rating, feedback);
        }
        requireElement("#historyForm").reset();
        await loadHistory();
    }
    catch (error) {
        const message = error instanceof Error ? error.message : "Failed to save history.";
        text("#historyError", message);
    }
    finally {
        toggleDisabled("#historySubmit", false);
    }
}
async function onListClick(event) {
    const target = event.target;
    if (!(target instanceof HTMLElement)) {
        return;
    }
    const action = target.dataset.action;
    const idText = target.dataset.id;
    const id = idText ? Number(idText) : NaN;
    if (!action || Number.isNaN(id)) {
        return;
    }
    if (action === "delete") {
        if (!window.confirm("Delete this history entry?")) {
            return;
        }
        await deleteHistory(id);
        await loadHistory();
        return;
    }
    if (action === "load-edit") {
        const entry = historyItems.find((item) => item.id === id);
        if (!entry) {
            return;
        }
        requireElement("#historyId").value = String(entry.id);
        requireElement("#historyOutfitId").value = String(entry.outfit);
        requireElement("#historyRating").value = entry.rating ? String(entry.rating) : "";
        requireElement("#historyFeedback").value = entry.feedback;
        text("#historyMode", `Editing entry #${entry.id}`);
    }
}
function resetEditor() {
    requireElement("#historyForm").reset();
    text("#historyMode", "Create / Update History Entry");
}
function init() {
    requireAuth();
    setActiveNav();
    requireElement("#historyForm").addEventListener("submit", (event) => {
        void submitForm(event);
    });
    requireElement("#historyList").addEventListener("click", (event) => {
        void onListClick(event);
    });
    requireElement("#historyReset").addEventListener("click", () => resetEditor());
    void loadHistory();
}
init();
