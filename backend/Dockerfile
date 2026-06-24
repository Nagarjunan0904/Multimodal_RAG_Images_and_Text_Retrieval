FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt \
    --extra-index-url https://download.pytorch.org/whl/cpu

COPY backend/ ./backend/
COPY eval/ ./eval/

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
