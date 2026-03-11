import { recommend } from "../api.js";
import { requireAuth } from "../auth.js";
import { formatDate, html, requireElement, text, toggleDisabled } from "../ui.js";

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

async function generate(event?: SubmitEvent): Promise<void> {
  event?.preventDefault();

  toggleDisabled("#recommendBtn", true);
  text("#ootdStatus", "Getting your current location...");

  try {
    const position = await getCurrentPosition();
    text("#ootdStatus", "Generating recommendation...");

    const data = await recommend(position.coords.latitude, position.coords.longitude);
    const top = data.outfit.top_detail?.item ?? "None";
    const bottom = data.outfit.bottom_detail?.item ?? "None";
    const shoes = data.outfit.shoes_detail?.item ?? "None";

    text("#weatherText", `${data.weather.location}: ${data.weather.temperature}°C, ${data.weather.condition}`);
    text("#recommendText", data.outfit.recommendation_text || "No recommendation text returned.");
    html("#outfitItems", `
      <li>Top: ${top}</li>
      <li>Bottom: ${bottom}</li>
      <li>Shoes: ${shoes}</li>
      <li>Created: ${formatDate(data.outfit.created_at)}</li>
      <li>History entry id: ${data.history.id}</li>
    `);
    text("#ootdStatus", "Recommendation generated and history was auto-created.");
  } catch (error) {
    const message = error instanceof Error ? error.message : "Recommendation failed.";
    text("#ootdStatus", message);
  } finally {
    toggleDisabled("#recommendBtn", false);
  }
}

function init(): void {
  requireAuth();
  setActiveNav();
  requireElement<HTMLFormElement>("#locationForm").addEventListener("submit", (event) => {
    void generate(event as SubmitEvent);
  });
}

init();
