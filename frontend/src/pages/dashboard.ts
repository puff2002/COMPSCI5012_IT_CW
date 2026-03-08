import { requireAuth } from "../auth.js";
import { getMe } from "../api.js";
import { text } from "../ui.js";

function setActiveNav(): void {
  const current = window.location.pathname.split("/").pop() ?? "dashboard.html";
  document.querySelectorAll<HTMLAnchorElement>(".app-nav-link").forEach((link) => {
    const href = link.getAttribute("href") ?? "";
    if (href.endsWith(current)) {
      link.classList.add("active");
      link.setAttribute("aria-current", "page");
    }
  });
}

async function initDashboard(): Promise<void> {
  requireAuth();
  setActiveNav();

  try {
    const user = await getMe();
    text("#welcomeText", `Welcome back, ${user.username}.`);
    text("#profileSummary", `${user.email} (${user.role})`);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Failed to load dashboard data.";
    text("#statusRegion", message);
  }
}

void initDashboard();
