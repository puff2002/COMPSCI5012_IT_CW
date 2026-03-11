import { createHistory, deleteHistory, getHistory, updateHistory } from "../api.js";
import { requireAuth } from "../auth.js";
import { formatDate, html, requireElement, text, toggleDisabled } from "../ui.js";
import type { OutfitHistory } from "../types.js";

let historyItems: OutfitHistory[] = [];

function setActiveNav(): void {
  const current = window.location.pathname.split("/").pop() ?? "history.html";
  document.querySelectorAll<HTMLAnchorElement>(".app-nav-link").forEach((link) => {
    if ((link.getAttribute("href") ?? "").endsWith(current)) {
      link.classList.add("active");
      link.setAttribute("aria-current", "page");
    }
  });
}

function renderHistory(): void {
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
        <p>Top: ${top}</p>
        <p>Bottom: ${bottom}</p>
        <p>Shoes: ${shoes}</p>
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

async function loadHistory(): Promise<void> {
  text("#historyStatus", "Loading history...");
  try {
    historyItems = await getHistory();
    renderHistory();
    text("#historyStatus", `${historyItems.length} entry(ies) loaded.`);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Failed to load history.";
    text("#historyStatus", message);
  }
}

async function submitForm(event: SubmitEvent): Promise<void> {
  event.preventDefault();

  const idValue = requireElement<HTMLInputElement>("#historyId").value.trim();
  const outfitValue = requireElement<HTMLInputElement>("#historyOutfitId").value.trim();
  const ratingValue = requireElement<HTMLInputElement>("#historyRating").value.trim();
  const feedback = requireElement<HTMLInputElement>("#historyFeedback").value.trim();

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
    } else {
      const outfitId = Number(outfitValue);
      if (Number.isNaN(outfitId)) {
        throw new Error("Outfit ID is required for manual history create.");
      }
      await createHistory(outfitId, rating, feedback);
    }
    requireElement<HTMLFormElement>("#historyForm").reset();
    await loadHistory();
  } catch (error) {
    const message = error instanceof Error ? error.message : "Failed to save history.";
    text("#historyError", message);
  } finally {
    toggleDisabled("#historySubmit", false);
  }
}

async function onListClick(event: Event): Promise<void> {
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
    requireElement<HTMLInputElement>("#historyId").value = String(entry.id);
    requireElement<HTMLInputElement>("#historyOutfitId").value = String(entry.outfit);
    requireElement<HTMLInputElement>("#historyRating").value = entry.rating ? String(entry.rating) : "";
    requireElement<HTMLInputElement>("#historyFeedback").value = entry.feedback;
    text("#historyMode", `Editing entry #${entry.id}`);
  }
}

function resetEditor(): void {
  requireElement<HTMLFormElement>("#historyForm").reset();
  text("#historyMode", "Create / Update History Entry");
}

function init(): void {
  requireAuth();
  setActiveNav();
  requireElement<HTMLFormElement>("#historyForm").addEventListener("submit", (event) => {
    void submitForm(event as SubmitEvent);
  });
  requireElement<HTMLElement>("#historyList").addEventListener("click", (event) => {
    void onListClick(event);
  });
  requireElement<HTMLButtonElement>("#historyReset").addEventListener("click", () => resetEditor());
  void loadHistory();
}

init();
