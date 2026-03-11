from typing import Literal, Optional

from pydantic import BaseModel


class LLMConfig(BaseModel):
    removebg_api_key: str = ""
    bg_removal_method: Literal["local", "removebg"] = "removebg"


class LLMConfigUpdate(BaseModel):
    removebg_api_key: Optional[str] = None
    bg_removal_method: Optional[Literal["local", "removebg"]] = None
