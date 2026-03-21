# ─── Stage 1: Builder with UV ─────────────────────────────────────────────────
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ && rm -rf /var/lib/apt/lists/*

# Copy all workspace packages
COPY pyproject.toml /build/
COPY README.md /build/
COPY packages/ontology /build/packages/ontology
COPY packages/graph /build/packages/graph
COPY packages/extraction /build/packages/extraction
COPY packages/reasoning /build/packages/reasoning
COPY packages/api /build/packages/api

# Install all packages via UV
RUN uv sync --all-packages --no-dev

# ─── Stage 2: Production ──────────────────────────────────────────────────────
FROM python:3.12-slim AS production

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 dialectica

COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=builder /usr/local/bin /usr/local/bin

COPY packages/ontology/src /app/packages/ontology/src
COPY packages/graph/src /app/packages/graph/src
COPY packages/extraction/src /app/packages/extraction/src
COPY packages/reasoning/src /app/packages/reasoning/src
COPY packages/api/src /app/packages/api/src

ENV PYTHONPATH=/app/packages/ontology/src:/app/packages/graph/src:/app/packages/extraction/src:/app/packages/reasoning/src:/app/packages/api/src
ENV PYTHONUNBUFFERED=1

USER dialectica

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

EXPOSE 8080

CMD ["uvicorn", "dialectica_api.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8080", \
     "--workers", "4", \
     "--timeout-keep-alive", "30"]
