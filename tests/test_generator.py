import sys
import types
from pathlib import Path
from types import SimpleNamespace

import pytest
from PIL import Image

from backend.generator import generate_answer
from backend.models.schemas import GenerationResponse, RetrievalResult


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_generate_answer_non_stream(tmp_path: Path, monkeypatch) -> None:
    _mock_openai(monkeypatch)
    image_path = tmp_path / "page.png"
    Image.new("RGB", (8, 8), color="white").save(image_path)

    response = await generate_answer(
        query="What does the figure show?",
        retrieval_result=_retrieval_result(image_path=image_path),
    )

    assert isinstance(response, GenerationResponse)
    assert response.answer
    assert response.used_image is True
    assert response.sources == [{"page_num": 3, "doc_id": "doc"}]


@pytest.mark.anyio
async def test_generate_answer_no_image(monkeypatch) -> None:
    _mock_openai(monkeypatch)

    response = await generate_answer(
        query="What does the document say?",
        retrieval_result=RetrievalResult(
            top_pages=[],
            top_chunks=[
                {
                    "chunk_id": "doc_p3_c0",
                    "text": "Example text.",
                    "score": 0.9,
                    "doc_id": "doc",
                    "page_num": 3,
                }
            ],
        ),
    )

    assert response.used_image is False


def _mock_openai(monkeypatch) -> None:
    class FakeResponses:
        async def create(self, *args, **kwargs):
            return SimpleNamespace(output_text="Generated answer.")

    class FakeAsyncOpenAI:
        def __init__(self):
            self.responses = FakeResponses()

    openai_module = types.ModuleType("openai")
    openai_module.AsyncOpenAI = FakeAsyncOpenAI
    monkeypatch.setitem(sys.modules, "openai", openai_module)


def _retrieval_result(image_path: Path) -> RetrievalResult:
    return RetrievalResult(
        top_pages=[
            {
                "page_num": 3,
                "score": 0.9,
                "doc_id": "doc",
                "image_path": str(image_path),
            }
        ],
        top_chunks=[
            {
                "chunk_id": "doc_p3_c0",
                "text": "Example text.",
                "score": 0.8,
                "doc_id": "doc",
                "page_num": 3,
            }
        ],
    )
