from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.models.schemas import IngestRequest, IngestResponse, QueryRequest, QueryResponse
from backend.qdrant_client import ensure_collections, get_qdrant_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = get_qdrant_client()
    ensure_collections(client)
    app.state.qdrant_client = client
    yield


app = FastAPI(title="Multimodal RAG API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ingest", response_model=IngestResponse)
def ingest(request: IngestRequest) -> IngestResponse:
    return IngestResponse()


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest) -> QueryResponse:
    return QueryResponse()


@app.get("/documents")
def documents() -> list[Any]:
    return []


@app.get("/eval")
def eval_status() -> dict[str, Any]:
    return {}
