import base64
import json
import os
import re
from typing import Sequence

import httpx

from domain.clothes import ClothesSemantics
from domain.prompts import CLOTHES_SEMANTIC_PROMPT


OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_DEFAULT_MODEL = "openai/gpt-4o-mini"


def _resolve_api_base() -> str:
    api_base = os.getenv("OPENROUTER_API_BASE", "").strip() or OPENROUTER_BASE_URL
    return api_base.rstrip("/")


def _resolve_api_key() -> str:
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise ValueError("OpenRouter API key is not configured")
    return api_key


def _resolve_model_name() -> str:
    return os.getenv("OPENROUTER_MODEL", "").strip() or OPENROUTER_DEFAULT_MODEL


def _extract_json(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    fenced_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if fenced_match:
        try:
            return json.loads(fenced_match.group(1))
        except json.JSONDecodeError:
            pass

    brace_match = re.search(r"\{[\s\S]*\}", text)
    if brace_match:
        try:
            return json.loads(brace_match.group(0))
        except json.JSONDecodeError:
            pass

    raise ValueError("Could not parse JSON from model response")


def _headers(api_key: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": os.getenv("OPENROUTER_HTTP_REFERER", "http://localhost"),
        "X-Title": os.getenv("OPENROUTER_APP_TITLE", "Smart Closet"),
    }


async def chat_completion(messages: Sequence[dict[str, object]], temperature: float = 0.3) -> str:
    payload = {
        "model": _resolve_model_name(),
        "messages": list(messages),
        "temperature": temperature,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{_resolve_api_base()}/chat/completions",
            headers=_headers(_resolve_api_key()),
            json=payload,
        )

    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text.strip()
        raise ValueError(f"OpenRouter request failed: {exc.response.status_code} {detail}") from exc

    data = response.json()
    choices = data.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ValueError("OpenRouter response did not include any choices")

    message = choices[0].get("message", {})
    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise ValueError("OpenRouter response did not include message content")
    return content.strip()


async def analyze_clothes(image_bytes: bytes, mime_type: str = "image/png") -> ClothesSemantics:
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    content = [
        {"type": "text", "text": CLOTHES_SEMANTIC_PROMPT},
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:{mime_type};base64,{encoded}",
            },
        },
    ]
    text = await chat_completion(
        [
            {
                "role": "system",
                "content": "You extract structured wardrobe semantics from clothing images. Return JSON only.",
            },
            {
                "role": "user",
                "content": content,
            },
        ],
        temperature=0,
    )
    return ClothesSemantics(**_extract_json(text))
