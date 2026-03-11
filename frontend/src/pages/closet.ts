import { createClosetItem, deleteClosetItem, getClosetItems, updateClosetItem, uploadClosetImage } from "../api.js";
import { requireAuth } from "../auth.js";
import { normalizeImageFile } from "../image.js";
import { badge, formatDate, html, initMobileSidebar, requireElement, text, toggleDisabled } from "../ui.js";
import type { Category, ClothingAnalysis, ClothingItem } from "../types.js";

let items: ClothingItem[] = [];
let editingId: number | null = null;
let uploadedImageFile: File | null = null;

function setActiveNav(): void {
  const current = window.location.pathname.split("/").pop() ?? "closet.html";
  document.querySelectorAll<HTMLAnchorElement>(".app-nav-link").forEach((link) => {
    if ((link.getAttribute("href") ?? "").endsWith(current)) {
      link.classList.add("active");
      link.setAttribute("aria-current", "page");
    }
  });
}

function normalizeCategory(raw: string): Category | null {
  if (raw === "top" || raw === "bottom" || raw === "shoes") {
    return raw;
  }
  return null;
}

function parseTags(value: string): string[] {
  return value.split(",").map((entry) => entry.trim()).filter((entry) => entry.length > 0);
}

function setComposerVisible(visible: boolean): void {
  const composer = requireElement<HTMLElement>("#closetComposer");
  const toggleButton = requireElement<HTMLButtonElement>("#toggleComposerBtn");
  composer.classList.toggle("is-hidden", !visible);
  composer.setAttribute("aria-hidden", String(!visible));
  toggleButton.setAttribute("aria-expanded", String(visible));
  toggleButton.textContent = visible ? "Close" : "Add Item";
  if (visible) {
    composer.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

function setDetailsCardVisible(visible: boolean): void {
  const detailsCard = requireElement<HTMLElement>("#itemDetailsCard");
  detailsCard.classList.toggle("is-hidden", !visible);
  detailsCard.setAttribute("aria-hidden", String(!visible));
}

function applyAnalysisToForm(analysis: ClothingAnalysis): void {
  requireElement<HTMLSelectElement>("#itemCategory").value = analysis.category;
  requireElement<HTMLInputElement>("#itemName").value = analysis.item;
  requireElement<HTMLInputElement>("#itemStyle").value = analysis.style_semantics.join(", ");
  requireElement<HTMLInputElement>("#itemSeason").value = analysis.season_semantics.join(", ");
  requireElement<HTMLInputElement>("#itemUsage").value = analysis.usage_semantics.join(", ");
  requireElement<HTMLInputElement>("#itemColor").value = analysis.color_semantics;
  requireElement<HTMLInputElement>("#itemDescription").value = analysis.description;
}

function renderList(): void {
  const query = requireElement<HTMLInputElement>("#filterText").value.trim().toLowerCase();
  const category = requireElement<HTMLSelectElement>("#filterCategory").value;

  const filtered = items.filter((item) => {
    const matchesQuery = query.length === 0 || item.item.toLowerCase().includes(query) || item.description.toLowerCase().includes(query);
    const matchesCategory = category.length === 0 || item.category === category;
    return matchesQuery && matchesCategory;
  });

  if (filtered.length === 0) {
    html("#itemsGrid", "<p class=\"empty-panel\">No items found.</p>");
    return;
  }

  const cards = filtered.map((item) => {
    const image = item.image_url || "./assets/img/placeholder-item.svg";
    return `
      <article class="item-card">
        <img src="${image}" alt="${item.item}" loading="lazy" width="240" height="240">
        <div class="item-card-body">
          <h3>${item.item}</h3>
          <p>${item.description || "No description"}</p>
          <p>${badge(item.category)} ${badge(item.color_semantics || "unknown", "warn")}</p>
          <p class="muted">${formatDate(item.created_at)}</p>
          <div class="item-actions">
            <button class="btn btn-secondary" data-action="edit" data-id="${item.id}">Edit</button>
            <button class="btn btn-danger" data-action="delete" data-id="${item.id}">Delete</button>
          </div>
        </div>
      </article>
    `;
  }).join("");

  html("#itemsGrid", cards);
}

async function loadItems(): Promise<void> {
  text("#closetStatus", "Loading items...");
  try {
    items = await getClosetItems();
    renderList();
    text("#closetStatus", `${items.length} item(s) loaded.`);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Failed to load items.";
    text("#closetStatus", message);
  }
}

function resetForm(): void {
  editingId = null;
  uploadedImageFile = null;
  requireElement<HTMLFormElement>("#itemForm").reset();
  requireElement<HTMLFormElement>("#uploadForm").reset();
  text("#itemFormTitle", "Add New Item");
  text("#itemError", "");
  text("#uploadStatus", "");
  text("#itemImageStatus", "");
  setDetailsCardVisible(false);
}

async function submitItem(event: SubmitEvent): Promise<void> {
  event.preventDefault();
  const categoryValue = requireElement<HTMLSelectElement>("#itemCategory").value;
  const category = normalizeCategory(categoryValue);

  if (!category) {
    text("#itemError", "Category must be top, bottom, or shoes.");
    return;
  }

  const basePayload = {
    category,
    item: requireElement<HTMLInputElement>("#itemName").value.trim(),
    style_semantics: parseTags(requireElement<HTMLInputElement>("#itemStyle").value),
    season_semantics: parseTags(requireElement<HTMLInputElement>("#itemSeason").value),
    usage_semantics: parseTags(requireElement<HTMLInputElement>("#itemUsage").value),
    color_semantics: requireElement<HTMLInputElement>("#itemColor").value.trim(),
    description: requireElement<HTMLInputElement>("#itemDescription").value.trim()
  };

  toggleDisabled("#itemSubmit", true);
  text("#itemError", "");

  try {
    if (editingId) {
      await updateClosetItem(editingId, basePayload);
    } else {
      await createClosetItem(uploadedImageFile ? { ...basePayload, image: uploadedImageFile } : basePayload);
    }
    await loadItems();
    resetForm();
    setComposerVisible(false);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Failed to save item.";
    text("#itemError", message);
  } finally {
    toggleDisabled("#itemSubmit", false);
  }
}

async function onGridClick(event: Event): Promise<void> {
  const target = event.target;
  if (!(target instanceof HTMLElement)) {
    return;
  }
  const action = target.dataset.action;
  const idValue = target.dataset.id;
  const id = idValue ? Number(idValue) : NaN;
  if (!action || Number.isNaN(id)) {
    return;
  }

  if (action === "delete") {
    const confirmed = window.confirm("Delete this item?");
    if (!confirmed) {
      return;
    }
    try {
      await deleteClosetItem(id);
      await loadItems();
    } catch (error) {
      const message = error instanceof Error ? error.message : "Delete failed.";
      text("#closetStatus", message);
    }
  }

  if (action === "edit") {
    const existing = items.find((item) => item.id === id);
    if (!existing) {
      return;
    }
    setComposerVisible(true);
    editingId = id;
    uploadedImageFile = null;
    setDetailsCardVisible(true);
    text("#itemFormTitle", `Edit Item #${id}`);
    requireElement<HTMLSelectElement>("#itemCategory").value = existing.category;
    requireElement<HTMLInputElement>("#itemName").value = existing.item;
    requireElement<HTMLInputElement>("#itemStyle").value = existing.style_semantics.join(", ");
    requireElement<HTMLInputElement>("#itemSeason").value = existing.season_semantics.join(", ");
    requireElement<HTMLInputElement>("#itemUsage").value = existing.usage_semantics.join(", ");
    requireElement<HTMLInputElement>("#itemColor").value = existing.color_semantics;
    requireElement<HTMLInputElement>("#itemDescription").value = existing.description;
    text("#itemImageStatus", existing.image_url ? "Using the saved item data. Upload a photo only if you want to analyze a new item draft." : "");
    text("#uploadStatus", "");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
}

async function uploadImage(event: SubmitEvent): Promise<void> {
  event.preventDefault();
  const input = requireElement<HTMLInputElement>("#itemImage");
  const file = input.files?.[0];
  if (!file) {
    text("#uploadStatus", "Please choose an image.");
    return;
  }
  if (!file.type.startsWith("image/")) {
    text("#uploadStatus", "Only image files are supported.");
    return;
  }
  if (file.size > 5 * 1024 * 1024) {
    text("#uploadStatus", "File too large. Max 5MB.");
    return;
  }

  toggleDisabled("#uploadBtn", true);
  text("#uploadStatus", "Uploading and analyzing...");
  try {
    const normalizedFile = await normalizeImageFile(file);
    const analysis = await uploadClosetImage(normalizedFile);
    editingId = null;
    uploadedImageFile = normalizedFile;
    setComposerVisible(true);
    setDetailsCardVisible(true);
    text("#itemFormTitle", "Add New Item");
    applyAnalysisToForm(analysis);
    text("#itemImageStatus", `Image ready to save: ${normalizedFile.name}`);
    text("#uploadStatus", "Analysis complete. Review the fields and save when ready.");
  } catch (error) {
    const message = error instanceof Error ? error.message : "Upload failed.";
    if (message === "No clothing item detected in the image") {
      text("#uploadStatus", "Recognition failed: no clothing item was detected. Use the manual form instead.");
    } else {
      text("#uploadStatus", `${message} Use manual form instead.`);
    }
  } finally {
    toggleDisabled("#uploadBtn", false);
  }
}

function init(): void {
  requireAuth();
  setActiveNav();
  initMobileSidebar();
  setComposerVisible(false);
  setDetailsCardVisible(false);

  requireElement<HTMLFormElement>("#itemForm").addEventListener("submit", (event) => {
    void submitItem(event as SubmitEvent);
  });
  requireElement<HTMLButtonElement>("#itemReset").addEventListener("click", () => {
    resetForm();
    setComposerVisible(false);
  });
  requireElement<HTMLButtonElement>("#toggleComposerBtn").addEventListener("click", () => {
    const isHidden = requireElement<HTMLElement>("#closetComposer").classList.contains("is-hidden");
    setComposerVisible(isHidden);
    if (isHidden) {
      resetForm();
      text("#uploadStatus", "Upload a clothing image to auto-fill the details card.");
    } else {
      resetForm();
    }
  });
  requireElement<HTMLFormElement>("#uploadForm").addEventListener("submit", (event) => {
    void uploadImage(event as SubmitEvent);
  });
  requireElement<HTMLElement>("#itemsGrid").addEventListener("click", (event) => {
    void onGridClick(event);
  });
  requireElement<HTMLInputElement>("#filterText").addEventListener("input", () => renderList());
  requireElement<HTMLSelectElement>("#filterCategory").addEventListener("change", () => renderList());

  void loadItems();
}

init();
