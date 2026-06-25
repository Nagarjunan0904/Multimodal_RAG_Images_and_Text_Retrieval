from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = Field(default=None, validation_alias="QDRANT_API_KEY")
    image_collection: str = "image_index"
    text_collection: str = "text_index"
    colpali_model: str = "vidore/colpali-v1.2"
    embed_device: str = "cuda"
    generation_model: str = "gpt-5.4-mini-2026-03-17"
    hf_home: str = Field(
        default="D:/AI_ML/Models/huggingface_cache",
        validation_alias="HF_HOME",
    )

    model_config = SettingsConfigDict(
        env_file=Path(".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )
