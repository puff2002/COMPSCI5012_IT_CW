import { getMe, logout } from "../api.js";
import { clearTokens, getRefreshToken, requireAuth } from "../auth.js";
import { ROUTES } from "../config.js";
import { requireElement, text } from "../ui.js";

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
    const user = await getMe();
    text("#profileText", `${user.username} (${user.email})`);
    text("#settingsStatus", "Settings loaded.");
  } catch (error) {
    const message = error instanceof Error ? error.message : "Failed to load settings.";
    text("#settingsStatus", message);
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
  requireElement<HTMLButtonElement>("#logoutBtn").addEventListener("click", () => {
    void onLogout();
  });
  void loadSettings();
}

init();
