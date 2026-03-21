# ─── Extraction Worker Dockerfile ─────────────────────────────────────────────
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml /build/
COPY packages/ontology /build/packages/ontology
COPY packages/graph /build/packages/graph
COPY packages/extraction /build/packages/extraction
COPY packages/reasoning /build/packages/reasoning
COPY packages/api /build/packages/api

RUN uv sync --all-packages --no-dev

# Pre-download GLiNER model into image cache
RUN python -c "from gliner import GLiNER; GLiNER.from_pretrained('gliner-community/gliner_medium-v2.5')" 2>/dev/null || true

FROM python:3.12-slim AS production

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 dialectica

COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /root/.cache /home/dialectica/.cache 2>/dev/null || true

COPY packages/ontology/src /app/packages/ontology/src
COPY packages/graph/src /app/packages/graph/src
COPY packages/extraction/src /app/packages/extraction/src
COPY packages/reasoning/src /app/packages/reasoning/src
COPY packages/api/src /app/packages/api/src

ENV PYTHONPATH=/app/packages/ontology/src:/app/packages/graph/src:/app/packages/extraction/src:/app/packages/reasoning/src:/app/packages/api/src
ENV PYTHONUNBUFFERED=1

USER dialectica

EXPOSE 8080

CMD ["python", "-m", "dialectica_extraction.pubsub_worker"]
