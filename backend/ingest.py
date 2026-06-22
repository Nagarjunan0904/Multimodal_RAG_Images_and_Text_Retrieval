from pathlib import Path

from backend.models.schemas import IngestResponse


def ingest_document(file_path: Path | None = None) -> IngestResponse:
    return IngestResponse()
