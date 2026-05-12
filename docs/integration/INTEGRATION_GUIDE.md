# Integration Guide

How DIALECTICA actually calls AGON and KAIROS — code shape, feature flags, configuration, testing.

> **Status.** Target state. Stub clients exist or are planned under `packages/integrations/`. Wiring proceeds per [`ROADMAP.md`](./ROADMAP.md).

---

## Configuration

### Environment variables

```bash
# KAIROS
KAIROS_ENABLED=false                                # master switch
KAIROS_URL=https://kairos-internal.tacitus.me
KAIROS_AUTH_HEADER="Bearer <iam-token-or-key>"
KAIROS_TIMEOUT_SECONDS=30
KAIROS_HARD_TIMEOUT_SECONDS=60
KAIROS_CONTRACTS_RANGE=">=1.0.0,<2.0.0"

# AGON
AGON_ENABLED=false
AGON_URL=https://agon-internal.tacitus.me
AGON_AUTH_HEADER="Basic <base64>"
AGON_TIMEOUT_SECONDS=30
AGON_HARD_TIMEOUT_SECONDS=60
AGON_CONTRACTS_RANGE=">=1.0.0,<2.0.0"

# Pipeline flags
EXTRACTION_USE_KAIROS=false        # pre-pass enabled?
EXTRACTION_USE_AGON=false          # post-pass enabled?
EXTRACTION_KAIROS_REQUIRED=false   # if true, fail pipeline when KAIROS unreachable
EXTRACTION_AGON_REQUIRED=false     # if true, fail pipeline when AGON unreachable
```

Defaults are off. Wire incrementally per workspace via `Workspace.integration_flags` once stable.

### Per-workspace overrides

Tenant-level control via existing `Workspace.config`:

```json
{
  "integrations": {
    "kairos": { "enabled": true, "required": false },
    "agon":   { "enabled": true, "required": false }
  }
}
```

---

## Code layout

```
packages/
├── integrations/
│   ├── __init__.py
│   ├── _base.py                 # AsyncHttpClient, retries, timeouts, contract version check
│   ├── kairos/
│   │   ├── __init__.py
│   │   ├── client.py            # KairosClient
│   │   ├── models.py            # Pydantic mirrors of tacitus-contracts types
│   │   └── mock.py              # Deterministic mock for tests
│   └── agon/
│       ├── __init__.py
│       ├── client.py            # AgonClient
│       ├── models.py
│       └── mock.py
├── extraction/
│   └── src/dialectica_extraction/
│       ├── pipeline.py          # existing LangGraph DAG, gains 2 new nodes
│       └── nodes/
│           ├── temporal_scaffold.py    # NEW — calls KAIROS
│           └── evidence_verify.py      # NEW — calls AGON
└── api/
    └── src/dialectica_api/routers/
        ├── temporal.py          # NEW — /v1/temporal/* proxies KAIROS
        └── evidence.py          # NEW — /v1/evidence/* proxies AGON
```

---

## Client skeletons

### `packages/integrations/_base.py`

```python
import httpx
from contextlib import asynccontextmanager
from typing import Any
from dialectica_common.tracing import current_trace_id

class IntegrationError(Exception):
    pass

class AsyncIntegrationClient:
    def __init__(
        self,
        *,
        name: str,
        base_url: str,
        auth_header: str,
        soft_timeout: float,
        hard_timeout: float,
        contracts_range: str,
    ):
        self.name = name
        self.base_url = base_url
        self.contracts_range = contracts_range
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers={"Authorization": auth_header},
            timeout=httpx.Timeout(hard_timeout, connect=5.0),
        )
        self._soft_timeout = soft_timeout

    async def request(self, method: str, path: str, **kwargs) -> dict[str, Any]:
        headers = kwargs.setdefault("headers", {})
        headers["X-Trace-Id"] = current_trace_id()
        try:
            resp = await self._client.request(method, path, **kwargs)
            resp.raise_for_status()
            body = resp.json()
            self._check_contracts_version(body.get("envelope", {}).get("contracts_version"))
            return body
        except httpx.TimeoutException as e:
            raise IntegrationError(f"{self.name} timeout") from e
        except httpx.HTTPError as e:
            raise IntegrationError(f"{self.name} http error: {e}") from e

    def _check_contracts_version(self, version: str | None) -> None:
        # use packaging.specifiers; raise IntegrationError on mismatch
        ...

    async def aclose(self) -> None:
        await self._client.aclose()
```

### `packages/integrations/kairos/client.py`

```python
from packages.integrations._base import AsyncIntegrationClient
from .models import KairosOutput, KairosRequest

class KairosClient(AsyncIntegrationClient):
    async def analyze(self, req: KairosRequest) -> KairosOutput:
        body = await self.request(
            "POST", "/api/v1/analyze",
            json=req.model_dump(mode="json"),
        )
        return KairosOutput.model_validate(body)

    async def graph_only(self, text: str, document_id: str) -> dict:
        return await self.request(
            "POST", "/api/v1/graph",
            json={"text": text, "document_id": document_id},
        )
```

### `packages/integrations/agon/client.py`

```python
from packages.integrations._base import AsyncIntegrationClient
from .models import AgonOutput, PerceiveRequest

class AgonClient(AsyncIntegrationClient):
    async def perceive(self, req: PerceiveRequest) -> AgonOutput:
        body = await self.request(
            "POST", "/api/perceive",
            json=req.model_dump(mode="json"),
        )
        return AgonOutput.model_validate(body)
```

---

## Pipeline wiring

### Existing pipeline (today)

```
ingest → chunk → gliner_prefilter → gemini_extract → validate → repair → write_neo4j → reasoning
```

### Enriched pipeline (target)

```
ingest
  → [feature flag: KAIROS] temporal_scaffold       ← NEW node
  → chunk
  → gliner_prefilter (now informed by KAIROS actors)
  → gemini_extract (now anchored on KAIROS events)
  → validate
  → repair
  → [feature flag: AGON] evidence_verify           ← NEW node
  → fuse (NEW: merges KAIROS + AGON + Gemini outputs per ONTOLOGY_MAPPING.md)
  → write_neo4j
  → reasoning
```

### `temporal_scaffold` node

```python
# packages/extraction/src/dialectica_extraction/nodes/temporal_scaffold.py
from dialectica_extraction.state import PipelineState
from packages.integrations.kairos import KairosClient, KairosRequest, IntegrationError
from dialectica_extraction.settings import settings
import logging

log = logging.getLogger(__name__)

async def temporal_scaffold(state: PipelineState) -> PipelineState:
    if not settings.extraction_use_kairos:
        return state
    client: KairosClient = state.kairos_client
    try:
        result = await client.analyze(KairosRequest(
            text=state.raw_text,
            document_id=state.document_id,
            document_created_at=state.document_metadata.created_at,
            analysis_mode="auto",
        ))
    except IntegrationError as e:
        log.warning("kairos.unreachable", error=str(e))
        if settings.extraction_kairos_required:
            raise
        state.emit_progress("kairos.skipped", reason=str(e))
        return state

    state.kairos_output = result
    state.emit_progress(
        "kairos.complete",
        events=len(result.events),
        actors=len(result.actors),
        commitments=len(result.commitments),
        relations=len(result.relations),
    )
    return state
```

### `evidence_verify` node

```python
# packages/extraction/src/dialectica_extraction/nodes/evidence_verify.py
async def evidence_verify(state: PipelineState) -> PipelineState:
    if not settings.extraction_use_agon:
        return state
    client: AgonClient = state.agon_client
    try:
        result = await client.perceive(PerceiveRequest(
            text=state.raw_text,
            document_id=state.document_id,
            # send Gemini-extracted claims for verification
            candidate_claims=state.extracted_claims,
        ))
    except IntegrationError as e:
        log.warning("agon.unreachable", error=str(e))
        if settings.extraction_agon_required:
            raise
        state.emit_progress("agon.skipped", reason=str(e))
        return state

    state.agon_output = result
    state.emit_progress(
        "agon.complete",
        verified=sum(1 for c in result.claims if c.verification == "verified"),
        contradictions=len(result.contradictions),
    )
    return state
```

### `fuse` node

Replaces existing entity merging. Implements pseudocode from [`ONTOLOGY_MAPPING.md`](./ONTOLOGY_MAPPING.md) §Fusion algorithm.

```python
async def fuse(state: PipelineState) -> PipelineState:
    fused = ConflictGraphBuilder(
        kairos=state.kairos_output,
        agon=state.agon_output,
        gemini=state.gemini_output,
        workspace_actor_registry=state.workspace.actor_registry,
    ).build()
    state.fused_graph = fused
    return state
```

---

## MCP tools (runtime reasoning)

Existing MCP server at `packages/mcp/src/dialectica_mcp/server.py` exposes 5 tools. Add 4 more:

```python
@tool(name="temporal_query")
async def temporal_query(actor: str, predicate: str, time_range: dict) -> dict:
    """Query KAIROS temporal graph for events involving actor."""
    return await ctx.kairos.graph_only(...)

@tool(name="verify_claim")
async def verify_claim(claim_id: str, workspace_id: str) -> dict:
    """Re-run AGON verification on a stored claim."""
    claim = await ctx.graph.get_claim(claim_id)
    return await ctx.agon.perceive(...)

@tool(name="find_contradictions")
async def find_contradictions(workspace_id: str) -> list[dict]:
    """Sweep workspace for AGON-detected contradictions."""
    return await ctx.agon.list_contradictions(workspace_id)

@tool(name="commitment_state")
async def commitment_state(actor: str, target: str, workspace_id: str) -> dict:
    """Query current commitment state machine via KAIROS reasoning."""
    ...
```

Update `docs/mcp-setup.md` to list 9 tools instead of 5.

---

## FastAPI router proxies

Two new routers under `packages/api/src/dialectica_api/routers/`:

### `/v1/temporal/*` (KAIROS proxy)

```python
@router.post("/v1/temporal/analyze")
async def temporal_analyze(req: TemporalAnalyzeRequest, ctx: Context):
    """External access to KAIROS via DIALECTICA gateway."""
    result = await ctx.kairos.analyze(req)
    # log usage, apply rate limit, return
    return result
```

Endpoints:
- `POST /v1/temporal/analyze`
- `POST /v1/temporal/graph`
- `POST /v1/temporal/validate`

### `/v1/evidence/*` (AGON proxy)

- `POST /v1/evidence/perceive`
- `POST /v1/evidence/verify-claim`
- `GET  /v1/evidence/sessions/{id}/report.md`

External developers see one API. Internal: three services.

---

## Local development

### `docker-compose.local.yml` additions

```yaml
services:
  kairos:
    image: ghcr.io/sargonxg/kairos:latest
    environment:
      KAIROS_LLM: mock
      KAIROS_BASIC_USER: kairos
      KAIROS_BASIC_PASSWORD: dev
    ports: ["8081:8080"]

  agon:
    image: ghcr.io/sargonxg/agon:latest
    environment:
      AGON_BACKEND: mock
      AGON_DEMO_USER: AGON
      AGON_DEMO_PASSWORD: AGON
    ports: ["8082:18080"]

  api:
    environment:
      KAIROS_ENABLED: "true"
      KAIROS_URL: http://kairos:8080
      KAIROS_AUTH_HEADER: "Basic a2Fpcm9zOmRldg=="
      AGON_ENABLED: "true"
      AGON_URL: http://agon:18080
      AGON_AUTH_HEADER: "Basic QUdPTjpBR09O"
      EXTRACTION_USE_KAIROS: "true"
      EXTRACTION_USE_AGON: "true"
```

### Mock-first development

Both clients ship with `mock.py` implementations that return deterministic fixtures. Useful for:
- Running CI without AGON/KAIROS images
- Pipeline unit tests
- Offline development

```python
from packages.integrations.kairos.mock import MockKairosClient
client = MockKairosClient(fixture="meridian_compact")
result = await client.analyze(...)
```

---

## Testing

### Unit tests

- `packages/integrations/kairos/tests/test_client.py` — verifies request/response shapes against fixture
- `packages/integrations/agon/tests/test_client.py` — same
- `packages/extraction/tests/test_temporal_scaffold.py` — pipeline node with mock client
- `packages/extraction/tests/test_evidence_verify.py` — same

### Integration tests (Docker compose)

`make test-integration` brings up all three services with mock backends, runs end-to-end fixture document through enriched pipeline, asserts:
- Graph contains expected actors with merge trace
- All events have temporal_confidence
- Contradictions present as edges
- Quality gates attached to workspace

### Golden fixtures

Maintain `tests/fixtures/integration/`:
- `meridian_compact.txt` — KAIROS demo doc
- `board_packet_dispute.txt` — AGON demo doc
- `jcpoa_excerpt.txt` — DIALECTICA benchmark
- Each with expected graph snapshot for regression.

---

## Rollout sequence

1. **Phase 0 — Contracts** ([`ROADMAP.md`](./ROADMAP.md) §1). Publish `tacitus-contracts@0.1`. Stub clients.
2. **Phase 1 — KAIROS pre-pass.** Behind flag, mock by default. Soak in staging.
3. **Phase 2 — AGON post-pass.** Same pattern.
4. **Phase 3 — MCP tools.** Expose to agents.
5. **Phase 4 — FastAPI proxies.** External developers + PRAXIS gain access.
6. **Phase 5 — Per-workspace enablement.** Promote stable workspaces.
7. **Phase 6 — Default on.** Flip `EXTRACTION_USE_*=true` defaults after 30 days clean operation.

Each phase ships independently. No big-bang merge.

---

*See [`PRAXIS_BACKBONE.md`](./PRAXIS_BACKBONE.md) for what PRAXIS gets out of this.*
