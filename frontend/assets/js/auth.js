import { ROUTES } from "./config.js";
const ACCESS_KEY = "sc_access";
const REFRESH_KEY = "sc_refresh";
const RETURN_TO_KEY = "sc_return_to";
export function setTokens(tokens) {
    localStorage.setItem(ACCESS_KEY, tokens.access);
    localStorage.setItem(REFRESH_KEY, tokens.refresh);
}
export function getAccessToken() {
    return localStorage.getItem(ACCESS_KEY);
}
export function getRefreshToken() {
    return localStorage.getItem(REFRESH_KEY);
}
export function clearTokens() {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
}
export function setReturnPath(path) {
    localStorage.setItem(RETURN_TO_KEY, path);
}
export function consumeReturnPath() {
    const stored = localStorage.getItem(RETURN_TO_KEY);
    if (stored) {
        localStorage.removeItem(RETURN_TO_KEY);
        return stored;
    }
    return ROUTES.dashboard;
}
export function isAuthenticated() {
    return Boolean(getAccessToken());
}
export function requireAuth() {
    if (!isAuthenticated()) {
        setReturnPath(window.location.pathname);
        window.location.href = ROUTES.index;
    }
}
