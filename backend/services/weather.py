"""
Weather service backed by Open-Meteo.
Docs:
- https://open-meteo.com/en/docs
"""
from typing import Optional

import httpx
from pydantic import BaseModel


FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


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


def _location_label(latitude: float, longitude: float) -> str:
    return f"{latitude:.4f}, {longitude:.4f}"


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


async def get_weather_by_coordinates(latitude: float, longitude: float) -> Optional[WeatherInfo]:
    """Fetch current weather for a pair of coordinates."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                FORECAST_URL,
                params={
                    "latitude": latitude,
                    "longitude": longitude,
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
        location=_location_label(latitude, longitude),
        obsTime=str(current.get("time", "")),
    )


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
