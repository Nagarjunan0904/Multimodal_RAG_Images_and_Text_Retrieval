import sys
import types
from types import SimpleNamespace
from unittest.mock import MagicMock

import torch
from PIL import Image

from backend.retriever import MultimodalIndexer, MultimodalRetriever, retrieve


def _indexer() -> MultimodalIndexer:
    indexer = MultimodalIndexer.__new__(MultimodalIndexer)
    indexer.qdrant_client = MagicMock()
    indexer.settings = SimpleNamespace(
        embed_device="cpu",
        image_collection="image_index",
        text_collection="text_index",
    )
    indexer.processor = MagicMock()
    indexer.processor.process_images.return_value = {"pixel_values": torch.zeros(1, 3, 8, 8)}
    indexer.model = MagicMock(return_value=torch.ones(1, 4, 128))
    indexer.embed_model = MagicMock()
    indexer.embed_model.get_text_embedding.return_value = [0.1] * 1024
    return indexer


def test_retrieve_stub() -> None:
    assert retrieve("example query") == []


def test_index_page_image_calls_qdrant_upsert_once() -> None:
    indexer = _indexer()
    image = Image.new("RGB", (8, 8), color="white")

    indexer.index_page_image(
        image=image,
        doc_id="doc",
        page_num=1,
        image_path=str("tmp"),
    )

    indexer.qdrant_client.upsert.assert_called_once()


def test_index_text_chunk_calls_qdrant_upsert_once() -> None:
    indexer = _indexer()
    chunk = {
        "page_num": 1,
        "chunk_id": "doc_p1_c0",
        "text": "Example text chunk.",
    }

    indexer.index_text_chunk(chunk=chunk, doc_id="doc")

    indexer.qdrant_client.upsert.assert_called_once()


def test_retrieve_images_returns_results_sorted_by_descending_score(monkeypatch) -> None:
    _mock_colpali(monkeypatch)
    retriever = MultimodalRetriever(
        qdrant_client=_qdrant_client(),
        settings=_retriever_settings(),
    )

    results = retriever.retrieve_images("example query")

    assert [result["score"] for result in results] == [0.92, 0.81, 0.7]


def test_retrieve_images_result_dicts_contain_expected_keys(monkeypatch) -> None:
    _mock_colpali(monkeypatch)
    retriever = MultimodalRetriever(
        qdrant_client=_qdrant_client(),
        settings=_retriever_settings(),
    )

    results = retriever.retrieve_images("example query")

    assert results
    assert all(
        set(result) == {"page_num", "image_path", "score", "doc_id"}
        for result in results
    )


def _mock_colpali(monkeypatch) -> None:
    class FakeColPali:
        @classmethod
        def from_pretrained(cls, *args, **kwargs):
            return cls()

        def eval(self) -> None:
            return None

        def __call__(self, **inputs):
            assert inputs["input_ids"].dtype == torch.bfloat16
            return torch.tensor(
                [
                    [
                        [0.1, 0.2, 0.3],
                        [0.4, 0.5, 0.6],
                    ]
                ],
                dtype=torch.bfloat16,
            )

    class FakeColPaliProcessor:
        @classmethod
        def from_pretrained(cls, *args, **kwargs):
            return cls()

        def process_queries(self, queries):
            return {"input_ids": torch.ones(1, 2, 3)}

    models_module = types.ModuleType("colpali_engine.models")
    models_module.ColPali = FakeColPali
    models_module.ColPaliProcessor = FakeColPaliProcessor

    package_module = types.ModuleType("colpali_engine")
    package_module.models = models_module

    monkeypatch.setitem(sys.modules, "colpali_engine", package_module)
    monkeypatch.setitem(sys.modules, "colpali_engine.models", models_module)


def _qdrant_client() -> MagicMock:
    client = MagicMock()
    client.query_points.return_value = SimpleNamespace(
        points=[
            SimpleNamespace(
                payload={
                    "page_num": 3,
                    "image_path": "page_3.png",
                    "doc_id": "doc",
                },
                score=0.92,
            ),
            SimpleNamespace(
                payload={
                    "page_num": 1,
                    "image_path": "page_1.png",
                    "doc_id": "doc",
                },
                score=0.81,
            ),
            SimpleNamespace(
                payload={
                    "page_num": 2,
                    "image_path": "page_2.png",
                    "doc_id": "doc",
                },
                score=0.7,
            ),
        ]
    )
    return client


def _retriever_settings() -> SimpleNamespace:
    return SimpleNamespace(
        colpali_model="fake-colpali",
        embed_device="cpu",
        image_collection="image_index",
    )
