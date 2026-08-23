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

    otel_sampling_ratio: float = 1.0

    otel_console_exporter: bool = False

    langfuse_enabled: bool = False
    langfuse_public_key: str | None = None
    langfuse_secret_key: str | None = None
    langfuse_base_url: str | None = None
    langfuse_capture_content: bool = False

    knowledge_chunk_size: int = 1000

    knowledge_chunk_overlap: int = 200
    
    knowledge_storage_directory: str = "data/knowledge"

    # ---------------------------------------------------------
    # Chroma
    # ---------------------------------------------------------

    knowledge_chroma_directory: str = "./data/chroma"

    knowledge_bm25_directory: str = "./data/bm25"

    knowledge_collection_name: str = "knowledge"

    # ---------------------------------------------------------
    # Embeddings
    # ---------------------------------------------------------

    openai_embedding_model: str = "text-embedding-3-small"

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

    # ---------------------------------------------------------
    # Retrieval
    # ---------------------------------------------------------

    knowledge_retrieval_top_k: int = 5

    # Hybrid retrieval uses rank fusion, so this is the number of candidates
    # independently requested from Chroma and BM25 before final Top-K fusion.
    knowledge_hybrid_candidate_k: int = 50

    knowledge_hybrid_rrf_rank_constant: int = 60

    knowledge_rerank_enabled: bool = True

    knowledge_rerank_top_k: int = 20

    knowledge_rerank_model: str = "cross-encoder/stsb-roberta-base"

    knowledge_similarity_threshold: float = 0.75

    knowledge_max_context_chunks: int = 5

    # Maximum accepted upload size (25 MiB) to bound parsing/indexing cost.
    knowledge_upload_max_size_bytes: int = 26_214_400

    # Approximate input-context budget. Context assembly estimates tokens as
    # four thirds of whitespace-delimited words; it is not model tokenization.
    knowledge_context_max_tokens: int = 4_000

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
