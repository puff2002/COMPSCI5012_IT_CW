import { getIntegrationConfig, getMe, logout, updateIntegrationConfig } from "../api.js";
import { clearTokens, getRefreshToken, requireAuth } from "../auth.js";
import { ROUTES } from "../config.js";
import { requireElement, text, toggleDisabled } from "../ui.js";
import type { IntegrationConfigUpdate } from "../types.js";

function setActiveNav(): void {
  const current = window.location.pathname.split("/").pop() ?? "settings.html";
  document.querySelectorAll<HTMLAnchorElement>(".app-nav-link").forEach((link) => {
    if ((link.getAttribute("href") ?? "").endsWith(current)) {
      link.classList.add("active");
      link.setAttribute("aria-current", "page");
    }
  });
}

async function loadSettings(): Promise<void> {
  text("#settingsStatus", "Loading settings...");

  try {
    const [user, config] = await Promise.all([getMe(), getIntegrationConfig()]);
    text("#profileText", `${user.username} (${user.email})`);

    requireElement<HTMLInputElement>("#apiBase").value = config.api_base;
    requireElement<HTMLInputElement>("#model").value = config.model;
    requireElement<HTMLInputElement>("#bgMethod").value = config.bg_removal_method;
    requireElement<HTMLInputElement>("#weatherHost").value = config.qweather_api_host;

    text("#maskedKeys", `LLM key: ${config.api_key_masked} | RemoveBG: ${config.removebg_api_key_masked} | QWeather: ${config.qweather_api_key_masked}`);
    text("#settingsStatus", "Settings loaded.");
  } catch (error) {
    const message = error instanceof Error ? error.message : "Failed to load settings.";
    text("#settingsStatus", message);
  }
}

async function saveConfig(event: SubmitEvent): Promise<void> {
  event.preventDefault();
  toggleDisabled("#configSaveBtn", true);
  text("#configError", "");

  const payload: IntegrationConfigUpdate = {
    api_base: requireElement<HTMLInputElement>("#apiBase").value.trim(),
    api_key: requireElement<HTMLInputElement>("#apiKey").value.trim(),
    model: requireElement<HTMLInputElement>("#model").value.trim(),
    removebg_api_key: requireElement<HTMLInputElement>("#removeBgKey").value.trim(),
    bg_removal_method: requireElement<HTMLInputElement>("#bgMethod").value.trim(),
    qweather_api_key: requireElement<HTMLInputElement>("#weatherKey").value.trim(),
    qweather_api_host: requireElement<HTMLInputElement>("#weatherHost").value.trim()
  };

  try {
    await updateIntegrationConfig(payload);
    text("#settingsStatus", "Config saved.");
    requireElement<HTMLInputElement>("#apiKey").value = "";
    requireElement<HTMLInputElement>("#removeBgKey").value = "";
    requireElement<HTMLInputElement>("#weatherKey").value = "";
  } catch (error) {
    const message = error instanceof Error ? error.message : "Failed to save config.";
    text("#configError", message);
  } finally {
    toggleDisabled("#configSaveBtn", false);
  }
}

async function onLogout(): Promise<void> {
  const refresh = getRefreshToken();
  try {
    if (refresh) {
      await logout(refresh);
    }
  } catch {
  } finally {
    clearTokens();
    window.location.href = ROUTES.index;
  }
}

function init(): void {
  requireAuth();
  setActiveNav();
  requireElement<HTMLFormElement>("#configForm").addEventListener("submit", (event) => {
    void saveConfig(event as SubmitEvent);
  });
  requireElement<HTMLButtonElement>("#logoutBtn").addEventListener("click", () => {
    void onLogout();
  });
  void loadSettings();
}

init();
