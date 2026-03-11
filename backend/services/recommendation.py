from services.openrouter import chat_completion
from services.weather import WeatherInfo


def build_outfit_prompt(
    weather: WeatherInfo,
    seasons: list[str],
    tops: list[dict[str, object]],
    bottoms: list[dict[str, object]],
    shoes: list[dict[str, object]],
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

Available shoes:
{shoes}

Write a concise recommendation that:
1. explains why the outfit suits the weather
2. mentions useful precautions
3. references the available wardrobe items when possible, including footwear if relevant
4. stays under 120 words
""".strip()


async def get_llm_recommendation(
    weather: WeatherInfo,
    seasons: list[str],
    tops: list[dict[str, object]],
    bottoms: list[dict[str, object]],
    shoes: list[dict[str, object]],
) -> str:
    return await chat_completion(
        [
            {
                "role": "system",
                "content": "You are a practical outfit recommendation assistant.",
            },
            {
                "role": "user",
                "content": build_outfit_prompt(weather, seasons, tops, bottoms, shoes),
            },
        ],
        temperature=0.7,
    )


def build_outfit_image_prompt(
    weather: WeatherInfo,
    seasons: list[str],
    *,
    top: dict[str, object] | None,
    bottom: dict[str, object] | None,
    shoes: dict[str, object] | None,
    recommendation_text: str,
) -> str:
    def describe_item(label: str, item: dict[str, object] | None) -> str:
        if not item:
            return f"{label}: not selected"
        return (
            f"{label}: {item.get('item', 'Unknown item')}; "
            f"category={item.get('category', '')}; "
            f"color={item.get('color_semantics', '')}; "
            f"style={item.get('style_semantics', [])}; "
            f"description={item.get('description', '')}"
        )

    return f"""
Generate a polished fashion editorial style outfit mockup on a clean neutral background.

Weather:
- temperature: {weather.temperature} C
- feels like: {weather.feelsLike} C
- condition: {weather.condition}
- season signals: {", ".join(seasons)}

Recommended outfit:
- {describe_item("Top", top)}
- {describe_item("Bottom", bottom)}
- {describe_item("Shoes", shoes)}

Styling notes:
- Show the complete outfit together as a cohesive flat lay or mannequin-style presentation.
- Keep the garments faithful to the listed colors, materials, and overall style.
- Avoid adding extra garments or accessories that were not described.
- Make the composition clear and easy to read on a mobile screen.
- Recommendation context: {recommendation_text}
""".strip()
