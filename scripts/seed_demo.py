import os
from pathlib import Path

import requests


def seed_demo() -> None:
    backend_url = os.environ.get("BACKEND_URL") or os.environ.get(
        "VITE_API_URL",
        "http://localhost:8000",
    )
    pdf_path = Path("demo.pdf")

    if not pdf_path.exists():
        print(f"ERROR: demo PDF not found at {pdf_path.resolve()}")
        return

    try:
        with pdf_path.open("rb") as pdf_file:
            response = requests.post(
                f"{backend_url.rstrip('/')}/ingest",
                files={"file": ("demo.pdf", pdf_file, "application/pdf")},
                timeout=3600,
            )
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"ERROR: failed to seed demo data: {exc}")
        if getattr(exc, "response", None) is not None:
            print(f"Response: {exc.response.text}")
        return

    data = response.json()
    print(f"doc_id: {data['doc_id']}")
    print(f"num_pages: {data['num_pages']}")
    print(f"num_chunks: {data['num_chunks']}")


if __name__ == "__main__":
    seed_demo()
