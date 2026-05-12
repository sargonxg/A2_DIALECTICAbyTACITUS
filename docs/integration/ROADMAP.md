# Integration Roadmap

What to do, in what order, to wire DIALECTICA + AGON + KAIROS into the production backbone for praxis.tacitus.me.

> **Posture: practical, not aspirational.** Each phase ships and demos independently. No big-bang merges. Feature flags everywhere.

---

## Sequencing principle

Don't wire integration until contracts exist. Don't promote flags until each phase is observed clean for 7+ days. Don't claim "trinity-powered" in marketing until phase 4 is done.

---

## Phase 0 — Foundations (week 1-2)

**Goal:** make integration possible without committing to it.

- [ ] Decide protobuf vs JSON Schema for contracts (see [`CONTRACTS.md`](./CONTRACTS.md) §Tooling)
- [ ] Create `sargonxg/tacitus-contracts` repo
- [ ] Write `schema/*.proto` for v0.1 covering: Identifiers, SourceSpan, Actor, Event, Claim, Commitment, Contradiction, AllenRelation, Envelope
- [ ] Generate Rust + Python + TypeScript bindings via `buf` or manual
- [ ] Publish `tacitus-contracts@0.1.0` to PyPI / crates.io / npm
- [ ] Audit DIALECTICA's existing Actor/Event types — list every divergence from contract
- [ ] Stub `packages/integrations/kairos/` and `packages/integrations/agon/` with types only, no calls

**Done when:** all three repos import `tacitus-contracts` without errors and tests still pass.

---

## Phase 1 — KAIROS pre-pass (week 3-4)

**Goal:** Gemini extraction operates on KAIROS temporal scaffold. Behind feature flag.

- [ ] Implement `KairosClient` with mock backend
- [ ] Add `temporal_scaffold` LangGraph node ([`INTEGRATION_GUIDE.md`](./INTEGRATION_GUIDE.md) §Pipeline wiring)
- [ ] Update fusion: import KAIROS events as Conflict Grammar `Event` nodes per [`ONTOLOGY_MAPPING.md`](./ONTOLOGY_MAPPING.md)
- [ ] Add Conflict Grammar v2.1 edges: `PRECEDES`, `MEETS`, `OVERLAPS`, `DURING`, `STARTS`, `FINISHES`, `COTEMPORAL`, `ANCHORED_BY`
- [ ] Add `Episode` node type (alias `Phase`)
- [ ] Add `Commitment` node type + state enum
- [ ] Update SSE progress stream: emit `kairos.complete`, `kairos.skipped` events
- [ ] Frontend: surface temporal richness in `/workspaces/[id]/timeline` tab
- [ ] Tests: fixture document `meridian_compact.txt` produces graph with N events + M Allen relations
- [ ] Deploy KAIROS to internal Cloud Run (`kairos-internal.tacitus.me`)
- [ ] Soak in staging 7 days

**Done when:** one workspace can ingest with `EXTRACTION_USE_KAIROS=true`, see commitments + Allen relations in graph, no regression on existing benchmarks.

---

## Phase 2 — AGON post-pass (week 5-7)

**Goal:** every claim Gemini extracts is verified or marked unresolved. Contradictions land as edges.

- [ ] Implement `AgonClient` with mock backend
- [ ] Add `evidence_verify` LangGraph node
- [ ] Update fusion: AGON claims → `Assertion` nodes + `EVIDENCED_BY` edges
- [ ] Add Conflict Grammar v2.1: `Assertion` node, `CONTRADICTS` edge, `DENIES` edge, `ASSERTS` edge
- [ ] Add `verification_status` property to assertions
- [ ] Workspace quality gates: store AGON output in `Workspace.quality_gates`
- [ ] Frontend: per-claim verification badge in entity detail view
- [ ] Frontend: contradiction list in workspace overview
- [ ] Tests: fixture `board_packet_dispute.txt` produces graph with K contradictions
- [ ] Deploy AGON to internal Cloud Run (`agon-internal.tacitus.me`)
- [ ] Soak 7 days

**Done when:** 80%+ of extracted claims are `verified` or `denied`, contradictions visible in PRAXIS UI.

---

## Phase 3 — MCP runtime tools (week 8)

**Goal:** DIALECTICA's 6 agents can call AGON + KAIROS during reasoning, not just ingestion.

- [ ] Add MCP tools: `temporal_query`, `verify_claim`, `find_contradictions`, `commitment_state`
- [ ] Update `docs/mcp-setup.md` (5 tools → 9 tools)
- [ ] Agent prompts: teach Analyst + Forecaster + Mediator to use new tools
- [ ] Tests: agent answers cite AGON/KAIROS-sourced data
- [ ] Claude Desktop dogfood: install MCP, verify tools fire

**Done when:** agent responses include verified citations and temporal reasoning paths.

---

## Phase 4 — FastAPI proxies (week 9-10)

**Goal:** external developers + PRAXIS get one unified API surface.

- [ ] New router `packages/api/src/dialectica_api/routers/temporal.py` proxying KAIROS
- [ ] New router `packages/api/src/dialectica_api/routers/evidence.py` proxying AGON
- [ ] Auth, rate limit, billing apply uniformly
- [ ] OpenAPI docs auto-update at `/docs`
- [ ] TypeScript SDK: add `client.temporal.*` and `client.evidence.*` namespaces
- [ ] Update developer portal at `/developers` with new endpoint examples

**Done when:** PRAXIS migrates one feature (e.g., timeline view) to consume `/v1/temporal/*` via DIALECTICA gateway.

---

## Phase 5 — PRAXIS UI consumption (week 11-14)

**Goal:** trinity outputs visible to PRAXIS users.

- [ ] PRAXIS adds `<CommitmentTracker>` component
- [ ] PRAXIS adds `<ContradictionExplorer>` component
- [ ] PRAXIS adds `<TimelineView>` with Allen-relation rendering
- [ ] PRAXIS adds `<QualityGauge>` workspace health card
- [ ] Provenance overlay: click any node → see source span + which service emitted it
- [ ] Ship one customer demo with trinity-powered analysis

**Done when:** customer demo lands and at least one user says "wait, you can show me the actual source line?"

---

## Phase 6 — Default-on rollout (week 15+)

**Goal:** flip flags from off to on for new workspaces.

- [ ] Per-workspace `integrations.{kairos|agon}.enabled = true` for new sign-ups
- [ ] Existing workspaces get migration banner: opt in
- [ ] 30 days clean: flip env defaults `EXTRACTION_USE_KAIROS=true`, `EXTRACTION_USE_AGON=true`
- [ ] Remove `_REQUIRED=false` safety nets after 90 days of stability
- [ ] Trinity becomes the default story in pitch deck

---

## Parallel tracks

### Track A — Contracts evolution

- After v0.1: gather feedback, plan v0.2 (add `Episode`, `Hypothesis`, refine predicate vocabulary)
- After 6 months: cut v1.0.0 stable

### Track B — KAIROS hardening

Standalone improvements that make integration better:
- Multi-document corpus mode (KAIROS's own roadmap)
- TimeML import/export
- Trained local NER for date extraction (reduces Gemini dependency)
- gRPC server option for faster cross-service calls

### Track C — AGON hardening

- Deeper deterministic contradiction rules (dates, order, obligations)
- Reviewed/unreviewed evidence workflow
- NLI-style contradiction classifier
- BGE/fastembed local embeddings for alias clustering
- Multi-document case folders

### Track D — DIALECTICA cleanup

Pre-requisites for clean integration:
- Resolve "sprawl note" in CLAUDE.md: remove parallel ingestion paths (`dialectica/ingestion/`, `apps/web/src/lib/graphopsExtraction.ts`)
- Migrate `Redis` job store from in-process (already planned)
- Conflict Grammar v2.1 ontology migration (additive only — backward compatible)
- Update `docs/ARCHITECTURE.md` to reference integration docs

---

## Risk register

| Risk | Mitigation |
|---|---|
| Contract drift between Rust + Python types | `buf breaking` CI check + cross-service version checks |
| AGON/KAIROS latency blocks pipeline | Soft timeouts + skip-on-failure flags |
| Actor canonicalization wrong (false merges) | Fuzzy-match threshold + human review queue |
| Conflict Grammar v2.1 breaks existing queries | All changes additive; no removed types/edges |
| Three services × Cloud Run cost spikes | Min instances 0, scale to zero, monitor monthly |
| Gemini billing triples (three services call it) | KAIROS + AGON both have mock modes for staging; production uses shared quota |
| MCP tool sprawl confuses agents | Cap at 10 tools; consolidate if overlap |
| Customer expects "it just works" before phase 5 | Honest README + capability statements; no marketing ahead of code |

---

## Success criteria — backbone ready

The trinity is "production backbone for PRAXIS" when ALL of:

- [ ] Phase 0-5 complete
- [ ] One paying customer in production
- [ ] 99.5% pipeline success rate over 30 days
- [ ] p95 ingestion latency under 90s for single document
- [ ] Zero data integrity incidents (no false actor merges, no missing spans)
- [ ] PRAXIS UI demos cleanly to a non-technical buyer in < 5 minutes
- [ ] Investors stop asking "but how is this different from ChatGPT"

---

## What this roadmap does NOT cover

Out of scope here (live in respective repo issues):
- AGON's own MVP+++ plan (`docs/AGON_MVP_PLUS_PLAN.md`)
- KAIROS standalone features (TimeML, neural date NER)
- DIALECTICA non-integration work (subdomains, benchmarks, theory frameworks)
- PRAXIS product roadmap

This roadmap is **only** about wiring the three together.

---

*Maintained by TACITUS. Update every phase completion. Ship the work; don't ship the plan.*
