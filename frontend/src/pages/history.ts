import { createHistory, deleteHistory, getHistory, updateHistory } from "../api.js";
import { requireAuth } from "../auth.js";
import { formatDate, html, initMobileSidebar, requireElement, text, toggleDisabled } from "../ui.js";
import type { ClothingItem, OutfitHistory } from "../types.js";

let historyItems: OutfitHistory[] = [];
const PLACEHOLDER_IMAGE = "./assets/img/placeholder-item.svg";

function setActiveNav(): void {
  const current = window.location.pathname.split("/").pop() ?? "history.html";
  document.querySelectorAll<HTMLAnchorElement>(".app-nav-link").forEach((link) => {
    if ((link.getAttribute("href") ?? "").endsWith(current)) {
      link.classList.add("active");
      link.setAttribute("aria-current", "page");
    }
  });
}

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function renderStars(rating: number | null): string {
  if (!rating) {
    return "<span class=\"history-rating-empty\">Not rated</span>";
  }

  return Array.from({ length: 5 }, (_, index) => {
    const filled = index < rating;
    return `<span class="history-star${filled ? " is-filled" : ""}" aria-hidden="true">${filled ? "★" : "☆"}</span>`;
  }).join("");
}

function renderPiece(label: string, item: ClothingItem | null): string {
  const name = item?.item ?? "Not included";
  const description = item?.description?.trim() || "No saved notes for this item.";
  const image = item?.image_url || PLACEHOLDER_IMAGE;

  return `
    <article class="history-piece">
      <div class="history-piece-media">
        <img src="${escapeHtml(image)}" alt="${escapeHtml(name)}" loading="lazy" width="160" height="160">
      </div>
      <div class="history-piece-body">
        <p class="history-piece-label">${escapeHtml(label)}</p>
        <h4>${escapeHtml(name)}</h4>
        <p>${escapeHtml(description)}</p>
      </div>
    </article>
  `;
}

function renderHistory(): void {
  if (historyItems.length === 0) {
    html("#historyList", "<p class=\"empty-panel\">No history entries yet.</p>");
    return;
  }

  const blocks = historyItems.map((entry) => {
    const feedback = entry.feedback.trim() || "No feedback recorded.";
    const recommendation = entry.outfit_detail.recommendation_text.trim() || "No recommendation summary saved.";

    return `
      <article class="history-card">
        <header class="history-card-header">
          <div>
            <p class="eyebrow">Entry #${entry.id}</p>
            <h3>Outfit record</h3>
          </div>
          <div class="history-card-date">
            <span>Saved</span>
            <strong>${escapeHtml(formatDate(entry.created_at))}</strong>
          </div>
        </header>
        <section class="history-piece-grid" aria-label="Outfit items for history entry ${entry.id}">
          ${renderPiece("Top", entry.outfit_detail.top_detail)}
          ${renderPiece("Bottom", entry.outfit_detail.bottom_detail)}
          ${renderPiece("Shoes", entry.outfit_detail.shoes_detail)}
        </section>
        <dl class="history-meta">
          <div>
            <dt>Rating</dt>
            <dd class="history-rating" aria-label="${entry.rating ? `${entry.rating} out of 5 stars` : "Not rated"}">${renderStars(entry.rating)}</dd>
          </div>
          <div>
            <dt>Outfit ID</dt>
            <dd>#${entry.outfit}</dd>
          </div>
        </dl>
        <div class="history-note-grid">
          <section class="history-note-card">
            <p class="history-note-label">Recommendation</p>
            <p>${escapeHtml(recommendation)}</p>
          </section>
          <section class="history-note-card">
            <p class="history-note-label">Feedback</p>
            <p>${escapeHtml(feedback)}</p>
          </section>
        </div>
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
    historyItems.sort((left, right) => new Date(right.created_at).getTime() - new Date(left.created_at).getTime());
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
  initMobileSidebar();
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
