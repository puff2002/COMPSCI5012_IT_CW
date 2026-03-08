import { ROUTES } from "./config.js";
import type { AuthTokens } from "./types.js";

const ACCESS_KEY = "sc_access";
const REFRESH_KEY = "sc_refresh";
const RETURN_TO_KEY = "sc_return_to";

export function setTokens(tokens: AuthTokens): void {
  localStorage.setItem(ACCESS_KEY, tokens.access);
  localStorage.setItem(REFRESH_KEY, tokens.refresh);
}

export function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_KEY);
}

export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_KEY);
}

export function clearTokens(): void {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

export function setReturnPath(path: string): void {
  localStorage.setItem(RETURN_TO_KEY, path);
}

export function consumeReturnPath(): string {
  const stored = localStorage.getItem(RETURN_TO_KEY);
  if (stored) {
    localStorage.removeItem(RETURN_TO_KEY);
    return stored;
  }
  return ROUTES.dashboard;
}

export function isAuthenticated(): boolean {
  return Boolean(getAccessToken());
}

export function requireAuth(): void {
  if (!isAuthenticated()) {
    setReturnPath(window.location.pathname);
    window.location.href = ROUTES.index;
  }
}
