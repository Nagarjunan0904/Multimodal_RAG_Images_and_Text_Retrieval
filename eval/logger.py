from datetime import datetime
from pathlib import Path
import sqlite3

from backend.models.schemas import RetrievalResult


class EvalLogger:
    def __init__(self, db_path: str | Path = "eval.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._create_table()

    def log(
        self,
        query: str,
        doc_id: str,
        retrieval_result: RetrievalResult,
        latency_ms: float,
        used_image: bool,
    ) -> None:
        top_page = retrieval_result.top_pages[0] if retrieval_result.top_pages else None
        top_chunk = retrieval_result.top_chunks[0] if retrieval_result.top_chunks else None

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO eval_log (
                    timestamp,
                    query,
                    doc_id,
                    top_image_page,
                    image_score,
                    top_text_chunk_id,
                    text_score,
                    latency_ms,
                    used_image_in_answer
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    datetime.utcnow().isoformat(),
                    query,
                    doc_id,
                    top_page["page_num"] if top_page else None,
                    top_page["score"] if top_page else None,
                    top_chunk["chunk_id"] if top_chunk else None,
                    top_chunk["score"] if top_chunk else None,
                    latency_ms,
                    1 if used_image else 0,
                ),
            )

    def get_stats(self) -> dict:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                """
                SELECT
                    COUNT(*) AS total_queries,
                    AVG(latency_ms) AS avg_latency,
                    AVG(used_image_in_answer) * 100.0 AS pct_queries_using_image,
                    AVG(image_score) AS avg_image_score,
                    AVG(text_score) AS avg_text_score
                FROM eval_log
                """
            ).fetchone()

        return {
            "total_queries": int(row[0]),
            "avg_latency": float(row[1] or 0.0),
            "pct_queries_using_image": float(row[2] or 0.0),
            "avg_image_score": float(row[3] or 0.0),
            "avg_text_score": float(row[4] or 0.0),
        }

    def _create_table(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS eval_log (
                    id INTEGER PRIMARY KEY,
                    timestamp TEXT,
                    query TEXT,
                    doc_id TEXT,
                    top_image_page INTEGER,
                    image_score REAL,
                    top_text_chunk_id TEXT,
                    text_score REAL,
                    latency_ms REAL,
                    used_image_in_answer INTEGER
                )
                """
            )
