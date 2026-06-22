from pathlib import Path
from typing import Any

import pypdfium2 as pdfium
from llama_index.core.node_parser import SentenceSplitter

from backend.models.schemas import IngestResponse


def ingest_pdf(file_bytes: bytes, doc_id: str) -> dict[str, Any]:
    pdf = pdfium.PdfDocument(file_bytes)
    splitter = SentenceSplitter(chunk_size=512, chunk_overlap=64)
    page_dir = Path("tmp") / "pages" / doc_id
    page_dir.mkdir(parents=True, exist_ok=True)

    page_image_paths: list[str] = []
    text_chunks: list[dict[str, Any]] = []

    try:
        for page_index in range(len(pdf)):
            page_num = page_index + 1
            page = pdf[page_index]

            try:
                image = page.render(scale=150 / 72).to_pil()
                image_path = page_dir / f"page_{page_num}.png"
                image.save(image_path)
                image.close()
                page_image_paths.append(str(image_path))

                textpage = page.get_textpage()
                try:
                    char_count = textpage.count_chars()
                    text = textpage.get_text_range(index=0, count=char_count) if char_count else ""
                finally:
                    textpage.close()

                for chunk_index, chunk_text in enumerate(splitter.split_text(text)):
                    text_chunks.append(
                        {
                            "page_num": page_num,
                            "chunk_id": f"{doc_id}_p{page_num}_c{chunk_index}",
                            "text": chunk_text,
                        }
                    )
            finally:
                page.close()
    finally:
        pdf.close()

    return {
        "doc_id": doc_id,
        "num_pages": len(page_image_paths),
        "page_image_paths": page_image_paths,
        "text_chunks": text_chunks,
    }


def ingest_document(file_path: Path | None = None) -> IngestResponse:
    return IngestResponse()
