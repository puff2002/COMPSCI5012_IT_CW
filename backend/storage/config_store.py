import json
from pathlib import Path
from typing import Optional

from domain.config import LLMConfig

CONFIG_FILE = Path(__file__).parent / "llm_config.json"


def load_config() -> LLMConfig:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return LLMConfig(**data)
        except Exception:
            pass
    return LLMConfig()


def save_config(config: LLMConfig) -> None:
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config.model_dump(), f, indent=2, ensure_ascii=False)


def update_config(
    removebg_api_key: Optional[str] = None,
    bg_removal_method: Optional[str] = None
) -> LLMConfig:
    config = load_config()
    if removebg_api_key is not None:
        config.removebg_api_key = removebg_api_key.strip()
    if bg_removal_method is not None:
        config.bg_removal_method = bg_removal_method
    save_config(config)
    return config


def _mask_key(key: str) -> str:
    if not key:
        return ""
    if len(key) > 8:
        return key[:4] + "*" * (len(key) - 8) + key[-4:]
    return "*" * len(key)


def get_masked_config() -> dict:
    config = load_config()
    return {
        "removebg_api_key_masked": _mask_key(config.removebg_api_key),
        "has_removebg_key": bool(config.removebg_api_key),
        "bg_removal_method": config.bg_removal_method,
    }
