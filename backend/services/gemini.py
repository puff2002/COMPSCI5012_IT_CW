"""
Gemini API 服务
"""
import json
import os
import re

from google import genai
from google.genai import types

from domain.clothes import ClothesSemantics
from domain.prompts import CLOTHES_SEMANTIC_PROMPT


def _get_client():
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise ValueError("GEMINI_API_KEY 未配置")
    return genai.Client(api_key=api_key)


def _get_model_name() -> str:
    return os.getenv("GEMINI_MODEL", "gemini-1.5-flash")


def _extract_json_from_response(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    json_match = re.search(r"```(?:json)?\\s*([\\s\\S]*?)\\s*```", text)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    brace_match = re.search(r"\\{[\\s\\S]*\\}", text)
    if brace_match:
        try:
            return json.loads(brace_match.group())
        except json.JSONDecodeError:
            pass

    raise ValueError(f"无法从响应中提取 JSON: {text}")


def generate_text(prompt: str) -> str:
    client = _get_client()
    response = client.models.generate_content(
        model=_get_model_name(),
        contents=prompt,
    )
    return response.text.strip()


async def analyze_clothes(image_bytes: bytes) -> ClothesSemantics:
    """
    使用 Gemini Vision 分析衣物图片
    """
    client = _get_client()
    response = await client.aio.models.generate_content(
        model=_get_model_name(),
        contents=[
            CLOTHES_SEMANTIC_PROMPT,
            types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
        ],
    )

    result = _extract_json_from_response(response.text)
    return ClothesSemantics(**result)
