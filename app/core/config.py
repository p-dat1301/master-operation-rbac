from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    POSTGRES_DB: str = "masterop"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    RAG_LLM_GATEWAY_BASE_URL: str = ""
    RAG_LLM_GATEWAY_API_KEY: str = ""
    RAG_ANSWER_MODEL: str = ""
    RAG_ANSWER_TIMEOUT_SECONDS: float = 30.0
    RAG_ANSWER_MAX_CONTEXT_TOKENS: int = 8_000
    RAG_ANSWER_OUTPUT_TOKEN_RESERVE: int = 512
    RAG_RETRIEVAL_STRATEGY: str = "hybrid"
    ELASTICSEARCH_HOST: str = "localhost:9200"
    ELASTICSEARCH_INDEX_NAME: str = "agentic_chunks"
    RAG_USE_ELASTICSEARCH: bool = False

    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ROOT_USER: str = "minio_admin"
    MINIO_ROOT_PASSWORD: str = "minio_admin"
    MINIO_BUCKET: str = "documents"
    MINIO_SECURE: bool = False

    @field_validator("ELASTICSEARCH_HOST")
    @classmethod
    def validate_elasticsearch_host(cls, value: str) -> str:
        if not value or ":" not in value:
            raise ValueError("ELASTICSEARCH_HOST must be in host:port format, e.g. localhost:9200")
        host, port = value.rsplit(":", 1)
        if not host:
            raise ValueError("ELASTICSEARCH_HOST host cannot be empty")
        if not port.isdigit():
            raise ValueError("ELASTICSEARCH_HOST port must be numeric")
        return value

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
