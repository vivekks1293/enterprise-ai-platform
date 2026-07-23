from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    app_name: str = "Enterprise AI Platform"
    app_version: str = "0.1.0"
    environment: str = "development"
    database_url: str
    alembic_database_url: str

    database_echo: bool = False

    database_pool_size: int = 10

    database_max_overflow: int = 20

    # ==========================================
    # JWT Configuration
    # ==========================================

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    openai_api_key: str = Field(alias="OPENAI_API_KEY")

    openai_chat_model: str = Field(
        default="gpt-4.1-mini",
        alias="OPENAI_CHAT_MODEL",
    )

    openai_temperature: float = Field(
        default=0.7,
        alias="OPENAI_TEMPERATURE",
    )

    openai_max_tokens: int = Field(
        default=4096,
        alias="OPENAI_MAX_TOKENS",
    )

    ai_system_prompt: str = """
You are an Enterprise AI Assistant.

You provide accurate, concise and professional responses.

Always answer in Markdown.

If you don't know the answer,
say you don't know instead of making up information.
""".strip()

settings = Settings()