import { clearTokens, getAccessToken, getRefreshToken, setTokens } from "./auth.js";
import { API_BASE, ROUTES } from "./config.js";
import { parseError } from "./ui.js";
import type {
  AuthTokens,
  ClothingAnalysis,
  ClothingItem,
  OutfitHistory,
  RecommendationResponse,
  User,
  WeatherNow
} from "./types.js";

type Method = "GET" | "POST" | "PATCH" | "PUT" | "DELETE";

export interface ClosetItemDraft {
  category: ClothingAnalysis["category"];
  item: string;
  style_semantics: string[];
  season_semantics: string[];
  usage_semantics: string[];
  color_semantics: string;
  description: string;
  image?: File;
}

interface RequestOptions {
  method?: Method;
  body?: BodyInit;
  json?: boolean;
  headers?: Record<string, string>;
  retry?: boolean;
}

async function refreshAccessToken(): Promise<string> {
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

  const data = (await response.json()) as AuthTokens;
  setTokens(data);
  return data.access;
}

async function request(path: string, options: RequestOptions = {}): Promise<Response> {
  const access = getAccessToken();
  const retry = options.retry !== false;
  const init: RequestInit = {
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
    const retryInit: RequestInit = {
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
  } catch {
    clearTokens();
    window.location.href = ROUTES.index;
    throw new Error("Authentication expired");
  }
}

async function parseJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    throw new Error(await parseError(response));
  }
  return (await response.json()) as T;
}

export async function register(username: string, email: string, password: string): Promise<User> {
  const response = await request("/auth/user/register/", {
    method: "POST",
    json: true,
    body: JSON.stringify({ username, email, password })
  });
  return parseJson<User>(response);
}

export async function login(username: string, password: string): Promise<AuthTokens> {
  const response = await request("/auth/user/login/", {
    method: "POST",
    json: true,
    body: JSON.stringify({ username, password })
  });
  return parseJson<AuthTokens>(response);
}

export async function logout(refresh: string): Promise<void> {
  const response = await request("/auth/logout/", {
    method: "POST",
    json: true,
    body: JSON.stringify({ refresh })
  });
  if (!response.ok && response.status !== 204) {
    throw new Error(await parseError(response));
  }
}

export async function getMe(): Promise<User> {
  const response = await request("/auth/me/");
  return parseJson<User>(response);
}

export async function getClosetItems(): Promise<ClothingItem[]> {
  const response = await request("/wardrobe/items/");
  return parseJson<ClothingItem[]>(response);
}

export async function createClosetItem(payload: ClosetItemDraft): Promise<ClothingItem> {
  const form = new FormData();
  form.append("category", payload.category);
  form.append("item", payload.item);
  form.append("style_semantics", JSON.stringify(payload.style_semantics));
  form.append("season_semantics", JSON.stringify(payload.season_semantics));
  form.append("usage_semantics", JSON.stringify(payload.usage_semantics));
  form.append("color_semantics", payload.color_semantics);
  form.append("description", payload.description);
  if (payload.image) form.append("image", payload.image);
  const response = await request("/wardrobe/items/", {
    method: "POST",
    body: form
  });
  return parseJson<ClothingItem>(response);
}

export async function updateClosetItem(id: number, payload: Partial<ClothingItem>): Promise<ClothingItem> {
  const form = new FormData();
  if (payload.category) form.append("category", payload.category);
  if (payload.item) form.append("item", payload.item);
  if (payload.style_semantics) form.append("style_semantics", JSON.stringify(payload.style_semantics));
  if (payload.season_semantics) form.append("season_semantics", JSON.stringify(payload.season_semantics));
  if (payload.usage_semantics) form.append("usage_semantics", JSON.stringify(payload.usage_semantics));
  if (payload.color_semantics !== undefined) form.append("color_semantics", payload.color_semantics);
  if (payload.description !== undefined) form.append("description", payload.description);
  const response = await request(`/wardrobe/items/${id}/`, {
    method: "PATCH",
    body: form
  });
  return parseJson<ClothingItem>(response);
}

export async function deleteClosetItem(id: number): Promise<void> {
  const response = await request(`/wardrobe/items/${id}/`, { method: "DELETE" });
  if (!response.ok && response.status !== 204) {
    throw new Error(await parseError(response));
  }
}

export async function uploadClosetImage(file: File, removeBackground = false): Promise<ClothingAnalysis> {
  const form = new FormData();
  form.append("file", file);
  form.append("remove_background", String(removeBackground));
  const response = await request("/wardrobe/items/upload/", {
    method: "POST",
    body: form
  });
  return parseJson<ClothingAnalysis>(response);
}

export async function recommend(latitude: number, longitude: number): Promise<RecommendationResponse> {
  const response = await request("/outfits/recommend/", {
    method: "POST",
    json: true,
    body: JSON.stringify({ latitude, longitude })
  });
  return parseJson<RecommendationResponse>(response);
}

export async function getHistory(): Promise<OutfitHistory[]> {
  const response = await request("/outfits/history/");
  return parseJson<OutfitHistory[]>(response);
}

export async function createHistory(outfit: number, rating: number | null, feedback: string): Promise<OutfitHistory> {
  const response = await request("/outfits/history/", {
    method: "POST",
    json: true,
    body: JSON.stringify({ outfit, rating, feedback })
  });
  return parseJson<OutfitHistory>(response);
}

export async function updateHistory(id: number, rating: number | null, feedback: string): Promise<OutfitHistory> {
  const response = await request(`/outfits/history/${id}/`, {
    method: "PATCH",
    json: true,
    body: JSON.stringify({ rating, feedback })
  });
  return parseJson<OutfitHistory>(response);
}

export async function deleteHistory(id: number): Promise<void> {
  const response = await request(`/outfits/history/${id}/`, { method: "DELETE" });
  if (!response.ok && response.status !== 204) {
    throw new Error(await parseError(response));
  }
}
