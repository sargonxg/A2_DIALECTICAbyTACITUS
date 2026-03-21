FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && rm -rf /var/lib/apt/lists/*

COPY packages/ontology /app/packages/ontology
COPY packages/graph /app/packages/graph
COPY packages/extraction /app/packages/extraction
COPY packages/reasoning /app/packages/reasoning
COPY packages/mcp /app/packages/mcp

RUN pip install --no-cache-dir \
    -e packages/ontology \
    -e packages/graph \
    -e packages/extraction \
    -e packages/reasoning \
    -e packages/mcp

FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

RUN useradd -m -u 1000 dialectica
USER dialectica

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/packages/ontology/src:/app/packages/graph/src:/app/packages/extraction/src:/app/packages/reasoning/src:/app/packages/mcp/src

EXPOSE 8090

CMD ["python", "-m", "dialectica_mcp.server"]
