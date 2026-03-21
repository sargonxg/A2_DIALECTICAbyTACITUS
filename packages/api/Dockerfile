# --- Stage 1: Builder with UV ---
FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
WORKDIR /build
RUN DEBIAN_FRONTEND=noninteractive apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    gcc g++ && rm -rf /var/lib/apt/lists/*
# Copy workspace root
COPY pyproject.toml /build/
COPY README.md /build/
# Copy all workspace packages
COPY packages/ontology /build/packages/ontology
COPY packages/graph /build/packages/graph
COPY packages/extraction /build/packages/extraction
COPY packages/reasoning /build/packages/reasoning
COPY packages/api /build/packages/api
# Install all packages via UV into the venv
RUN uv sync --all-packages --no-dev
# --- Stage 2: Production ---
FROM python:3.12-slim AS production
WORKDIR /app
RUN DEBIAN_FRONTEND=noninteractive apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    curl && rm -rf /var/lib/apt/lists/*
RUN useradd -m -u 1000 dialectica
# Copy the entire venv from builder
COPY --from=builder /build/.venv /app/.venv
# Put venv on PATH
ENV PATH="/app/.venv/bin:$PATH"
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
