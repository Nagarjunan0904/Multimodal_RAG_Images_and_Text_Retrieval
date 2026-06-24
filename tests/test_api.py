import importlib
import sys
import types
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from backend.models.schemas import GenerationResponse, RetrievalResult


@pytest.fixture
def client(monkeypatch) -> TestClient:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setitem(sys.modules, "backend.qdrant_client", _qdrant_client_module())
    monkeypatch.setitem(sys.modules, "backend.retriever", _retriever_module())
    monkeypatch.setitem(sys.modules, "backend.generator", _generator_module())
    monkeypatch.setitem(sys.modules, "eval.logger", _logger_module())
    sys.modules.pop("backend.main", None)

    main = importlib.import_module("backend.main")
    return TestClient(main.app)


def test_ingest_endpoint(client: TestClient) -> None:
    response = client.post(
        "/ingest",
        files={"file": ("test.pdf", b"%PDF-1.4 fake pdf", "application/pdf")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["doc_id"]
    assert body["num_pages"] == 1
    assert body["num_chunks"] == 2


def test_query_endpoint(client: TestClient) -> None:
    response = client.post(
        "/query",
        json={"query": "What does the figure show?", "doc_id": "doc"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["answer"]
    assert "sources" in body
    assert "latency_ms" in body
    assert "used_image" in body


def test_documents_endpoint(client: TestClient) -> None:
    response = client.get("/documents")

    assert response.status_code == 200
    assert response.json() == {"documents": ["doc", "other-doc"]}


def test_eval_endpoint(client: TestClient) -> None:
    response = client.get("/eval")

    assert response.status_code == 200
    assert "total_queries" in response.json()


def _qdrant_client_module() -> types.ModuleType:
    class FakeQdrant:
        def scroll(self, *args, **kwargs):
            if kwargs.get("scroll_filter") is not None:
                return [SimpleNamespace(payload={"doc_id": "doc"})], None

            return [
                SimpleNamespace(payload={"doc_id": "doc"}),
                SimpleNamespace(payload={"doc_id": "other-doc"}),
                SimpleNamespace(payload={"doc_id": "doc"}),
            ], None

    module = types.ModuleType("backend.qdrant_client")
    module.get_qdrant_client = lambda settings=None: FakeQdrant()
    module.ensure_collections = lambda client: None
    return module


def _retriever_module() -> types.ModuleType:
    class FakeRetriever:
        def __init__(self, qdrant_client, settings):
            return None

        def retrieve(self, query, top_k=5, doc_id=None):
            return RetrievalResult(
                top_pages=[
                    {
                        "page_num": 1,
                        "doc_id": doc_id,
                        "score": 0.9,
                        "image_path": "missing.png",
                    }
                ],
                top_chunks=[
                    {
                        "chunk_id": "doc_p1_c0",
                        "text": "Example text.",
                        "score": 0.8,
                        "doc_id": doc_id,
                        "page_num": 1,
                    }
                ],
            )

    module = types.ModuleType("backend.retriever")
    module.MultimodalRetriever = FakeRetriever
    module.ingest_and_index = lambda file_bytes, doc_id, qdrant, settings: {
        "num_pages": 1,
        "num_chunks": 2,
    }
    return module


def _generator_module() -> types.ModuleType:
    async def fake_generate_answer(query, retrieval_result, stream=False):
        return GenerationResponse(
            answer="Generated answer.",
            sources=[{"page_num": 1, "doc_id": "doc"}],
            used_image=False,
        )

    module = types.ModuleType("backend.generator")
    module.generate_answer = fake_generate_answer
    return module


def _logger_module() -> types.ModuleType:
    class FakeLogger:
        def __init__(self, db_path):
            self.db_path = db_path

        def log(self, *args, **kwargs):
            return None

        def get_stats(self):
            return {
                "total_queries": 1,
                "avg_latency": 12.0,
                "pct_queries_using_image": 0.0,
                "avg_image_score": 0.9,
                "avg_text_score": 0.8,
            }

    module = types.ModuleType("eval.logger")
    module.EvalLogger = FakeLogger
    return module
