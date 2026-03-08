import { getIntegrationConfig, getMe, logout, updateIntegrationConfig } from "../api.js";
import { clearTokens, getRefreshToken, requireAuth } from "../auth.js";
import { ROUTES } from "../config.js";
import { requireElement, text, toggleDisabled } from "../ui.js";
function setActiveNav() {
    const current = window.location.pathname.split("/").pop() ?? "settings.html";
    document.querySelectorAll(".app-nav-link").forEach((link) => {
        if ((link.getAttribute("href") ?? "").endsWith(current)) {
            link.classList.add("active");
            link.setAttribute("aria-current", "page");
        }
    });
}
async function loadSettings() {
    text("#settingsStatus", "Loading settings...");
    try {
        const [user, config] = await Promise.all([getMe(), getIntegrationConfig()]);
        text("#profileText", `${user.username} (${user.email})`);
        requireElement("#apiBase").value = config.api_base;
        requireElement("#model").value = config.model;
        requireElement("#bgMethod").value = config.bg_removal_method;
        requireElement("#weatherHost").value = config.qweather_api_host;
        text("#maskedKeys", `LLM key: ${config.api_key_masked} | RemoveBG: ${config.removebg_api_key_masked} | QWeather: ${config.qweather_api_key_masked}`);
        text("#settingsStatus", "Settings loaded.");
    }
    catch (error) {
        const message = error instanceof Error ? error.message : "Failed to load settings.";
        text("#settingsStatus", message);
    }
}
async function saveConfig(event) {
    event.preventDefault();
    toggleDisabled("#configSaveBtn", true);
    text("#configError", "");
    const payload = {
        api_base: requireElement("#apiBase").value.trim(),
        api_key: requireElement("#apiKey").value.trim(),
        model: requireElement("#model").value.trim(),
        removebg_api_key: requireElement("#removeBgKey").value.trim(),
        bg_removal_method: requireElement("#bgMethod").value.trim(),
        qweather_api_key: requireElement("#weatherKey").value.trim(),
        qweather_api_host: requireElement("#weatherHost").value.trim()
    };
    try {
        await updateIntegrationConfig(payload);
        text("#settingsStatus", "Config saved.");
        requireElement("#apiKey").value = "";
        requireElement("#removeBgKey").value = "";
        requireElement("#weatherKey").value = "";
    }
    catch (error) {
        const message = error instanceof Error ? error.message : "Failed to save config.";
        text("#configError", message);
    }
    finally {
        toggleDisabled("#configSaveBtn", false);
    }
}
async function onLogout() {
    const refresh = getRefreshToken();
    try {
        if (refresh) {
            await logout(refresh);
        }
    }
    catch {
    }
    finally {
        clearTokens();
        window.location.href = ROUTES.index;
    }
}
function init() {
    requireAuth();
    setActiveNav();
    requireElement("#configForm").addEventListener("submit", (event) => {
        void saveConfig(event);
    });
    requireElement("#logoutBtn").addEventListener("click", () => {
        void onLogout();
    });
    void loadSettings();
}
init();
