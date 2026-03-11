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
    requireElement<HTMLInputElement>("#bgMethod").value = config.bg_removal_method;
    text("#maskedKeys", `RemoveBG key: ${config.removebg_api_key_masked}`);
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
    removebg_api_key: requireElement<HTMLInputElement>("#removeBgKey").value.trim(),
    bg_removal_method: requireElement<HTMLInputElement>("#bgMethod").value.trim()
  };

  try {
    await updateIntegrationConfig(payload);
    text("#settingsStatus", "Config saved.");
    requireElement<HTMLInputElement>("#removeBgKey").value = "";
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
