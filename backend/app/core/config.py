"""Config management: read from .env, fallback to env vars"""

import os
from pathlib import Path
from dotenv import load_dotenv

_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(_env_path)


class Settings:
    """Global config singleton"""

    llm_base_url: str = os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1")
    llm_api_key: str = os.getenv("LLM_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "deepseek-chat")

    amap_key: str = os.getenv("AMAP_KEY", "")
    mock_amap: bool = os.getenv("MOCK_AMAP", "false").lower() == "true"

    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/tourismai",
    )

    @classmethod
    def update_llm(cls, base_url: str, api_key: str, model: str):
        cls.llm_base_url = base_url
        cls.llm_api_key = api_key
        cls.llm_model = model


settings = Settings()