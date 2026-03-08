import { clearTokens, getAccessToken, getRefreshToken, setTokens } from "./auth.js";
import { API_BASE, ROUTES } from "./config.js";
import { parseError } from "./ui.js";
async function refreshAccessToken() {
    const refresh = getRefreshToken();
    if (!refresh) {
        throw new Error("No refresh token");
    }
    const response = await fetch(`${API_BASE}/auth/refresh/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh })
    });
    if (!response.ok) {
        throw new Error(await parseError(response));
    }
    const data = (await response.json());
    setTokens(data);
    return data.access;
}
async function request(path, options = {}) {
    const access = getAccessToken();
    const retry = options.retry !== false;
    const init = {
        method: options.method ?? "GET",
        headers: {
            ...(options.json ? { "Content-Type": "application/json" } : {}),
            ...(access ? { Authorization: `Bearer ${access}` } : {}),
            ...(options.headers ?? {})
        }
    };
    if (options.body !== undefined) {
        init.body = options.body;
    }
    const response = await fetch(`${API_BASE}${path}`, init);
    if (response.status !== 401 || !retry) {
        return response;
    }
    try {
        const newAccess = await refreshAccessToken();
        const retryInit = {
            method: options.method ?? "GET",
            headers: {
                ...(options.json ? { "Content-Type": "application/json" } : {}),
                Authorization: `Bearer ${newAccess}`,
                ...(options.headers ?? {})
            }
        };
        if (options.body !== undefined) {
            retryInit.body = options.body;
        }
        return fetch(`${API_BASE}${path}`, retryInit);
    }
    catch {
        clearTokens();
        window.location.href = ROUTES.index;
        throw new Error("Authentication expired");
    }
}
async function parseJson(response) {
    if (!response.ok) {
        throw new Error(await parseError(response));
    }
    return (await response.json());
}
export async function register(username, email, password) {
    const response = await request("/auth/user/register/", {
        method: "POST",
        json: true,
        body: JSON.stringify({ username, email, password })
    });
    return parseJson(response);
}
export async function login(username, password) {
    const response = await request("/auth/user/login/", {
        method: "POST",
        json: true,
        body: JSON.stringify({ username, password })
    });
    return parseJson(response);
}
export async function logout(refresh) {
    const response = await request("/auth/logout/", {
        method: "POST",
        json: true,
        body: JSON.stringify({ refresh })
    });
    if (!response.ok && response.status !== 204) {
        throw new Error(await parseError(response));
    }
}
export async function getMe() {
    const response = await request("/auth/me/");
    return parseJson(response);
}
export async function getClosetItems() {
    const response = await request("/wardrobe/items/");
    return parseJson(response);
}
export async function createClosetItem(payload) {
    const form = new FormData();
    form.append("category", payload.category);
    form.append("item", payload.item);
    form.append("style_semantics", JSON.stringify(payload.style_semantics));
    form.append("season_semantics", JSON.stringify(payload.season_semantics));
    form.append("usage_semantics", JSON.stringify(payload.usage_semantics));
    form.append("color_semantics", payload.color_semantics);
    form.append("description", payload.description);
    const response = await request("/wardrobe/items/", {
        method: "POST",
        body: form
    });
    return parseJson(response);
}
export async function updateClosetItem(id, payload) {
    const form = new FormData();
    if (payload.category)
        form.append("category", payload.category);
    if (payload.item)
        form.append("item", payload.item);
    if (payload.style_semantics)
        form.append("style_semantics", JSON.stringify(payload.style_semantics));
    if (payload.season_semantics)
        form.append("season_semantics", JSON.stringify(payload.season_semantics));
    if (payload.usage_semantics)
        form.append("usage_semantics", JSON.stringify(payload.usage_semantics));
    if (payload.color_semantics !== undefined)
        form.append("color_semantics", payload.color_semantics);
    if (payload.description !== undefined)
        form.append("description", payload.description);
    const response = await request(`/wardrobe/items/${id}/`, {
        method: "PATCH",
        body: form
    });
    return parseJson(response);
}
export async function deleteClosetItem(id) {
    const response = await request(`/wardrobe/items/${id}/`, { method: "DELETE" });
    if (!response.ok && response.status !== 204) {
        throw new Error(await parseError(response));
    }
}
export async function uploadClosetImage(file) {
    const token = getAccessToken();
    const form = new FormData();
    form.append("file", file);
    const response = await fetch(`${API_BASE}/wardrobe/items/upload/`, {
        method: "POST",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        body: form
    });
    return parseJson(response);
}
export async function searchCity(query) {
    const response = await request(`/integrations/weather/search/?query=${encodeURIComponent(query)}`);
    return parseJson(response);
}
export async function weatherNow(location) {
    const response = await request(`/integrations/weather/now/?location=${encodeURIComponent(location)}`);
    return parseJson(response);
}
export async function recommend(location) {
    const response = await request("/outfits/recommend/", {
        method: "POST",
        json: true,
        body: JSON.stringify({ location })
    });
    return parseJson(response);
}
export async function getHistory() {
    const response = await request("/outfits/history/");
    return parseJson(response);
}
export async function createHistory(outfit, rating, feedback) {
    const response = await request("/outfits/history/", {
        method: "POST",
        json: true,
        body: JSON.stringify({ outfit, rating, feedback })
    });
    return parseJson(response);
}
export async function updateHistory(id, rating, feedback) {
    const response = await request(`/outfits/history/${id}/`, {
        method: "PATCH",
        json: true,
        body: JSON.stringify({ rating, feedback })
    });
    return parseJson(response);
}
export async function deleteHistory(id) {
    const response = await request(`/outfits/history/${id}/`, { method: "DELETE" });
    if (!response.ok && response.status !== 204) {
        throw new Error(await parseError(response));
    }
}
export async function getIntegrationConfig() {
    const response = await request("/integrations/config/");
    return parseJson(response);
}
export async function updateIntegrationConfig(payload) {
    const response = await request("/integrations/config/", {
        method: "POST",
        json: true,
        body: JSON.stringify(payload)
    });
    return parseJson(response);
}
