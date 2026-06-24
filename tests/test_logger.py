from pathlib import Path

from backend.models.schemas import RetrievalResult
from eval.logger import EvalLogger


def test_log_inserts_row(tmp_path: Path) -> None:
    logger = EvalLogger(tmp_path / "eval.db")

    logger.log(
        query="example query",
        doc_id="doc",
        retrieval_result=_retrieval_result(image_score=0.9, text_score=0.8),
        latency_ms=100.0,
        used_image=True,
    )

    assert logger.get_stats()["total_queries"] == 1


def test_get_stats_averages(tmp_path: Path) -> None:
    logger = EvalLogger(tmp_path / "eval.db")

    logger.log(
        query="first query",
        doc_id="doc",
        retrieval_result=_retrieval_result(image_score=0.8, text_score=0.6),
        latency_ms=100.0,
        used_image=True,
    )
    logger.log(
        query="second query",
        doc_id="doc",
        retrieval_result=_retrieval_result(image_score=0.6, text_score=0.4),
        latency_ms=300.0,
        used_image=False,
    )

    stats = logger.get_stats()

    assert stats["avg_latency"] == 200.0
    assert stats["avg_image_score"] == 0.7


def test_empty_stats(tmp_path: Path) -> None:
    logger = EvalLogger(tmp_path / "eval.db")

    assert logger.get_stats() == {
        "total_queries": 0,
        "avg_latency": 0.0,
        "pct_queries_using_image": 0.0,
        "avg_image_score": 0.0,
        "avg_text_score": 0.0,
    }


def _retrieval_result(image_score: float, text_score: float) -> RetrievalResult:
    return RetrievalResult(
        top_pages=[
            {
                "page_num": 3,
                "score": image_score,
                "doc_id": "doc",
            }
        ],
        top_chunks=[
            {
                "chunk_id": "doc_p3_c0",
                "text": "Example text.",
                "score": text_score,
                "doc_id": "doc",
                "page_num": 3,
            }
        ],
    )
