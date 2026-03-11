from services.openrouter import chat_completion
from services.weather import WeatherInfo


def build_outfit_prompt(
    weather: WeatherInfo,
    seasons: list[str],
    tops: list[dict[str, object]],
    bottoms: list[dict[str, object]],
) -> str:
    return f"""
Generate a practical outfit recommendation for this weather.

Weather:
- temperature: {weather.temperature} C
- feels like: {weather.feelsLike} C
- condition: {weather.condition}
- humidity: {weather.humidity}%
- wind: {weather.windDir} {weather.windScale}

Season signals: {", ".join(seasons)}

Available tops:
{tops}

Available bottoms:
{bottoms}

Write a concise recommendation that:
1. explains why the outfit suits the weather
2. mentions useful precautions
3. references the available wardrobe items when possible
4. stays under 120 words
""".strip()


async def get_llm_recommendation(
    weather: WeatherInfo,
    seasons: list[str],
    tops: list[dict[str, object]],
    bottoms: list[dict[str, object]],
) -> str:
    return await chat_completion(
        [
            {
                "role": "system",
                "content": "You are a practical outfit recommendation assistant.",
            },
            {
                "role": "user",
                "content": build_outfit_prompt(weather, seasons, tops, bottoms),
            },
        ],
        temperature=0.7,
    )
