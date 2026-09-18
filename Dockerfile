FROM python:3.11-slim

WORKDIR /app

# System deps for pymupdf/pillow wheels build faster with these present;
# slim images usually have wheels available, but keep this in case a
# platform needs to build from source.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir -e ".[web]"

ENV PRR_WEB_HOST=0.0.0.0

EXPOSE 8000

CMD ["sh", "-c", "uvicorn prr_readiness.web:app --host 0.0.0.0 --port ${PORT:-8000}"]
