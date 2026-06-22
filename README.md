# Multimodal RAG — Images + Text Retrieval

This project is a scaffold for a multimodal retrieval-augmented generation system that indexes document images and text chunks, retrieves relevant visual and textual evidence from Qdrant, and generates answers with OpenAI Responses API models.

## Setup

```powershell
.venv\Scripts\Activate.ps1
docker compose up -d
python -m uvicorn backend.main:app --reload
```

The backend reads configuration from `.env` using `pydantic-settings`.

## Daily Workflow

```powershell
.venv\Scripts\Activate.ps1
docker compose up -d
python -m pytest
python -m uvicorn backend.main:app --reload
```

Use `scripts\seed_demo.py` for future demo data loading and `scripts\eval_pipeline.py` for future evaluation runs.
