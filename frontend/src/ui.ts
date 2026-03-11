import type { ApiError } from "./types.js";

export function text(id: string, value: string): void {
  const el = document.querySelector<HTMLElement>(id);
  if (el) {
    el.textContent = value;
  }
}

export function html(id: string, value: string): void {
  const el = document.querySelector<HTMLElement>(id);
  if (el) {
    el.innerHTML = value;
  }
}

export function toggleDisabled(id: string, disabled: boolean): void {
  const button = document.querySelector<HTMLButtonElement>(id);
  if (button) {
    button.disabled = disabled;
  }
}

export async function parseError(response: Response): Promise<string> {
  try {
    const data = (await response.json()) as ApiError;
    if (data.detail) {
      return data.detail;
    }
  } catch {
    return `Request failed (${response.status})`;
  }
  return `Request failed (${response.status})`;
}

export function formatDate(value: string): string {
  const dt = new Date(value);
  return Number.isNaN(dt.getTime()) ? value : dt.toLocaleString();
}

export function requireElement<T extends Element>(selector: string): T {
  const element = document.querySelector<T>(selector);
  if (!element) {
    throw new Error(`Missing element: ${selector}`);
  }
  return element;
}

export function badge(textValue: string, kind: "ok" | "warn" | "error" = "ok"): string {
  return `<span class="status-badge status-${kind}">${textValue}</span>`;
}

export function initMobileSidebar(): void {
  const sidebar = document.querySelector<HTMLElement>(".app-sidebar");
  const nav = document.querySelector<HTMLElement>(".app-nav");
  const toggle = document.querySelector<HTMLButtonElement>(".app-nav-toggle");

  if (!sidebar || !nav || !toggle) {
    return;
  }

  const mobileQuery = window.matchMedia("(max-width: 960px)");

  const setExpanded = (expanded: boolean): void => {
    toggle.textContent = expanded ? "Hide menu" : "Show menu";
    toggle.setAttribute("aria-expanded", String(expanded));
    toggle.setAttribute("aria-label", expanded ? "Hide navigation menu" : "Show navigation menu");
    sidebar.classList.toggle("is-nav-open", expanded && mobileQuery.matches);
    nav.setAttribute("aria-hidden", String(mobileQuery.matches ? !expanded : false));
  };

  const syncForViewport = (): void => {
    sidebar.classList.toggle("is-collapsible", mobileQuery.matches);
    setExpanded(!mobileQuery.matches);
  };

  toggle.hidden = false;
  toggle.addEventListener("click", () => {
    if (!mobileQuery.matches) {
      return;
    }
    const expanded = toggle.getAttribute("aria-expanded") === "true";
    setExpanded(!expanded);
  });

  nav.querySelectorAll<HTMLAnchorElement>("a").forEach((link) => {
    link.addEventListener("click", () => {
      if (mobileQuery.matches) {
        setExpanded(false);
      }
    });
  });

  mobileQuery.addEventListener("change", syncForViewport);
  syncForViewport();
}
