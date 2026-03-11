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
    try:
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
    except Exception:
        return generate_basic_recommendation(weather, seasons)


def generate_basic_recommendation(weather: WeatherInfo, seasons: list[str]) -> str:
    temp = weather.feelsLike
    condition = weather.condition

    if temp < 0:
        base_text = "Today is extremely cold. Wear a thick coat or down jacket with warm layers and insulated shoes."
    elif temp < 10:
        base_text = "Today is cold. A coat or jacket with a long-sleeve top and full-length trousers will work well."
    elif temp < 20:
        base_text = "Today is mild. A light jacket or layered long-sleeve outfit will keep you comfortable."
    elif temp < 28:
        base_text = "Today is comfortable. Lightweight tops with casual trousers are a good choice."
    else:
        base_text = "Today is hot. Choose breathable summer clothing and lighter fabrics."

    if "rain" in condition.lower() or "drizzle" in condition.lower() or "shower" in condition.lower():
        base_text += " Take an umbrella and prefer shoes that can handle wet ground."
    elif "snow" in condition.lower():
        base_text += " Choose warm, slip-resistant footwear."
    elif "clear" in condition.lower() or "sun" in condition.lower():
        if temp > 25:
            base_text += " Strong sunlight is likely, so add sun protection if you will be outside."
    elif "cloud" in condition.lower() or "overcast" in condition.lower():
        base_text += " A light extra layer may still be useful."

    if seasons:
        base_text += f" Seasonal match: {', '.join(seasons)}."

    return base_text
