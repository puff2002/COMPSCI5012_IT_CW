import asyncio
import base64
import json
import logging
import os
import re
import urllib.request
from typing import Any, Sequence

import dashscope

from domain.clothes import ClothesSemantics
from domain.prompts import CLOTHES_SEMANTIC_PROMPT


DASHSCOPE_DEFAULT_API_BASE = "https://dashscope.aliyuncs.com/api/v1"
DEFAULT_TEXT_OUTPUT_MODEL = "qwen3.5-flash"
DEFAULT_IMAGE_GENERATION_MODEL = "qwen-image-2.0"
logger = logging.getLogger(__name__)


class ClothesRecognitionError(ValueError):
    """Raised when the image does not contain enough clothing information."""


def _resolve_dashscope_api_key() -> str:
    api_key = os.getenv("DASHSCOPE_API_KEY", "").strip()
    if not api_key:
        raise ValueError("DashScope API key is not configured")
    return api_key


def _resolve_dashscope_api_base() -> str:
    return os.getenv("DASHSCOPE_API_BASE", "").strip() or DASHSCOPE_DEFAULT_API_BASE


def _resolve_text_output_model_name() -> str:
    return os.getenv("TEXT_OUTPUT_MODEL", "").strip() or DEFAULT_TEXT_OUTPUT_MODEL


def _resolve_image_generation_model_name() -> str:
    return os.getenv("IMAGE_GENERATION_MODEL", "").strip() or DEFAULT_IMAGE_GENERATION_MODEL


def _extract_json(text: str) -> dict[str, Any]:
    parsed: Any = None
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        parsed = None
    else:
        if isinstance(parsed, dict):
            return parsed
        logger.warning("Expected JSON object from model but received %s: %s", type(parsed).__name__, text)
        raise ValueError(f"Expected JSON object from model response, got {type(parsed).__name__}")

    fenced_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if fenced_match:
        try:
            parsed = json.loads(fenced_match.group(1))
        except json.JSONDecodeError:
            parsed = None
        else:
            if isinstance(parsed, dict):
                return parsed
            logger.warning("Expected JSON object from fenced model response but received %s: %s", type(parsed).__name__, text)
            raise ValueError(f"Expected JSON object from model response, got {type(parsed).__name__}")

    brace_match = re.search(r"\{[\s\S]*\}", text)
    if brace_match:
        try:
            parsed = json.loads(brace_match.group(0))
        except json.JSONDecodeError:
            parsed = None
        else:
            if isinstance(parsed, dict):
                return parsed

    logger.warning("Failed to parse model response as JSON object: %s", text)
    raise ValueError("Could not parse JSON from model response")


def _get_attr(value: Any, key: str, default: Any = None) -> Any:
    if value is None:
        return default
    if isinstance(value, dict):
        return value.get(key, default)
    return getattr(value, key, default)


def _normalize_message_content(content: object) -> list[dict[str, str]]:
    if isinstance(content, str):
        return [{"text": content}]

    if not isinstance(content, list):
        raise ValueError("Unsupported message content format")

    normalized: list[dict[str, str]] = []
    for part in content:
        if not isinstance(part, dict):
            continue
        part_type = part.get("type")
        if part_type == "text":
            text = part.get("text")
            if isinstance(text, str) and text.strip():
                normalized.append({"text": text})
            continue
        if part_type == "image_url":
            image_url = part.get("image_url")
            if isinstance(image_url, dict):
                url = image_url.get("url")
                if isinstance(url, str) and url.strip():
                    normalized.append({"image": url})
            continue
        if "text" in part and isinstance(part["text"], str):
            normalized.append({"text": part["text"]})
            continue
        if "image" in part and isinstance(part["image"], str):
            normalized.append({"image": part["image"]})
    if not normalized:
        raise ValueError("Unsupported message content format")
    return normalized


def _to_dashscope_messages(messages: Sequence[dict[str, object]]) -> list[dict[str, object]]:
    normalized: list[dict[str, object]] = []
    system_texts: list[str] = []

    for message in messages:
        role = str(message.get("role", "user")).strip() or "user"
        content = message.get("content")
        if role == "system":
            if isinstance(content, str) and content.strip():
                system_texts.append(content.strip())
            continue
        normalized.append(
            {
                "role": role,
                "content": _normalize_message_content(content),
            }
        )

    if system_texts and normalized:
        normalized[0]["content"] = [{"text": "\n\n".join(system_texts)}] + list(normalized[0]["content"])
    return normalized


def _extract_text_from_response(response: Any) -> str:
    output = _get_attr(response, "output", {})
    choices = _get_attr(output, "choices", [])
    if not isinstance(choices, list) or not choices:
        raise ValueError("DashScope response did not include any choices")

    message = _get_attr(choices[0], "message", {})
    content = _get_attr(message, "content", [])
    if not isinstance(content, list) or not content:
        raise ValueError("DashScope response did not include message content")

    texts: list[str] = []
    for entry in content:
        text = _get_attr(entry, "text")
        if isinstance(text, str) and text.strip():
            texts.append(text.strip())

    if not texts:
        raise ValueError("DashScope response did not include text content")
    return "\n".join(texts)


def _extract_generated_image_reference(response: Any) -> str:
    output = _get_attr(response, "output", {})
    choices = _get_attr(output, "choices", [])
    if not isinstance(choices, list) or not choices:
        raise ValueError("Image generation response did not include any choices")

    message = _get_attr(choices[0], "message", {})
    content = _get_attr(message, "content", [])
    if not isinstance(content, list) or not content:
        raise ValueError("Image generation response did not include content")

    for entry in content:
        for key in ("image", "image_url", "url"):
            image_ref = _get_attr(entry, key)
            if isinstance(image_ref, str) and image_ref.strip():
                return image_ref.strip()

    raise ValueError("Image generation response did not include an image output")


def _decode_generated_image(image_ref: str) -> bytes:
    if image_ref.startswith("data:"):
        _, _, payload = image_ref.partition(",")
        if not payload:
            raise ValueError("Image generation response returned an empty data URL")
        return base64.b64decode(payload)

    if image_ref.startswith("http://") or image_ref.startswith("https://"):
        with urllib.request.urlopen(image_ref, timeout=60) as response:
            return response.read()

    try:
        return base64.b64decode(image_ref)
    except Exception as exc:
        raise ValueError("Failed to decode generated image output") from exc


def _call_multimodal(messages: Sequence[dict[str, object]], *, model: str) -> Any:
    dashscope.base_http_api_url = _resolve_dashscope_api_base()
    response = dashscope.MultiModalConversation.call(
        api_key=_resolve_dashscope_api_key(),
        model=model,
        messages=_to_dashscope_messages(messages),
    )

    status_code = _get_attr(response, "status_code")
    if status_code not in (None, 200):
        raise ValueError(
            "DashScope request failed: "
            f"{status_code} {json.dumps(_get_attr(response, 'output', {}), ensure_ascii=False, default=str)}"
        )
    return response


async def chat_completion(messages: Sequence[dict[str, object]], temperature: float = 0.3) -> str:
    del temperature
    response = await asyncio.to_thread(
        _call_multimodal,
        messages,
        model=_resolve_text_output_model_name(),
    )
    return _extract_text_from_response(response)


async def edit_image_remove_background(image_bytes: bytes, mime_type: str = "image/png") -> bytes:
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    response = await asyncio.to_thread(
        _call_multimodal,
        [
            {
                "role": "user",
                "content": [
                    {"image": f"data:{mime_type};base64,{encoded}"},
                    {
                        "text": (
                            "Remove the background completely from this clothing image. "
                            "Keep only the clothing item and exclude everything else. "
                            "Crop tightly so only the garment remains visible, centered in frame. "
                            "Preserve the garment shape, texture, and colors. "
                            "Return a transparent square image intended for 512x512 output. "
                            "Do not add props, mannequins, people, shadows, floor, or extra empty scene content."
                        )
                    },
                ],
            }
        ],
        model=_resolve_image_generation_model_name(),
    )
    return _decode_generated_image(_extract_generated_image_reference(response))


async def generate_image(prompt: str, size: str = "1024x1024") -> bytes:
    del size
    response = await asyncio.to_thread(
        _call_multimodal,
        [
            {
                "role": "user",
                "content": [{"text": f"{prompt}\n\nRender as a square 512x512 image."}],
            }
        ],
        model=_resolve_image_generation_model_name(),
    )
    return _decode_generated_image(_extract_generated_image_reference(response))


async def analyze_clothes(image_bytes: bytes, mime_type: str = "image/png") -> ClothesSemantics:
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    text = await chat_completion(
        [
            {
                "role": "system",
                "content": "You extract structured wardrobe semantics from clothing images. Return JSON only.",
            },
            {
                "role": "user",
                "content": [
                    {"image": f"data:{mime_type};base64,{encoded}"},
                    {"text": CLOTHES_SEMANTIC_PROMPT},
                ],
            },
        ],
        temperature=0,
    )
    try:
        semantics = ClothesSemantics(**_extract_json(text))
    except Exception:
        logger.exception("Failed to parse clothes semantics from model response: %s", text)
        raise
    if not semantics.detected:
        raise ClothesRecognitionError("No clothing item detected in the image")
    return semantics
