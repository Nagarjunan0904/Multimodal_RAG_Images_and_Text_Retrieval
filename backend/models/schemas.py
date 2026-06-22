from pathlib import Path

from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    file_path: Path | None = None


class IngestResponse(BaseModel):
    doc_id: str = ""
    num_pages: int = 0
    num_chunks: int = 0


class QueryRequest(BaseModel):
    query: str = ""
    top_k: int = Field(default=5, ge=1)


class Source(BaseModel):
    doc_id: str = ""
    page_num: int | None = None
    score: float | None = None


class QueryResponse(BaseModel):
    answer: str = ""
    sources: list[Source] = Field(default_factory=list)
    latency_ms: int = 0
