"""Application configuration loaded from environment variables and .env."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central settings object used across API, database, RAG, and LLM code."""

    openai_api_key: str | None = None
    openai_base_url: str | None = None
    use_real_llm: bool = False
    model: str = "gpt-4.1-mini"
    debug: bool = True
    data_dir: str = "data"
    database_url: str = "sqlite:///data/knowledge_agent.db"
    max_history_messages: int = 8
    top_k_chunks: int = 3

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
