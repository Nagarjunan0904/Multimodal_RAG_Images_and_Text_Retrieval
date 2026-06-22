from types import SimpleNamespace
from unittest.mock import MagicMock

import torch
from PIL import Image

from backend.retriever import MultimodalIndexer, retrieve


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
