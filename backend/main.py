from pathlib import Path
import json
import time
import uuid

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from qdrant_client.models import FieldCondition, Filter, MatchValue

from backend.generator import generate_answer
from backend.models.config import Settings
from backend.models.schemas import IngestResponse, QueryRequest, QueryResponse
from backend.qdrant_client import get_qdrant_client
from backend.retriever import MultimodalRetriever, ingest_and_index
from eval.logger import EvalLogger


app = FastAPI(title="Multimodal RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

settings = Settings()
pages_dir = Path("tmp/pages")
pages_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static/pages", StaticFiles(directory=str(pages_dir)), name="pages")

qdrant = get_qdrant_client(settings)
retriever = MultimodalRetriever(qdrant_client=qdrant, settings=settings)
logger = EvalLogger(db_path=Path("eval.db"))


@app.post("/ingest", response_model=IngestResponse)
async def ingest(file: UploadFile) -> IngestResponse:
    try:
        file_bytes = await file.read()
        doc_id = str(uuid.uuid4())
        result = ingest_and_index(file_bytes, doc_id, qdrant, settings)
        return IngestResponse(
            doc_id=doc_id,
            num_pages=result["num_pages"],
            num_chunks=result["num_chunks"],
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest) -> QueryResponse:
    try:
        if not _doc_id_exists(request.doc_id):
            raise HTTPException(status_code=422, detail="doc_id not found")

        start = time.perf_counter()
        result = retriever.retrieve(request.query, top_k=5, doc_id=request.doc_id)
        gen = await generate_answer(request.query, result, stream=False)
        latency_ms = (time.perf_counter() - start) * 1000
        logger.log(request.query, request.doc_id, result, latency_ms, gen.used_image)

        return QueryResponse(
            answer=gen.answer,
            sources=gen.sources,
            latency_ms=latency_ms,
            used_image=gen.used_image,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/query/stream")
async def query_stream(query: str, doc_id: str) -> StreamingResponse:
    async def event_stream():
        try:
            yield f"data: {json.dumps({'type': 'status', 'content': 'Retrieving relevant pages...'})}\n\n"

            start = time.perf_counter()
            result = retriever.retrieve(query, top_k=5, doc_id=doc_id)

            yield f"data: {json.dumps({'type': 'sources', 'pages': result.top_pages, 'chunks': result.top_chunks})}\n\n"

            token_gen = await generate_answer(query, result, stream=True)
            async for token in token_gen:
                yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

            latency_ms = (time.perf_counter() - start) * 1000
            yield f"data: {json.dumps({'type': 'done', 'latency_ms': round(latency_ms, 2)})}\n\n"
        except Exception as exc:
            yield f"data: {json.dumps({'type': 'error', 'message': str(exc)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/documents")
def documents() -> dict[str, list[str]]:
    doc_ids = set()
    offset = None

    while True:
        points, offset = qdrant.scroll(
            collection_name=settings.image_collection,
            with_payload=True,
            offset=offset,
        )
        doc_ids.update(
            point.payload["doc_id"]
            for point in points
            if point.payload and "doc_id" in point.payload
        )
        if offset is None:
            break

    doc_ids = sorted(doc_ids)
    return {"documents": doc_ids}


@app.get("/eval")
def eval_stats() -> dict:
    return logger.get_stats()


def _doc_id_exists(doc_id: str) -> bool:
    points, _ = qdrant.scroll(
        collection_name=settings.image_collection,
        scroll_filter=Filter(
            must=[
                FieldCondition(
                    key="doc_id",
                    match=MatchValue(value=doc_id),
                )
            ]
        ),
        limit=1,
        with_payload=True,
    )
    return bool(points)


if __name__ == "__main__":
    import sys

    from dotenv import load_dotenv

    from backend.qdrant_client import ensure_collections

    if len(sys.argv) < 2:
        print("Error: missing PDF path. Usage: python -m backend.main <path-to-pdf>")
        raise SystemExit(1)

    load_dotenv()
    ensure_collections(qdrant)

    pdf_path = Path(sys.argv[1])
    file_bytes = pdf_path.read_bytes()

    doc_id = str(uuid.uuid4())
    print(f"doc_id: {doc_id}")

    start = time.perf_counter()
    result = ingest_and_index(file_bytes, doc_id, qdrant, settings)
    elapsed = time.perf_counter() - start

    print(f"Pages indexed:      {result['num_pages']}")
    print(f"Text chunks indexed:{len(result['text_chunks'])}")
    print(f"Time elapsed:       {elapsed:.2f}s")

    img_count = qdrant.count(collection_name=settings.image_collection).count
    txt_count = qdrant.count(collection_name=settings.text_collection).count
    print(f"Qdrant image_index points: {img_count}")
    print(f"Qdrant text_index points:  {txt_count}")
    if img_count < result["num_pages"]:
        print(f"WARNING: Expected at least {result['num_pages']} image points, got {img_count}")
    else:
        print(f"image_index OK ({img_count} points)")

    if txt_count < len(result["text_chunks"]):
        print(
            f"WARNING: Expected at least {len(result['text_chunks'])} text points, got {txt_count}"
        )
    else:
        print(f"text_index OK ({txt_count} points)")
