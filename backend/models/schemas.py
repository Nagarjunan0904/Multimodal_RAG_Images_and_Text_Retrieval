from pathlib import Path

from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    file_path: Path | None = None


class IngestResponse(BaseModel):
    doc_id: str = ""
    num_pages: int = 0
    num_chunks: int = 0


class QueryRequest(BaseModel):
    query: str
    doc_id: str


class Source(BaseModel):
    doc_id: str = ""
    page_num: int | None = None
    score: float | None = None


class RetrievalResult(BaseModel):
    top_pages: list[dict]
    top_chunks: list[dict]


class GenerationResponse(BaseModel):
    answer: str
    sources: list[dict]
    used_image: bool


class QueryResponse(BaseModel):
    answer: str
    sources: list[dict]
    latency_ms: float
    used_image: bool
