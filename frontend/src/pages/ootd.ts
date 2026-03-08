import { recommend, searchCity, weatherNow } from "../api.js";
import { requireAuth } from "../auth.js";
import { formatDate, html, requireElement, text, toggleDisabled } from "../ui.js";
import type { CitySearchResult } from "../types.js";

let cities: CitySearchResult[] = [];
let selectedLocationId = "";

function setActiveNav(): void {
  const current = window.location.pathname.split("/").pop() ?? "ootd.html";
  document.querySelectorAll<HTMLAnchorElement>(".app-nav-link").forEach((link) => {
    if ((link.getAttribute("href") ?? "").endsWith(current)) {
      link.classList.add("active");
      link.setAttribute("aria-current", "page");
    }
  });
}

function renderCities(): void {
  const options = cities.map((city) => `<option value="${city.id}">${city.name}, ${city.adm1}, ${city.country}</option>`).join("");
  html("#cityList", options);
}

async function search(event: SubmitEvent): Promise<void> {
  event.preventDefault();
  const query = requireElement<HTMLInputElement>("#cityQuery").value.trim();
  if (!query) {
    text("#ootdStatus", "Enter a city to search.");
    return;
  }

  toggleDisabled("#citySearchBtn", true);
  text("#ootdStatus", "Searching cities...");

  try {
    cities = await searchCity(query);
    renderCities();
    text("#ootdStatus", `${cities.length} city option(s) found.`);
  } catch (error) {
    const message = error instanceof Error ? error.message : "City search failed.";
    text("#ootdStatus", message);
  } finally {
    toggleDisabled("#citySearchBtn", false);
  }
}

async function loadWeather(): Promise<void> {
  selectedLocationId = requireElement<HTMLSelectElement>("#cityList").value;
  if (!selectedLocationId) {
    text("#ootdStatus", "Select a city first.");
    return;
  }
  toggleDisabled("#weatherBtn", true);
  text("#ootdStatus", "Loading weather...");
  try {
    const weather = await weatherNow(selectedLocationId);
    text("#weatherText", `${weather.location}: ${weather.temperature}°C (feels ${weather.feelsLike}°C), ${weather.condition}`);
    text("#ootdStatus", "Weather loaded.");
  } catch (error) {
    const message = error instanceof Error ? error.message : "Weather unavailable.";
    text("#ootdStatus", `${message} You can still use manual selection.`);
  } finally {
    toggleDisabled("#weatherBtn", false);
  }
}

async function generate(): Promise<void> {
  const location = requireElement<HTMLSelectElement>("#cityList").value;
  if (!location) {
    text("#ootdStatus", "Select a city before generating recommendation.");
    return;
  }

  toggleDisabled("#recommendBtn", true);
  text("#ootdStatus", "Generating recommendation...");

  try {
    const data = await recommend(location);
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
    text("#ootdStatus", `${message} Fallback: use manual outfit selection from closet + history form.`);
  } finally {
    toggleDisabled("#recommendBtn", false);
  }
}

function init(): void {
  requireAuth();
  setActiveNav();
  requireElement<HTMLFormElement>("#citySearchForm").addEventListener("submit", (event) => {
    void search(event as SubmitEvent);
  });
  requireElement<HTMLButtonElement>("#weatherBtn").addEventListener("click", () => {
    void loadWeather();
  });
  requireElement<HTMLButtonElement>("#recommendBtn").addEventListener("click", () => {
    void generate();
  });
}

init();
