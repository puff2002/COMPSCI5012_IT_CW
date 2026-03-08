"""
API 配置模型
"""
from pydantic import BaseModel
from typing import Optional, List, Literal


class LLMConfig(BaseModel):
    """应用配置（保留字段供后续接入）"""
    api_base: str = ""
    api_key: str = ""
    model: str = ""
    # remove.bg 配置
    removebg_api_key: str = ""
    bg_removal_method: Literal["local", "removebg"] = "removebg"  # 本地 rembg 或 remove.bg API
    # 和风天气 API 配置
    qweather_api_key: str = ""
    qweather_api_host: str = "devapi.qweather.com"  # 免费版: devapi.qweather.com | 付费版: api.qweather.com
    
    
class LLMConfigUpdate(BaseModel):
    """更新配置的请求体"""
    api_base: Optional[str] = None
    api_key: Optional[str] = None
    model: Optional[str] = None
    removebg_api_key: Optional[str] = None
    bg_removal_method: Optional[Literal["local", "removebg"]] = None
    qweather_api_key: Optional[str] = None
    qweather_api_host: Optional[str] = None


class AvailableModel(BaseModel):
    """可用模型"""
    id: str
    name: str
    

class ModelListResponse(BaseModel):
    """模型列表响应"""
    models: List[AvailableModel]
