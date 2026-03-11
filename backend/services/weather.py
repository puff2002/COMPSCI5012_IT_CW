"""
Weather service backed by Open-Meteo.
Docs:
- https://open-meteo.com/en/docs/geocoding-api
- https://open-meteo.com/en/docs
"""
import base64
import json
from typing import List, Optional

import httpx
from pydantic import BaseModel


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


class CityInfo(BaseModel):
    """City search result."""
    name: str
    id: str
    adm1: str
    adm2: str
    country: str
    lat: str
    lon: str


class WeatherInfo(BaseModel):
    """Simplified weather payload used by the app."""
    temperature: float
    feelsLike: float
    condition: str
    icon: str
    humidity: float
    windDir: str
    windScale: str
    location: str
    obsTime: str


WEATHER_CODE_MAP = {
    0: ("Clear sky", "100"),
    1: ("Mainly clear", "101"),
    2: ("Partly cloudy", "102"),
    3: ("Overcast", "104"),
    45: ("Fog", "500"),
    48: ("Depositing rime fog", "501"),
    51: ("Light drizzle", "300"),
    53: ("Moderate drizzle", "301"),
    55: ("Dense drizzle", "302"),
    56: ("Light freezing drizzle", "313"),
    57: ("Dense freezing drizzle", "314"),
    61: ("Slight rain", "305"),
    63: ("Moderate rain", "306"),
    65: ("Heavy rain", "307"),
    66: ("Light freezing rain", "311"),
    67: ("Heavy freezing rain", "312"),
    71: ("Slight snow", "400"),
    73: ("Moderate snow", "401"),
    75: ("Heavy snow", "402"),
    77: ("Snow grains", "407"),
    80: ("Slight rain showers", "350"),
    81: ("Moderate rain showers", "351"),
    82: ("Violent rain showers", "352"),
    85: ("Slight snow showers", "456"),
    86: ("Heavy snow showers", "457"),
    95: ("Thunderstorm", "302"),
    96: ("Thunderstorm with slight hail", "303"),
    99: ("Thunderstorm with heavy hail", "304"),
}


def _encode_location_token(result: dict) -> str:
    payload = json.dumps(
        {
            "name": result.get("name", ""),
            "adm1": result.get("admin1", "") or "",
            "adm2": result.get("admin2", "") or "",
            "country": result.get("country", "") or "",
            "lat": result.get("latitude"),
            "lon": result.get("longitude"),
        },
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")


def _decode_location_token(location: str) -> Optional[dict]:
    try:
        padding = "=" * (-len(location) % 4)
        decoded = base64.urlsafe_b64decode(f"{location}{padding}")
        data = json.loads(decoded.decode("utf-8"))
        lat = float(data["lat"])
        lon = float(data["lon"])
        return {
            "name": str(data.get("name", "")).strip(),
            "adm1": str(data.get("adm1", "")).strip(),
            "adm2": str(data.get("adm2", "")).strip(),
            "country": str(data.get("country", "")).strip(),
            "lat": lat,
            "lon": lon,
        }
    except Exception:
        return None


def _location_label(data: dict) -> str:
    parts = [data.get("name", "").strip(), data.get("adm1", "").strip(), data.get("country", "").strip()]
    return ", ".join(part for part in parts if part)


def _wind_direction(degrees: float) -> str:
    labels = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    normalized = degrees % 360
    index = int((normalized + 22.5) // 45) % len(labels)
    return labels[index]


def _wind_scale(speed_kmh: float) -> str:
    # Beaufort scale using km/h thresholds.
    thresholds = [1, 6, 12, 20, 29, 39, 50, 62, 75, 89, 103, 118]
    for index, threshold in enumerate(thresholds):
        if speed_kmh < threshold:
            return str(index)
    return "12"


def _weather_condition(code: int) -> tuple[str, str]:
    return WEATHER_CODE_MAP.get(code, ("Unknown", str(code)))


async def search_city(query: str, limit: int = 10) -> List[CityInfo]:
    """Search cities with Open-Meteo's geocoding API."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                GEOCODING_URL,
                params={"name": query, "count": limit, "language": "en", "format": "json"},
                timeout=10.0,
            )
            response.raise_for_status()
    except Exception as exc:
        print(f"Failed to search cities: {exc}")
        return []

    results = response.json().get("results", []) or []
    cities: List[CityInfo] = []
    for result in results:
        token = _encode_location_token(result)
        cities.append(
            CityInfo(
                name=result.get("name", ""),
                id=token,
                adm1=result.get("admin1", "") or "",
                adm2=result.get("admin2", "") or "",
                country=result.get("country", "") or "",
                lat=str(result.get("latitude", "")),
                lon=str(result.get("longitude", "")),
            )
        )
    return cities


async def get_weather(location: str) -> Optional[WeatherInfo]:
    """Fetch current weather for an encoded Open-Meteo location token."""
    location_data = _decode_location_token(location)
    if not location_data:
        print("Invalid weather location token")
        return None

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                FORECAST_URL,
                params={
                    "latitude": location_data["lat"],
                    "longitude": location_data["lon"],
                    "current": ",".join(
                        [
                            "temperature_2m",
                            "relative_humidity_2m",
                            "apparent_temperature",
                            "weather_code",
                            "wind_speed_10m",
                            "wind_direction_10m",
                        ]
                    ),
                    "timezone": "auto",
                },
                timeout=10.0,
            )
            response.raise_for_status()
    except Exception as exc:
        print(f"Failed to fetch weather: {exc}")
        return None

    current = response.json().get("current")
    if not current:
        return None

    code = int(current.get("weather_code", -1))
    condition, icon = _weather_condition(code)
    wind_speed = float(current.get("wind_speed_10m", 0.0))
    wind_degrees = float(current.get("wind_direction_10m", 0.0))

    return WeatherInfo(
        temperature=float(current.get("temperature_2m", 0.0)),
        feelsLike=float(current.get("apparent_temperature", 0.0)),
        condition=condition,
        icon=icon,
        humidity=float(current.get("relative_humidity_2m", 0.0)),
        windDir=_wind_direction(wind_degrees),
        windScale=_wind_scale(wind_speed),
        location=_location_label(location_data),
        obsTime=str(current.get("time", "")),
    )


async def get_weather_for_query(location_query: str) -> Optional[WeatherInfo]:
    location_query = location_query.strip()
    if not location_query:
        return None

    token_payload = _decode_location_token(location_query)
    if token_payload:
        return await get_weather(location_query)

    cities = await search_city(location_query, limit=1)
    if not cities:
        return None

    return await get_weather(cities[0].id)


def get_season_from_weather(weather: WeatherInfo) -> list[str]:
    """
    根据天气推断适合的季节标签

    Args:
        weather: 天气信息

    Returns:
        季节标签列表
    """
    temp = weather.temperature
    seasons = []

    if temp <= 10:
        seasons.extend(["winter", "autumn"])
    elif temp <= 20:
        seasons.extend(["spring", "autumn"])
    else:
        seasons.extend(["summer", "spring"])

    return list(dict.fromkeys(seasons))


def get_clothing_suggestion(weather: WeatherInfo) -> str:
    """
    根据天气生成穿搭建议

    Args:
        weather: 天气信息

    Returns:
        穿搭建议文本
    """
    temp = weather.temperature
    feels_like = weather.feelsLike
    condition = weather.condition.lower()

    suggestions = []

    if feels_like <= 5:
        suggestions.append("天气很冷，建议穿厚外套、毛衣、长裤，注意保暖。")
    elif feels_like <= 15:
        suggestions.append("天气较凉，建议穿外套或针织衫搭配长裤。")
    elif feels_like <= 25:
        suggestions.append("天气舒适，适合衬衫、T恤搭配长裤或裙装。")
    else:
        suggestions.append("天气炎热，建议穿轻薄透气的夏装。")

    if "rain" in condition or "drizzle" in condition or "shower" in condition:
        suggestions.append("有降水，建议带伞并选择防水鞋。")
    if "snow" in condition:
        suggestions.append("有降雪，建议穿防滑保暖的鞋靴。")
    if "thunderstorm" in condition:
        suggestions.append("有雷暴，建议减少户外停留并做好防雨。")
    if "fog" in condition:
        suggestions.append("有雾，外出注意能见度变化。")

    return " ".join(suggestions)
