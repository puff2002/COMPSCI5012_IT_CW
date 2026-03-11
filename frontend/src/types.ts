export type Category = "top" | "bottom" | "shoes";

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface ApiError {
  detail?: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  role: string;
  is_staff: boolean;
  is_superuser: boolean;
}

export interface ClothingItem {
  id: number;
  category: Category;
  item: string;
  style_semantics: string[];
  season_semantics: string[];
  usage_semantics: string[];
  color_semantics: string;
  description: string;
  image: string;
  image_url: string;
  created_at: string;
}

export interface Outfit {
  id: number;
  top: number | null;
  bottom: number | null;
  shoes: number | null;
  recommendation_text: string;
  weather: number | null;
  created_at: string;
  top_detail: ClothingItem | null;
  bottom_detail: ClothingItem | null;
  shoes_detail: ClothingItem | null;
}

export interface OutfitHistory {
  id: number;
  outfit: number;
  rating: number | null;
  feedback: string;
  created_at: string;
  outfit_detail: Outfit;
}

export interface WeatherNow {
  temperature: number;
  feelsLike: number;
  condition: string;
  icon: string;
  humidity: number;
  windDir: string;
  windScale: string;
  location: string;
  obsTime: string;
}

export interface CitySearchResult {
  name: string;
  id: string;
  adm1: string;
  adm2: string;
  country: string;
  lat: string;
  lon: string;
}

export interface RecommendationResponse {
  weather: WeatherNow;
  seasons: string[];
  outfit: Outfit;
  history: OutfitHistory;
}

export interface IntegrationConfigMasked {
  api_base: string;
  api_key_masked: string;
  has_api_key: boolean;
  model: string;
  removebg_api_key_masked: string;
  has_removebg_key: boolean;
  bg_removal_method: string;
}

export interface IntegrationConfigUpdate {
  api_base: string;
  api_key: string;
  model: string;
  removebg_api_key: string;
  bg_removal_method: string;
}
