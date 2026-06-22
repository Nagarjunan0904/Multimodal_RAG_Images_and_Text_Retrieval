import ctypes
import shutil
from pathlib import Path
from typing import Any

import pypdfium2 as pdfium
import pypdfium2.raw as pdfium_raw
import pytest


@pytest.fixture
def minimal_pdf(tmp_path: Path) -> dict[str, Any]:
    doc_id = "test_doc"
    output_dir = Path("tmp") / "pages" / doc_id
    pdf_path = tmp_path / "minimal.pdf"

    doc = pdfium.PdfDocument.new()
    page = doc.new_page(612, 792)

    text_object = pdfium_raw.FPDFPageObj_NewTextObj(doc.raw, b"Helvetica", 12.0)
    text_buffer = ctypes.create_unicode_buffer("Hello from a pypdfium2 fixture PDF.")
    pdfium_raw.FPDFText_SetText(
        text_object,
        ctypes.cast(text_buffer, pdfium_raw.FPDF_WIDESTRING),
    )
    pdfium_raw.FPDFPageObj_Transform(text_object, 1, 0, 0, 1, 72, 720)
    pdfium_raw.FPDFPage_InsertObject(page.raw, text_object)
    pdfium_raw.FPDFPage_GenerateContent(page.raw)

    doc.save(pdf_path)
    page.close()
    doc.close()

    yield {"file_bytes": pdf_path.read_bytes(), "doc_id": doc_id}

    if output_dir.exists():
        shutil.rmtree(output_dir)
