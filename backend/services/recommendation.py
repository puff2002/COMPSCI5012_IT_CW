import json
from typing import Any

from services.openrouter import chat_completion
from services.weather import WeatherInfo


RECOMMENDATION_CATEGORIES = ("top", "bottom", "shoes")


def _normalize_text(value: object) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip().lower()


def _normalize_list(values: object) -> list[str]:
    if not isinstance(values, list):
        return []
    normalized: list[str] = []
    for value in values:
        text = _normalize_text(value)
        if text and text not in normalized:
            normalized.append(text)
    return normalized


def _format_catalog(items: list[dict[str, object]]) -> list[dict[str, object]]:
    formatted: list[dict[str, object]] = []
    for item in items:
        formatted.append(
            {
                "item": item.get("item", ""),
                "style": item.get("style_semantics", []),
                "season": item.get("season_semantics", []),
                "color": item.get("color_semantics", ""),
                "description": item.get("description", ""),
            }
        )
    return formatted


def build_recommendation_prompt(
    weather: WeatherInfo,
    seasons: list[str],
    tops: list[dict[str, object]],
    bottoms: list[dict[str, object]],
    shoes: list[dict[str, object]],
) -> str:
    return f"""
Return a weather-aware clothing recommendation as strict JSON.

Context:
- geographic_location: {weather.location}
- observation_time: {weather.obsTime}
- temperature_c: {weather.temperature}
- feels_like_c: {weather.feelsLike}
- condition: {weather.condition}
- humidity_percent: {weather.humidity}
- wind: {weather.windDir} {weather.windScale}
- inferred_seasons: {", ".join(seasons)}

Available wardrobe summary:
- tops: {_format_catalog(tops)}
- bottoms: {_format_catalog(bottoms)}
- shoes: {_format_catalog(shoes)}

Required JSON shape:
{{
  "summary": "One short sentence describing the outfit choice.",
  "weather_focus": ["brief", "phrases"],
  "recommendations": {{
    "top": {{
      "type": "recommended clothing type",
      "season": ["season labels"],
      "color": ["color directions"],
      "texture": ["fabric or texture keywords"],
      "style": ["style keywords"],
      "reason": "why this category fits the weather"
    }},
    "bottom": {{
      "type": "recommended clothing type",
      "season": ["season labels"],
      "color": ["color directions"],
      "texture": ["fabric or texture keywords"],
      "style": ["style keywords"],
      "reason": "why this category fits the weather"
    }},
    "shoes": {{
      "type": "recommended footwear type",
      "season": ["season labels"],
      "color": ["color directions"],
      "texture": ["material keywords"],
      "style": ["style keywords"],
      "reason": "why this category fits the weather"
    }}
  }}
}}

Rules:
1. Output JSON only. No markdown.
2. Use all three categories: top, bottom, shoes.
3. Make the recommendation practical for the weather and location.
4. Prefer characteristics that can be matched against the wardrobe summary.
5. Keep summary under 30 words.
""".strip()

async def get_llm_recommendation(
    weather: WeatherInfo,
    seasons: list[str],
    tops: list[dict[str, object]],
    bottoms: list[dict[str, object]],
    shoes: list[dict[str, object]],
) -> dict[str, Any]:
    raw = await chat_completion(
        [
            {
                "role": "system",
                "content": (
                    "You are a clothing recommendation engine. "
                    "Always return valid JSON matching the requested schema."
                ),
            },
            {
                "role": "user",
                "content": build_recommendation_prompt(weather, seasons, tops, bottoms, shoes),
            },
        ],
        temperature=0.2,
    )
    return parse_recommendation_payload(raw)


def parse_recommendation_payload(payload: str | dict[str, Any]) -> dict[str, Any]:
    data = json.loads(payload) if isinstance(payload, str) else payload
    if not isinstance(data, dict):
        raise ValueError("Recommendation response must be a JSON object")

    recommendations = data.get("recommendations")
    if not isinstance(recommendations, dict):
        raise ValueError("Recommendation response missing recommendations")

    normalized: dict[str, Any] = {
        "summary": str(data.get("summary", "")).strip(),
        "weather_focus": _normalize_list(data.get("weather_focus")),
        "recommendations": {},
    }

    for category in RECOMMENDATION_CATEGORIES:
        entry = recommendations.get(category)
        if not isinstance(entry, dict):
            raise ValueError(f"Recommendation response missing {category}")

        normalized["recommendations"][category] = {
            "type": _normalize_text(entry.get("type")),
            "season": _normalize_list(entry.get("season")),
            "color": _normalize_list(entry.get("color")),
            "texture": _normalize_list(entry.get("texture")),
            "style": _normalize_list(entry.get("style")),
            "reason": str(entry.get("reason", "")).strip(),
        }

    return normalized


def score_clothing_match(item: dict[str, object], criteria: dict[str, Any], fallback_seasons: list[str]) -> int:
    score = 0
    haystacks = [
        _normalize_text(item.get("item")),
        _normalize_text(item.get("color_semantics")),
        _normalize_text(item.get("description")),
        " ".join(_normalize_list(item.get("style_semantics"))),
        " ".join(_normalize_list(item.get("season_semantics"))),
        " ".join(_normalize_list(item.get("usage_semantics"))),
    ]

    item_type = haystacks[0]
    if criteria.get("type") and criteria["type"] in item_type:
        score += 5

    item_seasons = set(_normalize_list(item.get("season_semantics")))
    desired_seasons = set(criteria.get("season") or fallback_seasons)
    score += len(item_seasons & desired_seasons) * 3

    item_color = haystacks[1]
    for color in criteria.get("color", []):
        if color and color in item_color:
            score += 2

    style_text = " ".join(haystacks)
    for style in criteria.get("style", []):
        if style and style in style_text:
            score += 2

    for texture in criteria.get("texture", []):
        if texture and texture in style_text:
            score += 2

    if score == 0 and not item_seasons and not item_color:
        score = 1

    return score


def build_recommendation_text(
    recommendation: dict[str, Any],
    *,
    top: dict[str, object] | None,
    bottom: dict[str, object] | None,
    shoes: dict[str, object] | None,
) -> str:
    summary = str(recommendation.get("summary", "")).strip()
    if summary:
        return summary
    chosen_items = [item.get("item") for item in (top, bottom, shoes) if item and item.get("item")]
    if chosen_items:
        return f"Selected: {', '.join(chosen_items)}."
    return "No recommendation available."


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
