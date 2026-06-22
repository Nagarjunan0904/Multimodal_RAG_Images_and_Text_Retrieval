from pathlib import Path
from typing import Any

from backend.ingest import ingest_pdf


def test_ingest_returns_correct_structure(minimal_pdf: dict[str, Any]) -> None:
    result = ingest_pdf(minimal_pdf["file_bytes"], minimal_pdf["doc_id"])

    assert set(result.keys()) == {"doc_id", "num_pages", "page_image_paths", "text_chunks"}
    assert result["doc_id"] == minimal_pdf["doc_id"]
    assert result["num_pages"] == 1
    assert isinstance(result["page_image_paths"], list)
    assert isinstance(result["text_chunks"], list)


def test_page_images_saved_to_disk(minimal_pdf: dict[str, Any]) -> None:
    result = ingest_pdf(minimal_pdf["file_bytes"], minimal_pdf["doc_id"])

    assert result["page_image_paths"]
    for image_path in result["page_image_paths"]:
        path = Path(image_path)
        assert path.exists()
        assert path.suffix == ".png"


def test_text_chunks_have_required_fields(minimal_pdf: dict[str, Any]) -> None:
    result = ingest_pdf(minimal_pdf["file_bytes"], minimal_pdf["doc_id"])

    assert result["text_chunks"]
    for chunk in result["text_chunks"]:
        assert set(chunk.keys()) == {"page_num", "chunk_id", "text"}
        assert isinstance(chunk["page_num"], int)
        assert isinstance(chunk["chunk_id"], str)
        assert isinstance(chunk["text"], str)
