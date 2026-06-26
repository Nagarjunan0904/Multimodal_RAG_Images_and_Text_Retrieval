"""Benchmark text-only vs multimodal RAG on visual-only questions.

Answers scored manually — run the script, review printed answers, then edit the
'correct' fields in benchmark_results.json before using in README.
"""

import asyncio
import json
from pathlib import Path

from backend.generator import generate_answer
from backend.models.config import Settings
from backend.models.schemas import RetrievalResult
from backend.qdrant_client import get_qdrant_client
from backend.retriever import MultimodalRetriever


DEMO_DOC_ID = "bffb0169-aa17-401e-82d9-2f972556a2b0"
QUESTIONS = [
    "What is the memory bandwidth of H100 SXM5 in TB/sec?",
    "How many texture units does H100 have?",
    "What is the TDP of H100 SXM5?",
    "What is the L2 cache size of H100?",
    "How does the H100 NVLink topology diagram show chip connections?",
    "What manufacturing process node is H100 built on?",
    "What is the register file size per GPU in H100?",
    "How many transistors does H100 have?",
    "What is the memory data rate of H100 SXM5?",
    "What is the peak FP8 Tensor TFLOPS of H100?",
]
RESULTS_PATH = Path("eval") / "benchmark_results.json"


def run_eval() -> dict:
    settings = Settings()
    settings.embed_device = "cpu"
    qdrant = get_qdrant_client(settings)
    retriever = MultimodalRetriever(qdrant_client=qdrant, settings=settings)
    results = {
        "demo_doc_id": DEMO_DOC_ID,
        "questions": [],
    }

    for index, question in enumerate(QUESTIONS, start=1):
        print(f"\nQuestion {index}: {question}")

        text_results = retriever.retrieve_text(question, top_k=3, doc_id=DEMO_DOC_ID)
        text_answer = asyncio.run(
            generate_answer(
                question,
                RetrievalResult(top_pages=[], top_chunks=text_results),
                stream=False,
            )
        )

        multimodal_result = retriever.retrieve(question, top_k=3, doc_id=DEMO_DOC_ID)
        multimodal_answer = asyncio.run(
            generate_answer(question, multimodal_result, stream=False)
        )

        print_answers(text_answer.answer, multimodal_answer.answer)
        results["questions"].append(
            {
                "question": question,
                "text_only_answer": text_answer.answer,
                "multimodal_answer": multimodal_answer.answer,
                "text_only_correct": None,
                "multimodal_correct": None,
            }
        )

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nSaved benchmark results to {RESULTS_PATH}")
    return results


def print_answers(text_only_answer: str, multimodal_answer: str) -> None:
    print("-" * 80)
    print("Pipeline     | Answer")
    print("-" * 80)
    print(f"Text-only    | {text_only_answer}")
    print(f"Multimodal   | {multimodal_answer}")
    print("-" * 80)


if __name__ == "__main__":
    run_eval()
