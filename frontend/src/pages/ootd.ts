import { recommend } from "../api.js";
import { requireAuth } from "../auth.js";
import { badge, formatDate, html, initMobileSidebar, requireElement, text, toggleDisabled } from "../ui.js";
import type { ClothingItem, RecommendationResponse } from "../types.js";

const PLACEHOLDER_IMAGE = "./assets/img/placeholder-item.svg";

function setActiveNav(): void {
  const current = window.location.pathname.split("/").pop() ?? "ootd.html";
  document.querySelectorAll<HTMLAnchorElement>(".app-nav-link").forEach((link) => {
    if ((link.getAttribute("href") ?? "").endsWith(current)) {
      link.classList.add("active");
      link.setAttribute("aria-current", "page");
    }
  });
}

function getCurrentPosition(): Promise<GeolocationPosition> {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error("Geolocation is not supported in this browser."));
      return;
    }

    navigator.geolocation.getCurrentPosition(resolve, reject, {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 300000
    });
  });
}

function renderSeasonBadges(seasons: string[]): void {
  if (seasons.length === 0) {
    html("#seasonBadges", "");
    return;
  }
  html("#seasonBadges", seasons.map((season) => badge(season, "ok")).join(""));
}

function renderItemCard(label: string, item: ClothingItem | null): string {
  if (!item) {
    return `
      <article class="ootd-item">
        <div class="ootd-item-media">
          <img src="${PLACEHOLDER_IMAGE}" alt="${label} placeholder" loading="lazy">
        </div>
        <div class="ootd-item-body">
          <p class="eyebrow">${label}</p>
          <h4>Not selected</h4>
          <p class="ootd-item-meta">No suitable item was picked for this slot.</p>
        </div>
      </article>
    `;
  }

  const image = item.image_url || PLACEHOLDER_IMAGE;
  const description = item.description || "No description provided.";
  return `
    <article class="ootd-item">
      <div class="ootd-item-media">
        <img src="${image}" alt="${item.item}" loading="lazy">
      </div>
      <div class="ootd-item-body">
        <p class="eyebrow">${label}</p>
        <h4>${item.item}</h4>
        <p>${description}</p>
        <p class="ootd-item-meta">${badge(item.category)} ${badge(item.color_semantics || "unknown", "warn")}</p>
      </div>
    </article>
  `;
}

function renderRecommendation(data: RecommendationResponse): void {
  const { outfit, weather, history, seasons } = data;

  text("#weatherText", `${weather.location} · ${weather.temperature}°C · ${weather.condition}`);
  text("#recommendText", outfit.recommendation_text || "No recommendation text returned.");
  text("#outfitCreated", formatDate(outfit.created_at));
  text("#historyMeta", `History entry #${history.id}`);
  renderSeasonBadges(seasons);
  html(
    "#ootdItemGrid",
    [
      renderItemCard("Top", outfit.top_detail),
      renderItemCard("Bottom", outfit.bottom_detail),
      renderItemCard("Shoes", outfit.shoes_detail)
    ].join("")
  );
}

async function generate(event?: SubmitEvent): Promise<void> {
  event?.preventDefault();

  toggleDisabled("#recommendBtn", true);
  text("#ootdStatus", "Getting your current location...");

  try {
    const position = await getCurrentPosition();
    text("#ootdStatus", "Generating recommendation...");

    const data = await recommend(position.coords.latitude, position.coords.longitude);
    renderRecommendation(data);
    text("#ootdStatus", "Recommendation generated and history was auto-created.");
  } catch (error) {
    const message = error instanceof Error ? error.message : "Recommendation failed.";
    text("#ootdStatus", message);
    renderSeasonBadges([]);
    text("#weatherText", "");
    text("#recommendText", "Generate an outfit to see the weather-aware recommendation.");
    text("#outfitCreated", "Not generated yet");
    text("#historyMeta", "No record yet");
    html("#ootdItemGrid", "<article class=\"ootd-item empty-state-card\"><p class=\"muted\">No outfit selected yet.</p></article>");
  } finally {
    toggleDisabled("#recommendBtn", false);
  }
}

function init(): void {
  requireAuth();
  setActiveNav();
  initMobileSidebar();
  requireElement<HTMLFormElement>("#locationForm").addEventListener("submit", (event) => {
    void generate(event as SubmitEvent);
  });
}

init();
