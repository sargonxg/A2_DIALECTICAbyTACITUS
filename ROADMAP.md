# DIALECTICA Roadmap

What's next for DIALECTICA as the **conductor of the TACITUS trinity** and the **backbone of [praxis.tacitus.me](https://praxis.tacitus.me)**.

> **Posture: practical, not aspirational.** Three tracks run in parallel. Standalone improvements continue while integration work lands behind feature flags.

---

## Tracks

| Track | Focus | Driver |
|---|---|---|
| **1. Trinity integration** | Wire AGON + KAIROS into pipeline, MCP, and routers | PRAXIS backbone readiness |
| **2. PRAXIS-ready features** | What praxis.tacitus.me needs from DIALECTICA | Customer-facing |
| **3. Standalone hardening** | Quality, performance, ontology evolution | Long-term durability |

---

## Track 1 — Trinity integration

**Full plan:** [`docs/integration/ROADMAP.md`](docs/integration/ROADMAP.md). Summary here.

### Phase 0 — Contracts (week 1-2)
- [ ] Decide protobuf vs JSON Schema
- [ ] Create `sargonxg/tacitus-contracts` repo
- [ ] Publish `tacitus-contracts@0.1.0`
- [ ] Stub `packages/integrations/{kairos,agon}/`

### Phase 1 — KAIROS pre-pass (week 3-4)
- [ ] `KairosClient` with mock backend
- [ ] `temporal_scaffold` LangGraph node
- [ ] Conflict Grammar v2.1: Allen-relation edges, `Episode`, `Commitment` node types
- [ ] Frontend timeline view consuming KAIROS data
- [ ] Behind `EXTRACTION_USE_KAIROS=true`

### Phase 2 — AGON post-pass (week 5-7)
- [ ] `AgonClient` with mock backend
- [ ] `evidence_verify` LangGraph node
- [ ] Conflict Grammar v2.1: `Assertion`, `CONTRADICTS`, `DENIES`, `ASSERTS`
- [ ] Workspace quality gates surfaced in UI
- [ ] Behind `EXTRACTION_USE_AGON=true`

### Phase 3 — MCP runtime tools (week 8)
- [ ] +4 tools (`temporal_query`, `verify_claim`, `find_contradictions`, `commitment_state`)
- [ ] Agent prompts updated

### Phase 4 — FastAPI proxies (week 9-10)
- [ ] `/v1/temporal/*` proxying KAIROS
- [ ] `/v1/evidence/*` proxying AGON
- [ ] TypeScript SDK namespaces

### Phase 5-6 — PRAXIS UI + default-on (week 11+)
- [ ] PRAXIS consumes trinity outputs
- [ ] Per-workspace enablement
- [ ] Default flags flipped after 30 days clean

---

## Track 2 — PRAXIS-ready features

What PRAXIS specifically needs from DIALECTICA, regardless of trinity wiring.

### P1 — Provenance overlay
- [ ] Every node/edge in graph carries `{document_id, span_id, sha256}` already; expose via API
- [ ] New endpoint: `GET /v1/workspaces/{ws}/provenance/{node_id}` returns full citation chain
- [ ] PRAXIS uses this to render "click any claim → see source"

### P2 — Workspace health summary
- [ ] `GET /v1/workspaces/{ws}/health` returns: extraction success rate, evidence coverage, contradiction count, last update, freshness
- [ ] PRAXIS renders as workspace card

### P3 — Reasoning trail replay
- [ ] Existing Cloud SQL ledger captures runs. Surface as `GET /v1/workspaces/{ws}/runs/{run_id}/trail`
- [ ] PRAXIS renders timeline of pipeline steps with per-step output

### P4 — Live SSE for everything
- [ ] Existing SSE on extraction. Extend to: reasoning runs, benchmark runs, agent calls
- [ ] PRAXIS shows "thinking" indicators with detail

### P5 — Mediator brief generator
- [ ] New endpoint: `POST /v1/workspaces/{ws}/brief` produces structured brief: parties, claims, contradictions, commitments, recommendations
- [ ] Drives PRAXIS "Generate brief" feature

### P6 — Multi-workspace cross-query
- [ ] `POST /v1/integration/query` with `workspace_ids: [...]` (already partial)
- [ ] Cross-corpus actor coreference (relies on Conflict Grammar v2.2 work)

### P7 — Permissioned shares
- [ ] Generate read-only share tokens for a workspace
- [ ] PRAXIS uses this for client-facing reports

---

## Track 3 — Standalone hardening

Improvements that benefit DIALECTICA users whether or not they wire AGON/KAIROS.

### H1 — Sprawl cleanup

Per `CLAUDE.md`, two parallel ingestion paths exist alongside the canonical one:
- `dialectica/ingestion/` CLI
- `apps/web/src/lib/graphopsExtraction.ts`

- [ ] Migrate any unique features into canonical `packages/extraction/`
- [ ] Remove parallel paths
- [ ] Update tests

### H2 — Redis job store

Today's job store is in-process (per CLAUDE.md). Doesn't scale to multi-instance Cloud Run.
- [ ] Implement Redis-backed `JobStore`
- [ ] SSE consumer routing across instances
- [ ] Feature flag during cutover

### H3 — Conflict Grammar v2.1

Driven by trinity integration but useful standalone:
- [ ] New nodes: `Assertion`, `Commitment`, alias `Episode` for `Phase`
- [ ] New edges: `CONTRADICTS`, `DENIES`, `ASSERTS`, Allen edges (`PRECEDES`, `MEETS`, etc.), `COMMITTED`, `TO`, `ANCHORED_BY`
- [ ] New enums: `VerificationStatus`, `CommitmentState`, `ContradictionMechanism`
- [ ] Backward-compatible: zero existing types removed
- [ ] Migration guide for existing graphs

### H4 — Benchmarking expansion

Current: 4 corpora (JCPOA, Romeo/Juliet, Crime/Punishment, War/Peace).
- [ ] Add 4 more across underrepresented subdomains: workplace dispute, commercial arbitration, environmental conflict, hybrid warfare
- [ ] Add quality measures: not just F1 but evidence coverage, contradiction recall, temporal precision
- [ ] Trend dashboard for regression detection

### H5 — Performance

- [ ] LangGraph pipeline p95 < 30s for 10k-word document
- [ ] Caching layer for repeated extractions (same content hash → cached graph)
- [ ] Concurrent Gemini calls within pipeline (batch chunks)
- [ ] Query latency: p95 < 200ms for graph reads

### H6 — Production observability

- [ ] OpenTelemetry tracing across pipeline stages
- [ ] Per-tenant cost tracking (Gemini tokens × workspace)
- [ ] Anomaly alerts (extraction failure rate, latency regressions)
- [ ] Cost dashboard in `/admin`

### H7 — Subdomain expansion

Six subdomains today (geopolitical, workplace, commercial, legal, armed, environmental).
- [ ] Add `family` subdomain (mediation use case)
- [ ] Add `community` subdomain (public disputes)
- [ ] Domain-specific symbolic rules per new subdomain
- [ ] Frontend filter

---

## Phase E — Enterprise readiness (when first paying customer)

Don't build speculatively.

- [ ] Multi-tenant SSO (SAML/OIDC)
- [ ] Row-level tenant isolation in Neo4j (currently workspace-scoped property; needs RLS or per-tenant DB)
- [ ] Audit log API (who-did-what-when)
- [ ] EU data residency option
- [ ] SOC 2 prep + SOC 2 Type II
- [ ] On-prem deployment option (Kubernetes Helm chart)
- [ ] PII redaction layer for documents in regulated industries

---

## What's NOT on the roadmap (intentional)

- **Replacing Gemini.** Use frontier models. Train only narrow sensors where clearly worth it.
- **Custom UI framework.** Stick with Next.js + Tailwind + Radix.
- **Generic graph DB.** Neo4j is the primary. Other backends (FalkorDB, Spanner) stay supported but Neo4j gets the love.
- **Becoming a general LLM platform.** DIALECTICA is conflict intelligence. Stay focused.
- **Verdicts.** Same posture as AGON + KAIROS. Structured intelligence, never autonomous decisions.

---

## Success criteria

| Track | Done when |
|---|---|
| 1 — Trinity integration | All 6 phases shipped; PRAXIS demo uses trinity outputs end-to-end |
| 2 — PRAXIS-ready | PRAXIS frontend consumes all P1-P7 endpoints in production |
| 3 — Standalone hardening | Sprawl removed; Redis store live; CG v2.1 shipped; p95 latency targets hit |
| E — Enterprise | First enterprise customer in production with full audit/RBAC |

---

## Open questions

1. **Monorepo or contracts-as-separate-repo?** See [`docs/integration/CONTRACTS.md`](docs/integration/CONTRACTS.md). Lean toward separate repo for clean publishing lifecycle.

2. **Cozo + Graphiti future.** Currently optional. Decide in 6 months whether they remain experiments or become first-class.

3. **Databricks ROI.** KGE training via Databricks works but isn't widely used. Keep as optional path or remove?

4. **Auth migration.** localStorage today (per README). When to migrate to Clerk/Supabase? Tied to first enterprise customer.

5. **Demo footprint cost.** `/demo/*` routes carry significant fixtures. Consider lazy-loading or removing legacy demo paths.

---

## How to contribute

- Pick a milestone. Open an issue first if non-trivial.
- Conventional commits (`feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `infra:`).
- `make quality-all` must pass.
- New features need tests; new endpoints need OpenAPI updates.

---

*Maintained by TACITUS. Update as phases close. Don't ship the plan; ship the work.*
