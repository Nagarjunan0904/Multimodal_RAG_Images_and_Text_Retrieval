from pathlib import Path

from backend.ingest import ingest_document


def test_ingest_document_stub() -> None:
    response = ingest_document(Path("demo.pdf"))

    assert response.doc_id == ""
    assert response.num_pages == 0
    assert response.num_chunks == 0
