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


if __name__ == "__main__":
    import sys
    import time
    from pathlib import Path
    from uuid import uuid4

    from dotenv import load_dotenv

    from backend.models.config import Settings
    from backend.qdrant_client import ensure_collections, get_qdrant_client
    from backend.retriever import ingest_and_index

    if len(sys.argv) < 2:
        print("Error: missing PDF path. Usage: python -m backend.main <path-to-pdf>")
        raise SystemExit(1)

    load_dotenv()

    client = get_qdrant_client()
    ensure_collections(client)

    pdf_path = Path(sys.argv[1])
    file_bytes = pdf_path.read_bytes()

    doc_id = str(uuid4())
    print(f"doc_id: {doc_id}")

    settings = Settings()
    start = time.perf_counter()
    result = ingest_and_index(file_bytes, doc_id, client, settings)
    elapsed = time.perf_counter() - start

    print(f"Pages indexed:      {result['num_pages']}")
    print(f"Text chunks indexed:{len(result['text_chunks'])}")
    print(f"Time elapsed:       {elapsed:.2f}s")

    img_count = client.count(collection_name=settings.image_collection).count
    txt_count = client.count(collection_name=settings.text_collection).count
    print(f"Qdrant image_index points: {img_count}")
    print(f"Qdrant text_index points:  {txt_count}")
    if img_count < result["num_pages"]:
        print(f"WARNING: Expected at least {result['num_pages']} image points, got {img_count}")
    else:
        print(f"✅ image_index OK ({img_count} points)")

    if txt_count < len(result["text_chunks"]):
        print(
            f"WARNING: Expected at least {len(result['text_chunks'])} text points, got {txt_count}"
        )
    else:
        print(f"✅ text_index OK ({txt_count} points)")
