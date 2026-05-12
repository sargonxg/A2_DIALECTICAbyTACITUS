# PRAXIS Backbone

How the trinity (DIALECTICA + AGON + KAIROS) powers [praxis.tacitus.me](https://praxis.tacitus.me) and the wider TACITUS product family.

---

## What PRAXIS is (and isn't)

PRAXIS is TACITUS's conflict-intelligence SaaS — the consumer-facing product layer above the analytical stack. Where DIALECTICA is the engine, PRAXIS is the cockpit.

PRAXIS users (institutional analysts, mediators, policy teams, HR investigators, conflict researchers) do not write Cypher. They:

- Drop documents into workspaces
- Watch ingestion happen with live progress
- Query "what changed?", "who broke what?", "where's the leverage?"
- Get evidence-traceable answers, not LLM summaries
- Export auditable reports

The product moat is **the graph behind the answers**, and that graph only becomes defensible with all three repos wired.

---

## The unlock — what PRAXIS can show that no competitor can

Compared to generic LLM dashboards or RAG-only tools:

| PRAXIS feature | Requires | Today (DIALECTICA alone) | With trinity wired |
|---|---|---|---|
| Show source quote for every claim | Source spans | Partial (Gemini-extracted, not verified) | ✅ AGON-verified spans, every node |
| "Commitment X breached by actor Y on date Z" | Commitment state machine | ❌ Not modeled | ✅ KAIROS commitments, Allen relations |
| "These two actors contradict each other on Y" | Contradiction edges | ❌ Not modeled | ✅ AGON contradictions as graph edges |
| "What happened between Mar and Sep 2024?" | Temporal interval queries | Partial (Event.occurred_at only) | ✅ Allen-13 interval algebra |
| "Show overlapping sanctions + negotiations" | Episode boundaries | ❌ Not modeled | ✅ KAIROS episodes + Allen OVERLAPS |
| "Evidence coverage on this dossier?" | Quality gates | ❌ Not modeled | ✅ AGON quality gates surfaced |
| Replay reasoning trail | Provenance ledger | ✅ Cloud SQL ledger exists | ✅ Plus per-claim verification trail |
| Confidence-aware answers | Verification status per claim | Probabilistic only | ✅ Deterministic verification status |

Every row in the right column is **table stakes for institutional buyers** (legal, compliance, policy think tanks, HR enterprise). LLM-summary tools cannot fake this — provenance and verification require structural commitment.

---

## PRAXIS query patterns the trinity enables

These map directly to PRAXIS UI features.

### 1. "Show me unfulfilled commitments by actor"

```cypher
MATCH (a:Actor {id: $actor_id})-[:COMMITTED]->(c:Commitment)
WHERE c.state IN ['breached', 'contested', 'pledged']
  AND c.deadline < datetime()
RETURN c, count{(c)-[:EVIDENCED_BY]->(:Evidence)} as evidence_count
ORDER BY c.deadline DESC
```

**Powered by:** KAIROS commitment extraction + state inference. Today: would return empty because Commitment nodes don't exist.

### 2. "Where do the parties disagree?"

```cypher
MATCH (a1:Assertion)-[r:CONTRADICTS]-(a2:Assertion)
WHERE a1.workspace_id = $ws
  AND r.severity >= 3
WITH a1, a2, r
MATCH (a1)<-[:ASSERTS]-(actor1:Actor),
      (a2)<-[:ASSERTS]-(actor2:Actor)
RETURN actor1, actor2, r.mechanism, a1.predicate, a2.predicate
```

**Powered by:** AGON contradiction detection. Today: graph has no CONTRADICTS edges.

### 3. "What's the timeline of the dispute?"

```cypher
MATCH (e:Event)-[r:PRECEDES|MEETS|OVERLAPS]->(e2:Event)
WHERE e.workspace_id = $ws
RETURN e, r, e2
ORDER BY e.occurred_at ASC
```

**Powered by:** KAIROS Allen-13 relations.

### 4. "What's the evidence coverage on this dossier?"

```python
gates = workspace.quality_gates  # AGON output
return {
    "evidence_coverage": gates.evidence_coverage,       # 0.78
    "ambiguity": gates.ambiguity_score,                  # 0.12
    "unresolved_spans": gates.unresolved_count,          # 7
    "contested_claims": gates.contested_count,           # 4
}
```

**Powered by:** AGON quality gates.

### 5. "Replay how this conclusion was reached"

```
1. Ingestion job J at timestamp T
2. KAIROS extracted N events with confidence levels
3. Gemini extracted M claims
4. AGON verified V claims, contradicted C claims
5. Fusion produced graph G
6. Rule R fired because of pattern P in G
7. Agent A synthesized answer using citations [s1, s2, s3]
```

**Powered by:** Existing DIALECTICA provenance ledger + KAIROS/AGON envelope trace IDs.

---

## PRAXIS UI features that this enables

(Mapped to praxis.tacitus.me feature roadmap.)

| PRAXIS feature | Requires | Status with trinity |
|---|---|---|
| **Document drop → live graph build** | Pipeline + SSE | Already works in DIALECTICA |
| **Per-claim source highlighting** | Spans + verification | Requires AGON |
| **Commitment tracker** ("X owes Y") | Commitment state | Requires KAIROS |
| **Contradiction explorer** | Contradiction edges | Requires AGON |
| **Timeline view** ("squeeze time") | Allen relations | Requires KAIROS |
| **Quality dashboard** ("how solid is this analysis?") | Quality gates | Requires AGON |
| **Provenance trail** ("why did the system say this?") | Existing | Enhanced by trinity envelope tracking |
| **"What changed?" alerts** | Cross-document temporal merge | Future KAIROS work |
| **Multi-source corroboration** | Multi-doc actor + event canonical | DIALECTICA workspace + future KAIROS corpus merge |
| **Mediator brief generator** | Reasoning + verified evidence | DIALECTICA agents + AGON quality gates |
| **Compliance audit export** | Full provenance | Existing + enhanced |

---

## The tacitus.me product family — beyond PRAXIS

DIALECTICA + AGON + KAIROS is positioned to power more than PRAXIS:

| Product (existing or planned) | What it needs from trinity |
|---|---|
| **PRAXIS** — conflict intelligence SaaS | Full stack |
| **CONCORDIA** — voice-first conflict mediation (Gemini Live) | DIALECTICA graph queries during conversation; AGON for fact-checking claims user makes |
| **Wind Tunnel** — adversarial reasoning / scenario testing | DIALECTICA agents (Forecaster, Comparator); KAIROS counterfactual timelines |
| **Trust Graph** (TACITUS-internal) | DIALECTICA `/v1/integration/graph`; AGON friction matrices |
| **Future: legal discovery tool** | AGON evidence verification; DIALECTICA provenance |
| **Future: policy timeline tool** | KAIROS as primary; DIALECTICA reasoning |

DIALECTICA's `/v1/integration/*` endpoints already exist (see `packages/api/src/dialectica_api/routers/integration.py`). Each TACITUS product is an integration tenant consuming the graph.

---

## What this means for PRAXIS engineering

PRAXIS frontend lives at `sargonxg/PRAXIS_NEXTJS_TACITUS`. It currently consumes DIALECTICA via REST.

To prepare PRAXIS for trinity outputs:

1. **Update data model.** New TypeScript types from `@tacitus/contracts`: `Commitment`, `Assertion`, `Contradiction`, `AllenRelation`, `QualityGates`.
2. **New UI components.**
   - `<CommitmentTracker>` — list, filter, state badge
   - `<ContradictionExplorer>` — pair view with side-by-side evidence
   - `<TimelineView>` — Gantt-style Allen relation layout
   - `<QualityGauge>` — workspace health card
3. **Provenance overlay.** Click any node/edge → see source spans + which service emitted it.
4. **Query shortcuts.** Map UI actions to graph queries above.

PRAXIS doesn't need to know about KAIROS or AGON directly — all calls go through DIALECTICA's `/v1/integration/*` endpoints. Trinity is invisible at the API surface but visible in the data richness.

---

## Selling the moat

For pitches, demos, sales:

> **"We don't summarize conflicts. We structure them."**
>
> Every claim PRAXIS shows you traces to a specific quote in a specific document.
> Every commitment has a state — pledged, active, fulfilled, breached.
> Every contradiction is explicit, not implicit in prose.
> Every event sits on a timeline with formal relationships to other events.
> Every analysis is replayable, auditable, defensible.
>
> Generic AI tools cannot do this. They produce paragraphs. We produce graphs.

This is true only when the trinity is wired. Until then, it's aspirational.

---

## Success criteria — PRAXIS-ready

The integration is "done enough for PRAXIS" when:

- [ ] Single document → KAIROS + Gemini + AGON → fused graph, end to end, in < 60s
- [ ] Every node in resulting graph carries `{span, sha256, verification_status}`
- [ ] At least 80% of claims marked `verified` or `denied` (not `unresolved`)
- [ ] Commitments have correct state machine transitions (`pledged → active → fulfilled/breached`)
- [ ] Allen relations cover at least 60% of dated event pairs
- [ ] Quality gates surface in workspace summary
- [ ] PRAXIS UI shows commitment tracker + contradiction explorer + timeline
- [ ] Provenance overlay works for every node
- [ ] One paying customer ships PRAXIS with trinity-powered analysis

Last item is the only one that matters.

---

*See [`ROADMAP.md`](./ROADMAP.md) for the path there.*
