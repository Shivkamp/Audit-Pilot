from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    project_name: str = "TaxAudit AI"
    app_version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"

    auth_secret_key: str = "change-me-dev-secret"
    auth_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    password_hash_scheme: str = "bcrypt"
    allow_public_registration: bool = True

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "taxaudit_ai"
    postgres_user: str = "taxaudit_ai"
    postgres_password: str = "taxaudit_ai"
    postgres_echo: bool = False
    database_url_override: str | None = Field(default=None, alias="DATABASE_URL")

    upload_dir: str = "storage/uploads"
    max_upload_size_mb: int = 25
    storage_backend: str = "local"

    max_pdf_size_mb: int = 50
    max_excel_size_mb: int = 100
    max_csv_size_mb: int = 250

    max_pdf_pages: int = 500
    max_excel_rows: int = 200_000
    max_csv_rows: int = 500_000
    max_excel_sheets: int = 20
    max_columns: int = 200

    extraction_batch_size: int = 5000
    extraction_api_default_limit: int = 100
    extraction_api_max_limit: int = 1000
    normalization_batch_size: int = 5000
    normalization_api_default_limit: int = 100
    normalization_api_max_limit: int = 1000
    risk_api_default_limit: int = 100
    risk_api_max_limit: int = 1000
    risk_config_api_default_limit: int = 100
    risk_config_api_max_limit: int = 1000
    knowledge_api_default_limit: int = 20
    knowledge_api_max_limit: int = 100
    knowledge_search_default_limit: int = 5
    knowledge_search_max_limit: int = 20
    agent_retrieval_default_limit: int = 5
    agent_retrieval_max_limit: int = 20
    agent_listing_max_limit: int = 200
    embedding_provider: str = "local_hash"
    embedding_model: str = "local-hash-v1"
    embedding_dimension: int = 384
    retrieval_mode: str = "hybrid"
    retrieval_enable_vector: bool = True
    retrieval_enable_keyword: bool = True
    retrieval_enable_structured: bool = True
    retrieval_fusion_method: str = "rrf"
    rrf_k: int = 60
    mmr_enabled: bool = True
    mmr_lambda: float = 0.70
    mmr_candidate_pool_size: int = 30
    final_evidence_limit: int = 6
    deterministic_rerank_enabled: bool = True
    reranker_provider: str = "none"
    llm_rerank_enabled: bool = False
    llm_rerank_top_n: int = 20
    llm_provider: str = "mock"
    cerebras_api_key: str | None = None
    cerebras_base_url: str = "https://api.cerebras.ai/v1"
    cerebras_model: str = "gpt-oss-120b"
    llm_timeout_seconds: int = 60
    llm_max_retries: int = 2
    llm_temperature: float = 0.1
    llm_max_tokens: int = 1200
    agent_max_evidence: int = 6
    agent_enable_llm_intent_fallback: bool = False
    agent_require_citations: bool = True
    risk_short_deposit_critical_threshold: float = 5000
    default_short_deposit_critical_threshold: float = 5000
    default_high_value_transaction_threshold: float = 100000
    normalization_max_error_samples: int = 20
    classification_sample_record_limit: int = 100
    classification_text_char_limit: int = 20_000
    classification_min_confidence: float = 0.55
    classification_ambiguity_margin: int = 3

    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    aws_region: str = "ap-south-1"
    aws_s3_bucket: str | None = None
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_presigned_url_expiry_seconds: int = 900

    @property
    def database_url(self) -> str:
        if self.database_url_override:
            return self.database_url_override

        return (
            "postgresql+psycopg2://"
            f"{self.postgres_user}:{self.postgres_password}@"
            f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def is_development(self) -> bool:
        return self.environment.strip().lower() in {
            "dev",
            "development",
            "local",
            "test",
            "testing",
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
