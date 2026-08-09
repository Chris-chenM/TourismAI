"""配置管理：从 .env 读取，无 .env 时回退到环境变量"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 从 config.py 所在目录向上两级找到 backend/.env
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(_env_path)


class Settings:
    """全局配置单例"""

    # LLM
    llm_base_url: str = os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1")
    llm_api_key: str = os.getenv("LLM_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "deepseek-chat")

    # 高德
    amap_key: str = os.getenv("AMAP_KEY", "")
    mock_amap: bool = os.getenv("MOCK_AMAP", "false").lower() == "true"

    # 运行时覆盖（PUT /api/settings 修改）
    @classmethod
    def update_llm(cls, base_url: str, api_key: str, model: str):
        cls.llm_base_url = base_url
        cls.llm_api_key = api_key
        cls.llm_model = model


settings = Settings()