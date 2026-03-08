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
