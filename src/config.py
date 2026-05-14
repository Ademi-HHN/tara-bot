import os
from functools import lru_cache


@lru_cache()
def get_env(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise ValueError(f"Missing required env var: {key}")
    return val


class Config:
    llm_mode: str = os.getenv("LLM_MODE", "anthropic").strip().lower()
    telegram_token: str = os.getenv("TELEGRAM_TOKEN", "")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "")
    serpapi_key: str = os.getenv("SERPAPI_KEY", "")
    allowed_user_id: str = os.getenv("ALLOWED_USER_ID", "")
    affiliate_template = os.getenv("AFFILIATE_TEMPLATE")
