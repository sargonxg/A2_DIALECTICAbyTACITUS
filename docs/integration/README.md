# TACITUS Stack Integration

This folder documents how **DIALECTICA**, **AGON**, and **KAIROS** combine into a single neurosymbolic conflict-intelligence stack — the backbone for [praxis.tacitus.me](https://praxis.tacitus.me) and other TACITUS products.

> **Status — be honest.** Most of what's described here is the **target architecture**, not the current wired state. Each repo is independently functional today. This folder is the contract that lets us wire them deliberately, in versioned slices, without breaking standalone use.

---

## The Trinity (one paragraph)

| Repo | Role | Language | Owns |
|---|---|---|---|
| [**DIALECTICA**](https://github.com/sargonxg/A2_DIALECTICAbyTACITUS) | Conductor + reasoning core | Python | Conflict Grammar ontology, Neo4j graph, 6 agents, GraphRAG, symbolic rules, FastAPI, MCP server |
| [**AGON**](https://github.com/sargonxg/AGON) | Evidence engine | Rust | Claim verification, contradiction detection, evidence spans, friction maps, deterministic inference |
| [**KAIROS**](https://github.com/sargonxg/KAIROS-temporal-vision-TACITUS) | Temporal engine | Rust | Date extraction, event canonicalization, Allen-13 relations, commitment state, episode boundaries |

**Why split:** Rust at the edges for determinism + speed on structural work; Python in the middle for orchestration + LLM reasoning. Each repo stays publishable on its own.

---

## Reading order

1. [`ARCHITECTURE.md`](./ARCHITECTURE.md) — system diagram, data flow, service topology, failure modes
2. [`CONTRACTS.md`](./CONTRACTS.md) — shared types (ActorID, SourceSpan, Claim, Event, Commitment) — **the moat**
3. [`ONTOLOGY_MAPPING.md`](./ONTOLOGY_MAPPING.md) — AGON primitives → Conflict Grammar nodes; KAIROS events → DIALECTICA events
4. [`INTEGRATION_GUIDE.md`](./INTEGRATION_GUIDE.md) — how DIALECTICA calls AGON + KAIROS in pipeline, MCP, and router layers
5. [`PRAXIS_BACKBONE.md`](./PRAXIS_BACKBONE.md) — how the stack powers praxis.tacitus.me
6. [`ROADMAP.md`](./ROADMAP.md) — what to wire first, second, last

---

## Core principles

1. **Standalone first.** AGON and KAIROS must each be a publishable product. DIALECTICA must degrade gracefully if either is unreachable.
2. **Contracts are the product.** Shared types live in one place, versioned semver, with Rust + Python + TypeScript bindings generated from one source.
3. **Wire optionally, feature-flagged.** Every integration point ships behind a flag (`EXTRACTION_USE_KAIROS=true`, `EXTRACTION_USE_AGON=true`). Off by default until proven.
4. **Determinism at the edges.** Rust does evidence verification + temporal logic. Python orchestrates. LLMs refine, never define.
5. **Honest capabilities.** Match AGON/KAIROS's restraint — "we don't issue verdicts." DIALECTICA marketing copy should follow.
6. **No autonomous verdicts.** The stack outputs structured analysis. Humans decide.

---

## Three integration patterns (all valid, use in combination)

### 1. Pipeline stages (highest ROI)
```
raw text
  → KAIROS         (temporal scaffold: dates, events, commitments)
  → DIALECTICA     (Gemini extraction anchored on KAIROS scaffold)
  → AGON           (verify claims against source, mark contradictions)
  → Neo4j write    (Conflict Grammar graph, evidence-bound, temporally rich)
```

### 2. MCP tools (runtime reasoning)
DIALECTICA's 6 agents call AGON + KAIROS as tools during analysis:
- `temporal_query(actor, predicate, time_range)` → KAIROS
- `verify_claim(claim_id)` → AGON
- `find_contradictions(workspace_id)` → AGON sweep
- `commitment_state(actor, target)` → KAIROS

### 3. FastAPI router proxies (external surface)
PRAXIS + external developers see one API:
- `/v1/temporal/*` → proxies KAIROS
- `/v1/evidence/*` → proxies AGON
- Unified auth, rate limit, billing through DIALECTICA's gateway

---

## What lives here vs in the other repos

| Doc | Lives in | Why |
|---|---|---|
| Integration architecture | DIALECTICA `docs/integration/` | DIALECTICA is the conductor |
| Shared contracts spec | DIALECTICA `docs/integration/CONTRACTS.md` | Single source of truth |
| Ontology mapping | DIALECTICA `docs/integration/ONTOLOGY_MAPPING.md` | DIALECTICA owns the target ontology |
| AGON-side interop notes | [AGON `docs/INTEROP.md`](https://github.com/sargonxg/AGON/blob/main/docs/INTEROP.md) | Mirrors CONTRACTS from Rust perspective |
| KAIROS-side interop notes | [KAIROS `docs/INTEROP.md`](https://github.com/sargonxg/KAIROS-temporal-vision-TACITUS/blob/main/docs/INTEROP.md) | Mirrors CONTRACTS from Rust perspective |

---

## Versioning

Three services + one contracts package. Semver per service. Contracts package is the compatibility gate:

- `tacitus-contracts@1.x` — initial wire spec (additive changes only)
- DIALECTICA, AGON, KAIROS each declare `contracts-compatible: ">=1.0, <2.0"`
- Breaking change to contracts = major bump everywhere

See [`CONTRACTS.md`](./CONTRACTS.md) for the rules.

---

*Maintained by TACITUS. Questions: [tacitus.me](https://www.tacitus.me).*
