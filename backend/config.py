from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


# Project root:
# D:\LegalEaseAI\LegalEase
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "LegalEase"
    company_name: str = "LegalEase"

    backend_url: str = "http://127.0.0.1:8000"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.8-flash"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()