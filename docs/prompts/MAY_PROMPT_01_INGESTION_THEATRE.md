# Codex Prompt 01 — DIALECTICA Demo: The Live Ingestion Theatre

> **Repository:** `A2_DIALECTICAbyTACITUS` (Next.js 15 monorepo + Python packages)
> **Branch convention:** `feat/demo-ingestion-theatre`
> **Companion prompt:** `CODEX_PROMPT_02_REASONING_THEATRE.md` (run after this one merges)
> **Estimated effort:** 5-day Claude Code build, 3 days for a senior engineer
> **Status when this prompt is handed to you:** the existing `/demo` page is a 2,408-line monolith that fakes a 5-step progress bar and falls back to a hard-coded graph. The real LangGraph extraction pipeline (`packages/extraction/src/dialectica_extraction/pipeline.py`) and SSE stream (`packages/api/src/dialectica_api/routers/extraction_stream.py`) already exist and emit canonical step events — the demo page just doesn't subscribe to them. Your job is to fix that, with real animation and real data.

---

## TL;DR — what you are building

A new `/demo` route that takes a visitor through **eleven cinematic acts** in a single auto-advancing scrolly-narrative, end-to-end:

1. **Act 0 — Mission framing.** Why a deterministic substrate for conflict matters.
2. **Act 1 — The three doors.** Pick one of three scenarios: *Romeo & Juliet*, *War and Peace*, *Syria 2011–2024*. Each door previews a question an LLM cannot answer with citations. (The actual reasoning layer ships in Prompt 02.)
3. **Act 2 — Source reveal.** The raw text streams in from Project Gutenberg (Romeo, War & Peace) or the curated Syria corpus.
4. **Act 3 — Chunking.** 2 000-character overlapping windows fly into place as the runner emits `chunk_document` events.
5. **Act 4 — GLiNER pre-filter.** Per-chunk entity-density bars rise as `gliner_prefilter` events arrive.
6. **Act 5 — Gemini Flash extraction.** Entity bubbles pop out of each chunk with confidence radii.
7. **Act 6 — Pydantic validation + repair loop.** Invalid entities flash red, cycle back into Gemini, re-emerge green or get culled.
8. **Act 7 — Coreference resolution.** Aliases ("Romeo", "Romeo Montague", "young Montague") snap together.
9. **Act 8 — Relationship extraction.** Edges materialise between validated nodes, coloured by edge type.
10. **Act 9 — Embedding projection.** Vertex AI `text-embedding-005` vectors are projected to 2D and the constellation forms.
11. **Act 10 — Write to graph.** Final force-directed graph settles; Cypher counts confirm the write.
12. **Act 11 — Handoff.** "Now you can ask things." Persistent CTA to the reasoning theatre (Prompt 02).

Every act runs against the **real SSE stream** when the API is reachable. When it isn't, the page falls back to a pre-recorded SSE replay (a stored `.ndjson` of events captured from a real run) — **never** to a synthetic graph that lies about what happened. Investors see what the system actually does, end-to-end, on real public-domain text.

---

## Repository contract (read these first)

Before writing a line of code, read in order:

| Path | Why |
|---|---|
| `docs/ARCHITECTURE.md` | Canonical pipeline. Step keys, SSE event shape, multi-tenant invariants. **Authoritative.** |
| `packages/extraction/src/dialectica_extraction/pipeline.py` | The 10-step LangGraph DAG. Note `PIPELINE_STEPS` ordering and the `should_repair` conditional edge. |
| `packages/api/src/dialectica_api/services/pipeline_runner.py` | Inline runner that emits `JobProgressEvent`s with `counts`. Match every count key on the frontend. |
| `packages/api/src/dialectica_api/routers/extraction_stream.py` | SSE endpoint. Pay attention to the `ready`, `started`, `complete`, `failed`, `info`, `job` event names. |
| `packages/extraction/src/dialectica_extraction/sources/gutenberg.py` | The 8-book curated catalogue. We will use book IDs **1513** (Romeo) and **2600** (War and Peace). |
| `data/seed/samples/syria_civil_war.json` | Existing 20-actor Syria seed. We will replace it with a richer narrative-text corpus in Phase 0 below. |
| `data/seed/benchmarks/{romeo_juliet,war_peace,jcpoa}_gold.json` | Gold standard graphs. These are the **fallback** graphs when the live pipeline can't run. |
| `apps/web/src/components/extraction/LiveExtractionProgress.tsx` | Existing minimal SSE consumer — replace with the new act-driven renderer, but reuse the EventSource wiring. |
| `apps/web/src/components/graph/ForceGraph.tsx` | Existing D3 force-directed renderer (~470 lines). Keep, extend, do not duplicate. |
| `apps/web/src/lib/api.ts` (look for `streamExtraction`) | Existing SSE client. Use it. |
| `apps/web/src/types/graph.ts` | `GraphNode`, `GraphLink`, `GraphData` types. Extend, don't fork. |

**Do not read** the existing `apps/web/src/app/demo/page.tsx` for inspiration — it is the artefact we are replacing. Skim it only to confirm what to delete.

---

## Architectural decisions (rationale-first, locked in advance)

### D-1. The demo runs against the *real* canonical pipeline.

The current demo's `handleAnalyze` calls `POST /v1/extract` and then `GET /v1/workspaces/{id}/graph` with a 10-second timeout, falls back to a hardcoded graph on any error, and shows a fake progress bar with `setTimeout` delays. **This is dishonest.** Investors will ask "is this real?" and the only honest answer should be yes.

The new flow:

1. User picks scenario.
2. Frontend calls `POST /v1/workspaces/{ws}/ingest/gutenberg` (for Romeo / W&P) or `POST /v1/workspaces/{ws}/extract` with seeded Syria text.
3. Frontend immediately opens `GET /v1/workspaces/{ws}/extractions/{job_id}/stream` (SSE).
4. Each act listens for the canonical step keys (`chunk_document`, `gliner_prefilter`, `extract_entities`, `validate_schema`, `extract_relationships`, `resolve_coreference`, `validate_structural`, `compute_embeddings`, `check_review_needed`, `write_to_graph`).
5. The `job` terminal event delivers the full graph snapshot.

### D-2. Fallback is honest.

If the API is unreachable (no GCP creds, demo laptop offline, Cloud Run cold-start fail), the page replays a **pre-recorded SSE log** from a real run — a file in `apps/web/public/demo/replays/{romeo,war_peace,syria}.ndjson` produced by capturing a single live run with the Phase 7 capture tool. The page shows a small amber banner: *"Demo mode — replaying a captured run from {date}. Live API unavailable."* No fake numbers; numbers come from the recording. The fallback graph in `data/seed/benchmarks/*_gold.json` is **only** used to validate the recording matches expectations, not displayed directly.

### D-3. One demo workspace per scenario, isolated tenants.

Create three demo workspaces on first deploy:

- `demo-romeo` (tenant `demo`, tier `standard`)
- `demo-war-peace` (tenant `demo`, tier `lite`)
- `demo-syria` (tenant `demo`, tier `full`)

These are pre-seeded *empty* on the API; the demo run actually writes them. Subsequent visitors trigger a `POST /v1/workspaces/{ws}/reset` (new endpoint, see Phase 1) to clear the previous graph before starting again. Multi-tenant invariants from `ARCHITECTURE.md § Multi-tenant invariants` are non-negotiable: `workspace_id` AND `tenant_id` filtering on every query.

### D-4. The 11 acts are React components, the page is the conductor.

```
apps/web/src/app/demo/
├── layout.tsx                  (existing — extend with skip-to-act ribbon)
├── page.tsx                    (NEW — ~300 lines max, conductor only)
└── investor/page.tsx           (existing, untouched)

apps/web/src/components/demo/
├── DemoConductor.tsx           (orchestrates act state + SSE subscription)
├── act00_MissionFraming.tsx
├── act01_ThreeDoors.tsx
├── act02_SourceReveal.tsx
├── act03_Chunking.tsx
├── act04_GlinerPrefilter.tsx
├── act05_GeminiExtraction.tsx
├── act06_ValidationRepair.tsx
├── act07_Coreference.tsx
├── act08_Relationships.tsx
├── act09_EmbeddingProjection.tsx
├── act10_GraphMaterialised.tsx
├── act11_Handoff.tsx
├── primitives/
│   ├── ActFrame.tsx            (shared frame: title, narrator caption, progress dot row)
│   ├── EventStream.tsx         (consumes SSE, broadcasts via React context)
│   ├── ReplayDriver.tsx        (NDJSON replay, same shape as EventStream)
│   ├── EntityBubble.tsx        (animated bubble with confidence ring)
│   ├── ChunkBar.tsx            (sliding chunk visualisation)
│   ├── EdgeFlourish.tsx        (animated SVG path with arrowhead reveal)
│   ├── GraphSpotlight.tsx      (the same ForceGraph but with a director's lens)
│   └── DemoModeBanner.tsx      (live vs replay vs offline)
└── data/
    ├── doors.ts                (3 scenarios with pitch questions)
    ├── narratorScripts.ts      (per-act, per-scenario voice-over text)
    └── replayMetadata.ts       (recording dates, run IDs, expected counts)
```

**Hard rule:** no act file may be longer than 350 lines. If you hit that, refactor a sub-component into `primitives/`.

### D-5. D3 only where SVG/WebGL is the right tool.

Use D3 (already a dependency) for: force-directed graph (existing `ForceGraph.tsx`), the embedding 2D projection (Act 09), chunk-density bars (Act 04), the relationship-emergence animation (Act 08).

Use Framer Motion (add as dep — `framer-motion@^11`) for: act transitions, scroll lock, narrator caption fades, entity-bubble pops, the "snap together" of coreference clusters in Act 07.

Do not use Three.js, react-spring, or canvas-based libs. Keep the bundle tight; the demo is the marketing surface and Lighthouse score matters.

### D-6. Accessibility: this is a serious B2B product, not a TikTok.

Every animated act must:
- Honour `prefers-reduced-motion` (Framer Motion's `useReducedMotion`). When set, animations collapse to instant state changes; SSE driving is unchanged.
- Provide a `Skip to next act` button (top-right of `ActFrame`).
- Provide a `Pause animation` toggle that halts auto-advance.
- Provide `Show event log` button that opens a side drawer with the raw SSE events as JSON (this doubles as the engineer-debug view and as proof to investors that the data is real).
- Have keyboard navigation: `→` advances, `←` rewinds, `Space` toggles pause, `L` opens log.

### D-7. The narrator voice is intellectually honest.

Captions in `narratorScripts.ts` must be precise. Examples:

- **Bad:** "Magic is happening."
- **Good:** "GLiNER (a 500 MB local NER model) scores each chunk by entity density. Chunks below the 0.3 threshold are routed to a lighter extractor. This is not a confidence trick — it is a cost-control hop."

- **Bad:** "AI extracts everything."
- **Good:** "Gemini 2.5 Flash receives the chunk plus the active ontology tier (`standard` = 12 node types, 13 edge types). Output is a JSON object that must validate against the Pydantic v2 `ConflictNode` discriminated union or it is sent back with the error trace, up to 3 retries."

The captions teach. They are the difference between a demo and a sales pitch.

### D-8. The page tells the truth about latency.

Real numbers, displayed prominently:

- Per-act elapsed time (real, from SSE timestamps).
- Cumulative pipeline time.
- Cost estimate ribbon: tokens × price (Gemini Flash @ ~$0.075/M input, $0.30/M output as of 2025-Q4 — pull from `packages/api/.../config.py:GEMINI_PRICING` if defined; otherwise hardcode and add a `# TODO: read from config` comment).
- Comparison ribbon: "Equivalent analyst hours: ~14h (UN DPPA baseline)" — soft estimate, footnoted.

---

## Phase 0 — Data preparation (do this first, half a day)

### 0.1  Curate the Syria corpus

The current `data/seed/samples/syria_civil_war.json` is a *graph seed*, not a *narrative corpus*. The pipeline ingests text, not pre-baked nodes. Create a new file:

```
data/sample_docs/syria_2011_2024_briefing.txt
```

This is a 12,000–18,000-word factual briefing covering 2011 (Daraa protests) through December 2024 (HTS-led Damascus collapse). Structure it as eight section headings with prose underneath, written in the analytical register of an ICG/Crisis Group briefing — not journalism, not Wikipedia.

Sections (each ~1,500–2,500 words):

1. **The Daraa moment and the FSA emergence (March–December 2011).** Bashar al-Assad's response framed as escalation choice. UN Human Rights Council resolutions. Defections.
2. **Multilateralisation and the Geneva I communiqué (2012).** Annan plan. Houla massacre. Sectarian dimension.
3. **The Ghouta chemical attack and the OPCW frame (August 2013).** US "red line" rhetoric, the Russian-brokered chemical weapons removal, the norm-violation/normalisation paradox.
4. **The rise of ISIS and the coalition response (2014).** Mosul fall, US-led coalition airstrikes, the Kurdish question.
5. **Russian intervention and Aleppo's fall (September 2015 – December 2016).** A2/AD layering, hospital bombings, the eastern Aleppo evacuation.
6. **Astana process and the "frozen" middle (2017–2019).** De-escalation zones, the Idlib carve-out, Turkey's Operation Peace Spring.
7. **The COVID-19 plateau and the Captagon economy (2020–2023).** Frozen lines, sanctions architecture, normalisation by Arab League members.
8. **The November 2024 HTS offensive and the December 8 collapse.** Aleppo → Hama → Homs → Damascus in 11 days. Assad's flight to Moscow. The transitional question.

Tone: third-person, present-tense for events being narrated, past-tense for completed outcomes, named actors with role titles on first reference, dates in `YYYY-MM-DD` or `Month YYYY` form to maximise temporal extractor recall.

**Why we write this and not scrape ACLED:** the demo runs against text. ACLED rows are already structured. The whole point of the theatre is showing extraction *from prose*. The Syria briefing is the analogue of *War and Peace* for the warfare domain — long-form, narrative, contested.

Cite each section with a footnote-style `[Source: UN OCHA, 2024-XX-XX]` style marker (these will be ignored by the extractor but make the corpus auditable). Avoid loaded language; the system extracts what is written.

### 0.2  Pre-recorded replays

Once Phase 6 (the live wiring) works once, capture three replays:

```bash
# Run with API up, capture the SSE stream to disk
NEXT_PUBLIC_API_URL=https://api-staging.tacitus.me \
  CAPTURE_REPLAY=apps/web/public/demo/replays/romeo.ndjson \
  pnpm --filter web dev

# Visit /demo, click the Romeo door, let it complete, kill the server.
```

The capture mechanism: a small Next.js middleware (`apps/web/src/middleware.ts` already exists — extend) that, when `CAPTURE_REPLAY` is set, intercepts the SSE stream and tees a copy to disk while passing through to the client. NDJSON: one event per line, `{"t": <ms-since-start>, "event": "<name>", "data": {...}}`.

Repeat for war_peace.ndjson and syria.ndjson.

Commit these to the repo (~50–200 KB each). They are the source of demo truth when offline.

### 0.3  Door manifest

```ts
// apps/web/src/components/demo/data/doors.ts

export const DOORS = [
  {
    id: "romeo",
    title: "Romeo and Juliet",
    subtitle: "Verona, ~1597 — interpersonal escalation cascade",
    domain: "Human friction",
    pitchQuestion:
      "When does this conflict cross from Glasl stage 6 (threats) into stage 9 (together into the abyss)?",
    pitchSubtext:
      "A trained mediator can answer this in 20 minutes. ChatGPT will guess. DIALECTICA computes it from the event chain in 240 ms — and shows you which CAUSED edges drove the verdict.",
    sourceTitle: "Project Gutenberg #1513 — Shakespeare",
    ingestKind: "gutenberg",
    ingestParams: { book_id: "1513", title: "Romeo and Juliet", tier: "standard", max_chars: 0 },
    workspaceId: "demo-romeo",
    expectedCounts: { actors: 9, events: 7, issues: 2, conflicts: 1, edges: 28 },
    replayPath: "/demo/replays/romeo.ndjson",
    handoffQuestionsCount: 8, // count must match Prompt 02's question library
  },
  {
    id: "war_peace",
    title: "War and Peace",
    subtitle: "Russia, 1805–1812 — Napoleonic invasion, civilian impact",
    domain: "Armed conflict",
    pitchQuestion:
      "Is Napoleon's choice to advance after Borodino a free decision or a forced one? How much variance in the 1812 outcome is explained by individual agency?",
    pitchSubtext:
      "Tolstoy posed the question across 1,225 pages. DIALECTICA answers it in two: a Pearl do-calculus over the decision graph plus a Glasl stage trajectory.",
    sourceTitle: "Project Gutenberg #2600 — Tolstoy (587k words; first 80k for the demo)",
    ingestKind: "gutenberg",
    ingestParams: { book_id: "2600", title: "War and Peace", tier: "lite", max_chars: 80000 },
    workspaceId: "demo-war-peace",
    expectedCounts: { actors: 11, events: 9, issues: 2, conflicts: 2, edges: 33 },
    replayPath: "/demo/replays/war_peace.ndjson",
    handoffQuestionsCount: 7,
  },
  {
    id: "syria",
    title: "Syria 2011–2024",
    subtitle: "Multi-party armed conflict, 13 years, 6.8M IDPs",
    domain: "Armed conflict",
    pitchQuestion:
      "Did Russia's September 2015 intervention cause regime survival? Quantify the counterfactual.",
    pitchSubtext:
      "An LLM gives you a confident paragraph with no traceable evidence. DIALECTICA gives you a Pearl do-calculus over the intervention edge, with the territorial-trajectory delta and a confidence interval.",
    sourceTitle: "TACITUS curated briefing (2011-03 → 2024-12)",
    ingestKind: "text",
    ingestParams: { text_path: "/demo/corpora/syria_2011_2024_briefing.txt", tier: "full" },
    workspaceId: "demo-syria",
    expectedCounts: { actors: 22, events: 14, issues: 5, conflicts: 1, edges: 70 },
    replayPath: "/demo/replays/syria.ndjson",
    handoffQuestionsCount: 8,
  },
] as const;
```

Move `syria_2011_2024_briefing.txt` to `apps/web/public/demo/corpora/` so the frontend can fetch it before POSTing to `/extract`. (Or pass `corpus_id` and let the API resolve — implement the simpler path first.)

---

## Phase 1 — Backend additions (one day)

### 1.1  Workspace reset endpoint

Add `POST /v1/workspaces/{ws}/reset` in `packages/api/src/dialectica_api/routers/workspaces.py`. It deletes all nodes and edges with matching `workspace_id` AND `tenant_id`. Multi-tenant invariant: must match both. Add a feature flag `DEMO_RESET_ENABLED` (env var) so this is **off in production tenants** by default; demo tenants only.

```python
@router.post("/{workspace_id}/reset", status_code=204)
async def reset_workspace(
    workspace_id: str,
    tenant_id: str = Depends(get_current_tenant),
    graph: GraphClient = Depends(get_graph_client),
):
    if not settings.demo_reset_enabled:
        raise HTTPException(403, "Reset disabled in this environment")
    if not workspace_id.startswith("demo-"):
        raise HTTPException(403, "Reset only allowed on demo-* workspaces")
    await graph.reset_workspace(workspace_id=workspace_id, tenant_id=tenant_id)
    return Response(status_code=204)
```

Add `GraphClient.reset_workspace`:

```cypher
MATCH (n {workspace_id: $workspace_id, tenant_id: $tenant_id})
DETACH DELETE n
```

Test: `packages/api/tests/test_demo_reset.py` — verify it deletes only the matching workspace; verify it 403s on non-demo tenants; verify the multi-tenant filter holds.

### 1.2  Replay capture middleware

Already sketched in Phase 0.2. Concrete spec:

```ts
// apps/web/src/middleware.ts (extend)
// When CAPTURE_REPLAY env var is set on the dev server, tee SSE responses for
// /v1/workspaces/*/extractions/*/stream to the file at that path.
// Format: one JSON object per line, {"t": deltaMs, "event": eventName, "data": payload}
// First line: {"t": 0, "event": "meta", "data": {"capturedAt": <iso>, "scenarioId": "<id>"}}
```

Document a one-liner in `docs/superpowers/CAPTURING_DEMO_REPLAYS.md`.

### 1.3  Cost-and-counts endpoint

`GET /v1/workspaces/{ws}/extractions/{job_id}/cost` returns a small JSON:

```json
{
  "tokens_in": 142847,
  "tokens_out": 18203,
  "estimated_cost_usd": 0.0119,
  "wall_clock_s": 32.4,
  "step_breakdown_s": {"chunk_document": 0.04, "extract_entities": 12.7, ...}
}
```

The runner already records timestamps; aggregate them. The demo's cost ribbon reads this. If the call 404s (older runs), the ribbon hides itself silently.

---

## Phase 2 — The conductor (`DemoConductor.tsx`) (one day)

### State machine

```
idle → door_picked → resetting → ingesting → streaming → graph_built → handoff
                       │             │           │
                       ▼             ▼           ▼
                    error_*       error_*     error_*  (each can fall back to replay)
```

Use [XState](https://xstate.js.org/) v5 (already in the dep tree per `package.json` — verify; if not, add `xstate@^5`). Reasoning: the act sequencing has enough conditional branches (live vs replay, repair-loop firing, late-arriving relationship events) that hand-rolled `useState` becomes a maintenance bog. XState gives you the visualisation tooling for free, which is itself useful for QA.

### Event source contract

```ts
interface PipelineEvent {
  job_id: string;
  step:
    | "fetch_gutenberg" | "chunk_document" | "gliner_prefilter"
    | "extract_entities" | "validate_schema" | "extract_relationships"
    | "resolve_coreference" | "validate_structural"
    | "compute_embeddings" | "check_review_needed" | "write_to_graph"
    | "stream" | "job";
  status: "started" | "complete" | "failed" | "info" | "ready";
  message?: string;
  counts?: Record<string, number>;
  timestamp?: number;
}
```

`EventStream` (live) and `ReplayDriver` (offline) both produce this. Acts subscribe via context:

```ts
const { latestForStep, allEventsForStep, pipelineMetrics } = useDemoEvents();
```

`latestForStep("extract_entities")` returns the most recent event for that step. `allEventsForStep` returns the array (useful for repair loop, which fires multiple times). `pipelineMetrics` gives elapsed times keyed by step.

### Auto-advance vs scroll

Default: **auto-advance** with `prefers-reduced-motion: no-preference`. Each act sets its `minDwellMs` (typically 4 000–8 000) and a completion predicate (e.g. Act 04 completes when its step's status is `complete`). The conductor advances when both fire.

Manual: **scroll-locked** mode toggleable via a "Manual" button in the top ribbon. Each act becomes a 100vh section with `scroll-snap-align: start` and only advances on explicit click. This is what investors who want to dwell on Act 06 (the repair loop) will use.

The act state and scroll position must be **bidirectionally driven** — programmatic advance updates scroll, manual scroll updates state.

---

## Phase 3 — Acts 00 to 02 (foundational; half a day)

### Act 00 — Mission framing

Single-screen hero. Three propositions, animated in sequence (Framer Motion staggered children, 400 ms each):

1. *"Every conflict — interpersonal, commercial, geopolitical — has a structure."*
2. *"For 60 years, conflict scholars have built theories that name that structure: Glasl on escalation, Zartman on ripeness, Mayer on trust, Pearl on causation."*
3. *"DIALECTICA is the first system to make those theories executable. The result is a deterministic backbone for any question of statecraft, policy, or conflict."*

Below: a faint, looping animation of the 16 theory framework names orbiting a central node. Do not over-design. The text is the work here.

CTA: "Show me." Click → Act 01.

### Act 01 — The three doors

Three large cards in a row. Each card uses the door manifest data:

- Title (e.g. "Romeo and Juliet")
- One-line subtitle
- The pitch question (in italics, as a quote)
- The "ChatGPT will guess. DIALECTICA computes." subtext
- Source attribution (Gutenberg link, Syria briefing source list)
- A subtle hover state that pre-warms the API: on hover for 300 ms, fire `POST /v1/workspaces/{ws}/reset` so the click → ingest path is cold-start-free.

Each card opens its scenario. State transition: `door_picked` with the scenario id.

### Act 02 — Source reveal

The chosen text streams in. Implementation: fetch the text (or for Gutenberg, use the existing `POST /v1/workspaces/{ws}/ingest/gutenberg` which returns the source text in the first SSE event, OR fetch directly via a new `GET /v1/gutenberg/{book_id}/preview?max_chars=4000`). Render in a code-style monospaced viewport, pseudo-typewriter effect at ~2 000 chars/sec (Framer Motion's `motion.span` with sliced text). For W&P, show the first 2 000 chars with a "(587,000 words total — first 80,000 ingested for this demo)" footnote. For Syria, show the first three section headers visibly, hint at the rest.

Once the text fills the viewport, the conductor fires `POST /v1/workspaces/{ws}/extract` (or `/ingest/gutenberg`), gets a `job_id`, and opens the SSE stream. Transition to `ingesting` → `streaming` and Act 03 begins.

The text remains visible — it shrinks to a sidebar in Act 03 onwards as the chunks slide out of it.

---

## Phase 4 — Acts 03 to 05 (core extraction; one day)

### Act 03 — Chunking

The source text (now in a sidebar) is overlaid with semi-transparent rectangular regions, one per chunk. As `chunk_document` events arrive (or in batched form — usually one event with `counts.chunks = N`), each rectangle slides out from the source into a horizontal stack below.

D3 implementation: use `d3.scaleLinear` to map chunk index to x-position. Each chunk is a `<rect>` of width 80px, height 20px, gap 4px. Animate `transform: translateX(...)` via Framer Motion (D3 for scales, Framer for animation — clean separation).

Above the stack: a counter "1 of N", "2 of N"… ticking up. Below: the cumulative chunk count from the SSE.

Caption (from `narratorScripts.ts`):

> "The pipeline splits the text into 2 000-character chunks with 200-character overlap. Sentence boundaries are respected. Overlap exists so an entity mentioned at chunk-edge isn't split — it's the difference between extracting 'Cardinal Wolsey' once versus twice as 'Cardinal' and 'Wolsey'."

### Act 04 — GLiNER pre-filter

Each chunk-rect now grows a vertical bar above it. The bar's height encodes entity density (events from `gliner_prefilter` carry `counts.entity_density_avg` and per-chunk densities in `counts.densities` — confirm with `pipeline_runner.py:142` and patch the runner to emit the per-chunk array if it doesn't already).

Bars under threshold (`< 0.3`) gray out. A line drawn across at `y = threshold` shows the cutoff.

Caption:

> "GLiNER (a 500 MB local NER model, no API call) scores each chunk by the count and type of named entities. Chunks below 0.3 entity density are routed to a lighter extraction path, saving ~40% of Gemini token spend on long literary texts where 60% of chunks are exposition with no actor mentions."

### Act 05 — Gemini Flash extraction

For each above-threshold chunk, entity bubbles pop out. Bubble visuals:

- Circle, radius mapped to confidence (8–22 px).
- Colour per node type: `Actor` → blue, `Event` → red, `Issue` → amber, `Norm` → orange, `Interest` → green, `EmotionalState` → pink, `TrustState` → violet, `PowerDynamic` → purple, `Narrative` → teal, `Process` → cyan, `Outcome` → emerald, `Location` → stone, `Conflict` → crimson. (Match `apps/web/src/lib/utils.ts:NODE_COLORS` exactly.)
- A faint outer ring whose radius equals `confidence × 30 px` — visualises the confidence as halo width.
- A label appearing 200 ms after the pop (entity name, truncated at 18 chars).

Bubbles emerge from chunks and drift toward an empty central staging area, where they cluster. As more entities arrive, the cluster grows.

D3 + Framer combo:
- Use `d3.forceSimulation` with `forceCollide` and `forceCenter` to lay out the cluster.
- Use Framer for the chunk → cluster fly-in animation (initial position from chunk centre, target position from simulation).

Caption (changes mid-act as types appear):

> "Gemini 2.5 Flash receives the chunk plus the active ontology tier. The output is a JSON object validated against the Pydantic v2 ConflictNode discriminated union. Each entity carries a confidence score from the model — visible here as the halo width."
> "Watch the actor types diverge from event types. The model is using the schema, not free-text labels."

---

## Phase 5 — Acts 06 to 08 (validation, coreference, relationships; one day)

### Act 06 — Pydantic validation + repair loop

This is the **most important act** because it is the act that LLMs cannot do.

Implementation:
- When `validate_schema` arrives with `counts.entities_invalid > 0`, the matching bubbles in the cluster flash red and shake.
- A small inset shows the validation error: e.g. `"actor_type='king' invalid; expected one of {individual, group, state, organization, informal_group, ...}"`.
- The flashed bubbles fly *back* to a "Repair" lane (a horizontal channel below the main cluster).
- When `repair_extraction` fires (look for `validate_schema` events with `status: started, message: "Repair attempt 1"`), the bubbles cycle through and re-emerge, most coloured green (now valid), some still red after 3 attempts and then **dropped** (slide off-screen with a faint "✕" trail).
- Counter shows: "Schema-valid: X / Y. Dropped after repair: Z."

D3 + Framer:
- The repair lane is a separate `<g>` group with its own simulation.
- Animate the path from cluster → repair lane → back to cluster as a curved Bézier with `motion.path` and a 600 ms easing.

Caption:

> "An LLM can hallucinate an actor of type 'king' — a type that does not exist in our ontology. Pydantic catches this before it enters the graph and sends the error back to the model, with the valid options. Up to three retries; persistent failures are dropped, not absorbed. This is the line between extraction and confabulation."

> "The graph that emerges in 30 seconds will have zero invalid entities by construction. Try paying a research analyst to guarantee that on a 587 000-word text."

### Act 07 — Coreference resolution

When `resolve_coreference` fires with `counts.merged_pairs = N`:

For each merged pair, two bubbles in the cluster glow, draw a connecting line, and snap together (Framer `layout` animation). The merged bubble takes the canonical name and the union of properties. A small "←" appears next to it for 1 second showing the merge happened.

Show the alias list in a side panel that fills up: `Romeo Montague ← Romeo, young Montague, son of Montague` — 4 aliases collapsed to 1.

Caption:

> "The same entity appears across chunks under different surface forms. Coreference resolution merges them by string similarity, edit distance, and pronoun-binding context. For Romeo and Juliet this typically reduces 47 raw entity mentions to 9 actors. For Tolstoy, 312 mentions to 11 main actors. Without this step, the graph has a 'Pierre' node and a 'Pierre Bezukhov' node and the analytics break."

### Act 08 — Relationship extraction

When `extract_relationships` fires with `counts.edges_valid > 0`:

Edges materialise between the now-stable cluster of node-bubbles. Implementation:

- Each edge is an SVG `path` (curved if both nodes are in the cluster, straight if not).
- `stroke-dasharray` animation: the path draws itself from source to target over 500 ms.
- Colour-coded by edge type using the existing `EDGE_COLORS` palette in `ForceGraph.tsx`. Use the same palette — single source of truth.
- A small label appears at the midpoint after the path completes, showing the edge type (`CAUSED`, `OPPOSED_TO`, etc.).

Edges arrive in batches as the runner processes them. Show the running count.

Caption (changes per scenario):

> Romeo: "Watch the OPPOSED_TO edges form between Houses Montague and Capulet, and the CAUSED chain from Tybalt's death to Romeo's banishment to the double suicide. Five CAUSED edges. Each one will be queryable as a deterministic causal chain."

> War & Peace: "The CAUSED chain here is military: Niemen crossing → Smolensk → Borodino → Moscow → Berezina retreat. Tolstoy's question — was each step forced or chosen? — becomes a graph-traversal problem with answerable Pearl do-calculus semantics."

> Syria: "Three causal layers emerge: violence events, norm violations, and intervention decisions. The 2013 Ghouta attack VIOLATES the CWC and triggers the 2014 OPCW agreement; the 2015 Russian intervention CAUSED the 2016 Aleppo fall, which CAUSED the 2017 Astana process. These are not narrative claims — they are graph edges with confidence scores."

---

## Phase 6 — Acts 09 to 11 (projection, materialisation, handoff; one day)

### Act 09 — Embedding projection

When `compute_embeddings` fires:

Each node-bubble in the cluster fades out and reappears in a **2D scatter plot** beneath. The plot is a UMAP/t-SNE projection of the 768-dim Vertex embeddings. (Frontend implementation: the API doesn't currently expose embeddings — add `GET /v1/workspaces/{ws}/embeddings/2d?method=umap` that returns `[{node_id, x, y}, ...]` after projecting on the server with `umap-learn` for ~30 nodes; this is fast.)

Visual:
- Standard scatter, axes hidden, dots coloured by node type.
- On hover: tooltip with node name + nearest 3 neighbours.
- A faint convex hull around clusters of same-type nodes.
- Caption text: "Semantically similar entities live near each other in 768-dim space. Pierre Bezukhov is closer to Andrei Bolkonsky (both reflective protagonists) than to Napoleon (commander). This is what unlocks structural-similarity queries across cases — the basis for the 'which historical conflict does this most resemble' question in the next act's reasoning theatre."

After 4 seconds, the projection fades and the nodes return to the cluster (or go directly to Act 10).

### Act 10 — Graph materialised

When `write_to_graph` fires `complete`:

The cluster reorganises into the final force-directed layout. Use the existing `ForceGraph.tsx` component — wrap it with a "director's lens" component (`GraphSpotlight.tsx`) that:

- Initial layout uses `forceSimulation` already in `ForceGraph`.
- After settle (2 s), the camera (CSS transform on the SVG container) zooms to fit the bounding box of all nodes.
- Pulses each node type in sequence (actors first, then events, then issues, etc.) by briefly scaling them up 1.3× — a "reveal" of the structure.
- Shows a count panel: "11 actors, 9 events, 2 conflicts, 33 edges. Written to Neo4j Aura, workspace `demo-war-peace`, tenant `demo`. Cypher round-trip: 1.4 s."

Caption:

> "This graph now lives in Neo4j Aura. It can be queried with Cypher, traversed for causal chains, fed into our 16 theory frameworks, and compared structurally to other workspaces. It is the deterministic substrate. What follows is the reasoning."

### Act 11 — Handoff

A single screen:

> *Now you can ask things ChatGPT cannot answer.*
>
> [Pitch question for the chosen scenario, e.g. for W&P:]
> *Is Napoleon's choice to advance after Borodino a free decision or a forced one?*
>
> [CTA button: "Ask DIALECTICA →"]
> [Secondary: "Try a different scenario" → back to Act 01]

Clicking the CTA navigates to `/demo/{scenarioId}/reasoning` — the surface that **Codex Prompt 02** will build. For now, that route can be a stub that says "Reasoning theatre coming online in build #2."

---

## Phase 7 — Polish, telemetry, ship (half a day)

### 7.1  Telemetry

Add PostHog (already in repo per `package.json` — verify) events:

- `demo_door_picked` `{scenario}`
- `demo_act_entered` `{scenario, act, mode: live|replay}`
- `demo_act_dwell` `{scenario, act, dwell_ms}`
- `demo_handoff_clicked` `{scenario}`
- `demo_event_log_opened` `{scenario, act}`
- `demo_pause_toggled` `{scenario, paused}`
- `demo_replay_fallback_triggered` `{scenario, reason}`

Dashboards: act-completion funnel, average dwell per act, drop-off heatmap.

### 7.2  Lighthouse

Targets:
- Performance: ≥ 85 desktop, ≥ 70 mobile.
- Accessibility: ≥ 95.
- Best practices: ≥ 95.

The bundle hits will be Framer Motion (~50 KB) + UMAP (offload to API). Total demo route bundle should stay under 200 KB gzipped. If it doesn't, code-split each act with `dynamic(() => import(...), { ssr: false })`.

### 7.3  Mobile

Mobile is an explicit secondary target. Below 768 px:
- Acts collapse to single-column.
- The 2D projection in Act 09 becomes a smaller plot.
- The graph in Act 10 disables drag (touch is taken by scroll); pinch-zoom enabled.
- Auto-advance dwell increased by 30% (more reading time per act on small screen).

### 7.4  E2E test

Extend `apps/web/e2e/demo-journey.spec.ts`:

```ts
test("Romeo demo: live or replay completes all 11 acts", async ({ page }) => {
  await page.goto("/demo");
  await page.click("text=Romeo and Juliet");
  for (const act of [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]) {
    await expect(page.locator(`[data-act="${act}"]`)).toBeVisible({ timeout: 60_000 });
    await page.click('[data-test="skip-act"]'); // force next
  }
  await expect(page.locator("text=Now you can ask things")).toBeVisible();
});
```

Repeat for war_peace and syria. CI runs this against the replay (deterministic). Staging runs it against the live API once per deploy.

### 7.5  README diff

Update `README.md`'s Quick Start section. Add a "Demo experience" section linking to `/demo` and explaining what to expect (live vs replay).

---

## Phase 8 — Investor ergonomics (half a day)

These are the small, high-leverage touches.

### 8.1  Press-and-hold to reveal raw

Pressing-and-holding any node in Act 10 reveals its underlying JSON for 1 second (small floating panel). Press-and-hold any edge → its `{source, target, edge_type, confidence, weight, evidence_ids[]}`. Investors who want to know "is this real" press and hold; everyone else doesn't notice.

### 8.2  Cypher console

Bottom-right collapsed drawer labelled "Cypher". Expanded, it shows:
- A read-only Cypher console showing the queries the demo just ran (e.g. the relationship-extraction queries, the graph-write queries).
- The current Neo4j Aura connection metadata (host obscured, just `*****.databases.neo4j.io`).
- A "Copy as cURL" button that emits the equivalent API call.

Engineers in the room will open this. It does the heavy lifting of "is this real."

### 8.3  Comparison ribbon

A single-line ribbon visible across acts 4–10:

> "ACLED gives you 47 events as rows. CrisisWatch gives you a 1 200-word narrative. DIALECTICA gives you a 22-actor, 70-edge graph with causal chains, 14 norm violations, and 6 unresolved interests — in 32 seconds, on the same input."

The ribbon's content is per-scenario (don't reuse the wording above for Romeo).

### 8.4  Architecture link

A persistent "How it works ↗" link in the corner, opening `/admin/architecture` in a new tab. (Already exists per `apps/web/src/app/admin/architecture/`.) Investors who want to dig do; everyone else doesn't.

---

## Don't-do list

- Do not rewrite `ForceGraph.tsx`. Extend it.
- Do not introduce a new graph library (cytoscape, vis-network, etc.). D3 force is fine for ≤ 200 nodes; we are at ≤ 30.
- Do not animate every act with the same transition. Each act should feel different.
- Do not show synthetic numbers. Every count is from the SSE.
- Do not auto-play audio narration. Visual + caption only. (Audio is a future Stretch.)
- Do not log to `console.*` in production. Use the EventStream's debug log instead.
- Do not add server-side rendering for the demo route. `"use client"` throughout, dynamic imports, and the demo is a single-page experience.
- Do not delete the existing fallback graph at `data/seed/benchmarks/`. It stays as a contract test for the replays.
- Do not let the demo write to a non-`demo-*` workspace. Hard-code the prefix check.

---

## Acceptance criteria (the merge gate)

A reviewer should be able to:

1. Pull the branch, `pnpm install`, `pnpm --filter web dev`, `make dev-local`, visit `/demo`, click any of the three doors, and see a real ingestion theatre run end-to-end against a real API. ✅
2. Stop the API container, refresh `/demo`, click any door, and see the **same** theatre run from the recorded replay. The amber "Replay mode" banner is visible. ✅
3. Open the event log drawer at any point and see real SSE events. ✅
4. Open the Cypher console and see the real queries. ✅
5. Run `pnpm --filter web test:e2e` and have all three scenarios pass against replay. ✅
6. Hit `/admin/architecture` and find the diagram updated to reflect any new endpoints (`/reset`, `/cost`, `/embeddings/2d`, `/preview`). ✅
7. Read the diff and find no act file longer than 350 lines, no inline styles in act components, no `// TODO: real data` markers. ✅
8. Run Lighthouse on `/demo` and clear the Phase 7.2 thresholds. ✅
9. Follow the README's new "Demo experience" section verbatim and reach a working state. ✅
10. Confirm `data/sample_docs/syria_2011_2024_briefing.txt` exists, is the right length, and ingests successfully (count expectations from the door manifest match within ±10%). ✅

---

## Reflection — why this matters

The current demo is a slideshow. What we are building is a **public proof that a deterministic substrate for conflict exists**. Every act is a small disprovable claim:

- *We can chunk a 587 000-word novel in 1 second.* (Act 03 — a stopwatch confirms it.)
- *We can route low-density chunks to a cheaper extractor.* (Act 04 — the gray bars show it.)
- *We can validate every entity against an academic ontology before it enters the graph.* (Act 06 — the red/green flashing shows it.)
- *We can resolve coreference deterministically.* (Act 07 — the alias list shows it.)
- *We can place these entities in a 768-dim semantic space.* (Act 09 — the projection shows it.)
- *We can write all of this into a multi-tenant graph database in under 2 seconds.* (Act 10 — the count panel shows it.)

The reasoning theatre that follows in Prompt 02 — the questions only DIALECTICA can answer — is built on the trustworthiness of these claims. If we cheat on Act 06, Act 11 collapses. The whole pitch — *deterministic backbone for statecraft* — rests on the fact that no LLM-only competitor can do Act 06 and call themselves a substrate.

This is why every act runs against the real pipeline, why fallbacks are recorded replays not synthetic graphs, and why the Cypher console is exposed. The honesty of the demo is the product.

— End of Prompt 01.
