"""系统设置接口：运行时修改大模型配置"""

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter()


class SettingsRequest(BaseModel):
    """设置请求"""
    base_url: str = "https://api.deepseek.com/v1"
    api_key: str = ""
    model: str = "deepseek-chat"


class SettingsResponse(BaseModel):
    """设置响应（不返回真实密钥）"""
    base_url: str
    api_key_set: bool
    model: str
    amap_mock: bool


@router.put("/api/settings", response_model=SettingsResponse)
async def update_settings(req: SettingsRequest):
    """更新大模型配置（运行时生效，仅存内存，重启后恢复为 .env 中的值）"""
    settings.update_llm(req.base_url, req.api_key, req.model)
    return SettingsResponse(
        base_url=settings.llm_base_url,
        api_key_set=bool(settings.llm_api_key),
        model=settings.llm_model,
        amap_mock=settings.mock_amap,
    )


@router.get("/api/settings", response_model=SettingsResponse)
async def get_settings():
    """查看当前配置"""
    return SettingsResponse(
        base_url=settings.llm_base_url,
        api_key_set=bool(settings.llm_api_key),
        model=settings.llm_model,
        amap_mock=settings.mock_amap,
    )
