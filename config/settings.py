from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    azure_openai_api_key: str
    azure_openai_endpoint: str
    azure_openai_api_version: str = "2024-12-01-preview"
    azure_openai_chat_deployment: str = "gpt-5-mini"
    azure_openai_mini_deployment: str = "gpt-5-nano"
    azure_openai_embedding_deployment: str = "text-embedding-3-small"

    azure_search_endpoint: str
    azure_search_key: str
    azure_search_index: str = "customer-support-index"

    routing_confidence_threshold: float = 0.7
    escalation_confidence_threshold: float = 0.5
    max_turns: int = 5
    max_cost_per_query: float = 0.10

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()