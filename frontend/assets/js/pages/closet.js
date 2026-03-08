import { createClosetItem, deleteClosetItem, getClosetItems, updateClosetItem, uploadClosetImage } from "../api.js";
import { requireAuth } from "../auth.js";
import { badge, formatDate, html, requireElement, text, toggleDisabled } from "../ui.js";
let items = [];
let editingId = null;
function setActiveNav() {
    const current = window.location.pathname.split("/").pop() ?? "closet.html";
    document.querySelectorAll(".app-nav-link").forEach((link) => {
        if ((link.getAttribute("href") ?? "").endsWith(current)) {
            link.classList.add("active");
            link.setAttribute("aria-current", "page");
        }
    });
}
function normalizeCategory(raw) {
    if (raw === "top" || raw === "bottom" || raw === "shoes") {
        return raw;
    }
    return null;
}
function parseTags(value) {
    return value.split(",").map((entry) => entry.trim()).filter((entry) => entry.length > 0);
}
function renderList() {
    const query = requireElement("#filterText").value.trim().toLowerCase();
    const category = requireElement("#filterCategory").value;
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
async function loadItems() {
    text("#closetStatus", "Loading items...");
    try {
        items = await getClosetItems();
        renderList();
        text("#closetStatus", `${items.length} item(s) loaded.`);
    }
    catch (error) {
        const message = error instanceof Error ? error.message : "Failed to load items.";
        text("#closetStatus", message);
    }
}
function resetForm() {
    editingId = null;
    requireElement("#itemForm").reset();
    text("#itemFormTitle", "Add New Item");
    text("#itemError", "");
}
async function submitItem(event) {
    event.preventDefault();
    const categoryValue = requireElement("#itemCategory").value;
    const category = normalizeCategory(categoryValue);
    if (!category) {
        text("#itemError", "Category must be top, bottom, or shoes.");
        return;
    }
    const payload = {
        category,
        item: requireElement("#itemName").value.trim(),
        style_semantics: parseTags(requireElement("#itemStyle").value),
        season_semantics: parseTags(requireElement("#itemSeason").value),
        usage_semantics: parseTags(requireElement("#itemUsage").value),
        color_semantics: requireElement("#itemColor").value.trim(),
        description: requireElement("#itemDescription").value.trim()
    };
    toggleDisabled("#itemSubmit", true);
    text("#itemError", "");
    try {
        if (editingId) {
            await updateClosetItem(editingId, payload);
        }
        else {
            await createClosetItem(payload);
        }
        await loadItems();
        resetForm();
    }
    catch (error) {
        const message = error instanceof Error ? error.message : "Failed to save item.";
        text("#itemError", message);
    }
    finally {
        toggleDisabled("#itemSubmit", false);
    }
}
async function onGridClick(event) {
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
        }
        catch (error) {
            const message = error instanceof Error ? error.message : "Delete failed.";
            text("#closetStatus", message);
        }
    }
    if (action === "edit") {
        const existing = items.find((item) => item.id === id);
        if (!existing) {
            return;
        }
        editingId = id;
        text("#itemFormTitle", `Edit Item #${id}`);
        requireElement("#itemCategory").value = existing.category;
        requireElement("#itemName").value = existing.item;
        requireElement("#itemStyle").value = existing.style_semantics.join(", ");
        requireElement("#itemSeason").value = existing.season_semantics.join(", ");
        requireElement("#itemUsage").value = existing.usage_semantics.join(", ");
        requireElement("#itemColor").value = existing.color_semantics;
        requireElement("#itemDescription").value = existing.description;
        window.scrollTo({ top: 0, behavior: "smooth" });
    }
}
async function uploadImage(event) {
    event.preventDefault();
    const input = requireElement("#itemImage");
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
        await uploadClosetImage(file);
        await loadItems();
        requireElement("#uploadForm").reset();
        text("#uploadStatus", "Upload successful.");
    }
    catch (error) {
        const message = error instanceof Error ? error.message : "Upload failed.";
        text("#uploadStatus", `${message} Use manual form instead.`);
    }
    finally {
        toggleDisabled("#uploadBtn", false);
    }
}
function init() {
    requireAuth();
    setActiveNav();
    requireElement("#itemForm").addEventListener("submit", (event) => {
        void submitItem(event);
    });
    requireElement("#itemReset").addEventListener("click", () => resetForm());
    requireElement("#uploadForm").addEventListener("submit", (event) => {
        void uploadImage(event);
    });
    requireElement("#itemsGrid").addEventListener("click", (event) => {
        void onGridClick(event);
    });
    requireElement("#filterText").addEventListener("input", () => renderList());
    requireElement("#filterCategory").addEventListener("change", () => renderList());
    void loadItems();
}
init();
