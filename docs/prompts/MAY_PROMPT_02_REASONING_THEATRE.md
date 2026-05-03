# Codex Prompt 02 — DIALECTICA Demo: The Deterministic Reasoning Theatre

> **Repository:** `A2_DIALECTICAbyTACITUS` (Next.js 15 monorepo + Python packages)
> **Branch convention:** `feat/demo-reasoning-theatre`
> **Pre-requisite:** `CODEX_PROMPT_01_INGESTION_THEATRE.md` is merged. The `/demo` route now ends in a built graph for one of three scenarios (`romeo`, `war_peace`, `syria`) and a stub link to `/demo/{scenarioId}/reasoning`.
> **Estimated effort:** 5-day Claude Code build.
> **Status when this prompt is handed to you:** The graph is in Neo4j. The 16 theory frameworks (`packages/ontology/.../theory/`) and 9 symbolic rule modules (`packages/reasoning/.../symbolic/`) compile and pass tests. The reasoning UI is a stub. Your job is to build the surface that converts a built graph into answers, traced and citable, that an LLM cannot produce.

---

## TL;DR — what you are building

A new route `/demo/{scenarioId}/reasoning` that hosts the **central pitch of TACITUS**: questions of statecraft, policy, and conflict that require a deterministic substrate to answer with citations.

For each of the three scenarios — *Romeo and Juliet*, *War and Peace*, *Syria 2011–2024* — there is a curated library of seven to eight **deterministic questions** that:

1. Cannot be answered with citations by any frontier LLM today.
2. *Can* be answered by DIALECTICA via a specific composition of symbolic rules + GraphRAG retrieval, with a traceable inference chain ending at named graph nodes and edges.
3. Are grounded in published academic frameworks (Glasl, Zartman, Pearl, Mayer, French/Raven, Kriesberg, Galtung, Lederach, Walter, Putzel) — explicitly cited inline.
4. Connect to a stake an investor or policy buyer recognises: war recurrence, intervention efficacy, mediation timing, alliance brittleness.

The page is designed around four moves:

- **Move A — The library.** A scrollable list of eight questions per scenario. Each question has a quoted academic source and a one-line stake.
- **Move B — Side-by-side answer.** Click a question. Two panels animate in: left = a frontier LLM's freeform answer (pre-recorded; never live; we never pay OpenAI/Anthropic to lose this comparison); right = DIALECTICA's traced answer with citations rendered as clickable graph paths.
- **Move C — The trace.** Below the answer, an animated reveal of the reasoning chain: which nodes were retrieved (GraphRAG), which symbolic rule fired (e.g. `escalation.compute_glasl_stage`), which Cypher queries ran, which framework was invoked, what confidence the answer carries.
- **Move D — Counterfactual / structural similarity.** For one question per scenario, the user can toggle off an event/edge in the graph and see the answer re-derive. For the structural-similarity question, a panel slides in showing the K nearest historical conflicts in embedding space, with explanations.

Every panel is animated with intent (not gratuitous), every claim is traceable to a graph object, and the panel headers carry the academic citation in plain view.

---

## Repository contract

Read in this order:

| Path | Why |
|---|---|
| `docs/neurosymbolic-rationale.md` (the §3, §5, §7 sections) | The bridge protocol — symbolic fires first, neural fills second. Every answer in this prompt enacts that protocol. |
| `docs/theory-frameworks.md` | The 16 frameworks, what each `assess()` and `score()` returns. |
| `packages/ontology/src/dialectica_ontology/benchmark_questions.py` | Existing diagnostic question library — we will supersede it with curated, narrative-grade questions but reuse the schema. |
| `packages/ontology/src/dialectica_ontology/theory/{glasl,zartman,fisher_ury,french_raven,mayer_trust,pearl_causal,kriesberg,winslade_monk,galtung,lederach}.py` | The frameworks each question invokes. Read `describe()`, `assess()`, `score()` carefully. |
| `packages/reasoning/src/dialectica_reasoning/symbolic/{escalation,ripeness,trust_analysis,power_analysis,causal_analysis,network_metrics,pattern_matching}.py` | The symbolic modules that fire deterministically. Each question maps to one or more of these. |
| `packages/reasoning/src/dialectica_reasoning/graphrag/retriever.py` | The hybrid retrieval (vector + N-hop traversal) that grounds neural synthesis. |
| `packages/reasoning/src/dialectica_reasoning/agents/{theorist,analyst,forecaster,mediator,comparator}.py` | The 6 agents. The reasoning theatre composes specific agent calls per question. |
| `packages/reasoning/src/dialectica_reasoning/hallucination_detector.py` | The detector. Every answer surface in this UI must show a hallucination-risk indicator. |
| `data/seed/benchmarks/{romeo_juliet,war_peace,jcpoa}_gold.json` | Gold standard. We use these for the Romeo and W&P benchmark backstops. |
| `apps/web/src/components/graph/ForceGraph.tsx` | The graph renderer. We will pass a `highlightPath` prop to animate citation traces. |
| `packages/reasoning/src/dialectica_reasoning/query_engine.py` | The single entry point that composes retrieval → symbolic → neural. The reasoning theatre's API client wraps this. |

---

## Architectural decisions (locked)

### D-1. The "answer" is a structured object, never a string.

Every question routes through `query_engine.answer(question_id, workspace_id, tenant_id)` and returns a `ReasoningResult`:

```python
class ReasoningResult(BaseModel):
    question_id: str
    answer_summary: str           # 1-3 sentences, surface-level
    answer_full: str              # full narrative, may be 200-400 words
    confidence: float             # 0..1
    determinism_score: float      # 0..1; 1.0 if pure symbolic, lower if neural-augmented
    primary_framework: str        # e.g. "glasl"
    cited_node_ids: list[str]
    cited_edge_ids: list[str]
    cypher_queries: list[str]     # the actual queries that ran
    symbolic_rules_fired: list[str]  # module.function names
    hallucination_risk: float     # 0..1; from hallucination_detector
    counterfactual_handle: Optional[CounterfactualHandle]  # only for questions that support it
    structural_similarity_handle: Optional[SimilarityHandle]
    elapsed_ms: int
    cost_usd: float
```

The frontend renders fields, not prose blobs. This is what makes the trace UI possible.

### D-2. Question library is curated, not generated.

A new file `data/seed/reasoning_library.json` defines exactly 23 questions across 3 scenarios (8 + 7 + 8). Each question is hand-written and hand-validated. We are not auto-enumerating the existing `benchmark_questions.py` — those questions are diagnostic ("how many actors?") and bore investors. The reasoning library is **the demo's editorial product** — every question is one we are willing to defend in a meeting.

### D-3. The LLM-comparison panel is pre-recorded, dated, and honest.

We do **not** call OpenAI/Anthropic from the demo. We pre-record one frontier-LLM answer per question (using GPT-4o, Claude 4.5 Sonnet, Gemini 2.5 Pro — pick one per question to keep things fair across vendors), label each with the date and model version, and ship them as static JSON. The panel header reads: *"Asked of {model_name} on {capture_date}. Identical question text. No retrieval, no system prompt beyond 'Answer concisely with citations'. The model's answer is reproduced verbatim."*

This is editorially defensible because we never claim "the LLM cannot answer" — we claim "the LLM cannot answer with verifiable citations to a structured representation." The captured answers will, in fact, often be eloquent. They will simply have no traceback.

### D-4. The trace is a first-class UI surface.

A `ReasoningTrace` panel renders, in order:
1. The question.
2. The retrieved subgraph (animated overlay on the main `ForceGraph`).
3. The Cypher queries (collapsed by default, expandable).
4. The symbolic rule(s) fired with their inputs and outputs.
5. The synthesis prompt sent to the LLM (collapsed).
6. The LLM response.
7. The hallucination-detector verdict.
8. The final `ReasoningResult` JSON (collapsed).

This panel is open by default for the *first* question the user clicks (so they see the machinery once); closed by default for subsequent questions (so they read answers, not internals). The toggle persists across questions in the session.

### D-5. Counterfactuals are real, not theatrical.

For supported questions, the user can click an event or edge in the graph and select "Remove for counterfactual". The frontend sends `POST /v1/workspaces/{ws}/reason/counterfactual` with `{question_id, removed_node_ids[], removed_edge_ids[]}`. The API:

1. Loads the workspace graph.
2. Constructs a *transient* in-memory copy with the specified nodes/edges deleted.
3. Re-runs `query_engine.answer` against the transient graph.
4. Returns the new `ReasoningResult` plus a diff: which fields changed, by how much.

Critically: the transient graph is **never written back to Neo4j**. The Pearl do-calculus semantics require working with a graph mutilation that does not persist. The endpoint must be explicit about this in the response.

### D-6. Structural similarity uses both embeddings and graph topology.

The existing `packages/reasoning/.../graphrag/community.py` and `kge/predictor.py` provide the building blocks. The structural-similarity feature combines:

- **Semantic distance**: cosine similarity on Conflict-node embeddings.
- **Topological distance**: edit distance on actor-issue-event topology, computed via approximate graph kernel (Weisfeiler-Lehman, k=3).

The handle returns a list of `(workspace_id, conflict_name, semantic_dist, topological_dist, combined_dist, explanation)`. The explanation is a short paragraph synthesised by the Comparator agent, with citations to the matched nodes in the comparison case.

For this demo, the comparison cases are pre-loaded into separate workspaces:

- `corpus-vendetta` — Hatfield-McCoy 1880s, Albanian gjakmarrja 1990s, Pashtun badal codes (compare against Romeo & Juliet)
- `corpus-imperial-overreach` — Athens-Sicily 415 BCE, Hitler-Russia 1941, US-Vietnam 1965 (compare against War & Peace)
- `corpus-multiparty-civil-war` — Lebanon 1975–90, Bosnia 1992–95, Yemen 2014– (compare against Syria)

Each is seeded from a curated briefing in `data/sample_docs/`, ingested once at deploy time, and never modified.

### D-7. Page bundle: lazy, fast, observable.

Same Lighthouse targets as Prompt 01 (≥85 perf, ≥95 a11y). Add Sentry breadcrumbs for every reasoning call so we can debug failed traces in production. PostHog events for engagement.

---

## The question library — full content

Below is the full editorial content for `data/seed/reasoning_library.json`. Build the file exactly to spec; the wording matters because investors will read these aloud.

### Scenario: `romeo` (8 questions)

#### R-1 — *"At what Glasl stage does this conflict pivot from objectifiable to intractable, and on which event?"*

- **Stake:** Mediators have 20-minute windows to identify whether they are facing a stage 5 (loss-of-face) or stage 6 (threats) conflict. The interventions diverge sharply — process consultation vs. third-party guarantees. Getting it wrong wastes the only entry point.
- **Academic anchor:** Glasl, F. (1999). *Confronting Conflict.* Stages 5–6 transition is defined by the introduction of public threats and the revocation of face-saving exits.
- **Primary framework:** `glasl`
- **Symbolic rules:** `escalation.compute_glasl_stage`, `causal_analysis.find_pivot_event`
- **Expected answer:** "The pivot is the Mercutio death (Act III Scene 1). Before it, the conflict is at stage 4–5 (coalitions, loss of face). After it, Romeo's killing of Tybalt and the prince's banishment edict put the conflict at stage 6 (threats with strategic intent), and the secret marriage now creates the conditions for stage 7. Confidence 0.92, deterministic from the CAUSED chain Brawl → Mercutio_death → Tybalt_death → Banishment."
- **LLM comparison:** GPT-4o will give a fluent answer naming the right event but no graph citation, no stage rule trace, no confidence number tied to evidence.
- **Counterfactual handle:** Yes — remove the Mercutio_death node, re-derive. Expected new stage: stays at 5; the trajectory becomes a different play.
- **Structural similarity handle:** No.

#### R-2 — *"Who is the structural spoiler? Quantify by betweenness centrality on de-escalation paths."*

- **Stake:** Spoilers are the named enemy of every peace process. Putzel (2010) and Stedman (1997) define the typology; identifying them in a live conflict is the first decision a special envoy makes.
- **Academic anchor:** Stedman, S. J. (1997). "Spoiler Problems in Peace Processes." *International Security* 22(2). Putzel, J. (2010) on hard-line spoilers.
- **Primary framework:** `network_metrics`
- **Symbolic rules:** `network_metrics.compute_betweenness`, `pattern_matching.identify_spoilers`
- **Expected answer:** "Tybalt Capulet. Betweenness centrality 0.71 on the de-escalation subgraph (paths from Friar_Lawrence_Mediation to Reconciliation must traverse him in 4 of 6 cases). He removes Mercutio (cuts the Romeo-Mercutio-Prince Escalus alliance bridge), forcing the conflict into the bilateral Capulet-Montague channel where no mediator has standing. Stedman typology: hard spoiler (total spoiler in his framing — incompatibility with any settlement involving Montague-Capulet rapprochement)."
- **LLM comparison:** Claude will name Tybalt correctly. It will not produce a centrality number; it will not cite the Stedman typology with the alliance-bridge mechanism; it will not show the underlying graph paths.
- **Counterfactual:** No.
- **Similarity:** No.

#### R-3 — *"Why does Friar Lawrence's Track-II mediation fail? Diagnose with French/Raven."*

- **Stake:** Track-II mediators (academics, religious leaders, NGOs) routinely walk into conflicts where they have expert and referent power but lack coercive and legitimate power. Diagnosing this asymmetry pre-engagement is the difference between a saved process and a wasted year.
- **Academic anchor:** French, J. R. P. & Raven, B. (1959). "The Bases of Social Power." Plus Bercovitch on Track-II mediation legitimacy.
- **Primary framework:** `french_raven`
- **Symbolic rules:** `power_analysis.compute_power_distribution`, `pattern_matching.match_mediator_template`
- **Expected answer:** "Friar Lawrence holds high expert (0.78 — religious authority + apothecary skill), high referent (0.65 — trusted by both Romeo and Juliet personally), but coercive 0.05, reward 0.10, legitimate 0.20 (sub-prince ecclesiastical authority, no enforcement reach over noble houses). The secret marriage requires legitimate power he lacks: the moment Lord Capulet arranges the Paris match, the Friar's mediation has no countervailing force. Bercovitch (1991) predicts Track-II failure when (coercive + legitimate) < 0.30 and the conflict has reached Glasl ≥ 5. Both conditions are met."
- **LLM comparison:** Will mention "lack of authority". Will not produce the five-axis power vector. Will not cite the Bercovitch threshold.
- **Counterfactual:** No.
- **Similarity:** No.

#### R-4 — *"If Mercutio survives Act III Scene 1, project the conflict trajectory."*

- **Stake:** Counterfactual reasoning is the daily work of intelligence shops. The question "what if X had been prevented" requires a do-calculus discipline most analysts approximate badly.
- **Academic anchor:** Pearl, J. (2009). *Causality.* Chapter on interventions and the do-operator.
- **Primary framework:** `pearl_causal`
- **Symbolic rules:** `causal_analysis.do_intervention`, `escalation.project_trajectory`
- **Expected answer:** "Removing Mercutio_death from the graph eliminates the Romeo-Tybalt revenge edge and the banishment cascade. The conflict's projected trajectory: stays at Glasl stage 5 (loss of face) for the duration of the Capulet-Paris arrangement subplot. The double suicide cascade requires Romeo's banishment as a precondition; without it, Romeo can openly contest the Paris match through Friar Lawrence's now-credible mediation. Projected outcome: stage 4–5 stable rivalry with intermittent skirmishes, no double suicide. Confidence 0.71 — counterfactuals over Pearl's L2 carry irreducible uncertainty in the absence of repeated trials."
- **LLM comparison:** Will speculate confidently. Will not flag the counterfactual confidence ceiling.
- **Counterfactual:** *Yes — this question itself is the counterfactual.* The user toggles off `Mercutio_death` and the answer re-derives.
- **Similarity:** No.

#### R-5 — *"Is the conflict ripe for resolution at the moment of the secret marriage? Compute MHS and MEO."*

- **Stake:** The single most underrated practical tool in conflict mediation is Zartman's ripeness theory. Mistiming an intervention against an unripe conflict burns the mediator's credibility for years.
- **Academic anchor:** Zartman, I. W. (1989). *Ripe for Resolution.*
- **Primary framework:** `zartman`
- **Symbolic rules:** `ripeness.compute_mhs_meo`
- **Expected answer:** "Not ripe. MHS (Mutually Hurting Stalemate) = 0.12 (no party has paid significant cost yet — the brawls are skirmishes, no major casualties on either side at this point in the play). MEO (Mutually Enticing Opportunity) = 0.31 (the Friar's vision of family reconciliation is not credible to either house; the marriage is hidden, not publicly negotiated). Composite ripeness 0.21. Friar Lawrence's intervention is 'pre-ripe' — a structural mistake. The conflict will need to reach the costs of the double suicide before either house has both pain and exit. Tragedy as ripeness mechanism is not a metaphor; it is the deterministic prediction of the model."
- **LLM comparison:** Will gesture at "tensions are high". Will not produce MHS/MEO numbers. Will not name the pre-ripe diagnosis.
- **Counterfactual:** No.
- **Similarity:** No.

#### R-6 — *"Which real-world conflicts share this actor-event-norm topology?"*

- **Stake:** Pattern recognition across cases is what separates a senior analyst from a junior one. Quantifying it removes the dependence on one analyst's career memory.
- **Academic anchor:** George, A. L. & Bennett, A. (2005). *Case Studies and Theory Development.* On structured-focused comparison.
- **Primary framework:** `pattern_matching` + `kge.predictor`
- **Symbolic rules:** `pattern_matching.compute_topology_signature`, `community.find_similar_workspaces`
- **Expected answer:** "Top three structural neighbours by combined embedding + graph kernel distance: (1) Hatfield-McCoy feud, Appalachia 1878–1891 (combined dist 0.18 — bilateral kin-based feud, weak central authority, terminating event = federal intervention). (2) Albanian gjakmarrja blood feuds, Tropoja district 1992–2005 (dist 0.21 — kanun-coded honor obligations, generational extension, dormant→reactivated dynamic). (3) Pashtun badal cycles, FATA 1950s–present (dist 0.27 — honor revenge as governance substitute when state is absent). Romeo's structural family is 'identity-coded vendettas in weak-state contexts' — *not* 'star-crossed lovers tragedies'. The latter is a literary genre; the former is the operational class."
- **LLM comparison:** Will list classic Western literary parallels (West Side Story). Will not produce a graph-kernel distance. Will not name the operational class.
- **Counterfactual:** No.
- **Similarity:** *Yes — this question is the similarity surface.* The panel slides in showing the three neighbours with full graphs.

#### R-7 — *"What unstated interest does Lord Capulet hold that the play never makes explicit?"*

- **Stake:** Fisher/Ury principled negotiation hinges on identifying interests that parties themselves do not articulate. This is the move that turns a positional negotiation into a productive one. Doing it from text rather than from interview is hard.
- **Academic anchor:** Fisher, R. & Ury, W. (1981). *Getting to Yes.*
- **Primary framework:** `fisher_ury`
- **Symbolic rules:** `pattern_matching.infer_unstated_interests`
- **Expected answer:** "Dynastic continuity through advantageous marriage. Stated position: 'Juliet will marry Paris.' Stated reason: filial obedience, family honour. Unstated interest (priority 0.84, derived from the Paris-arrangement subgraph): securing alliance with the Prince's kin (Paris is Escalus's kinsman) — i.e., closing the gap to the legitimate authority that has been threatening both houses with execution. Capulet's marriage strategy is a *legitimacy-purchase* against the Prince's coercive power. Romeo, as a Montague, is structurally incapable of offering this hedge. The conflict is not romantic — it is dynastic risk-management."
- **LLM comparison:** Will say "family alliance" or "social standing". Will not name the legitimacy-purchase mechanism with reference to Prince Escalus's coercive threat.
- **Counterfactual:** No.
- **Similarity:** No.

#### R-8 — *"What intervention would Lederach's conflict transformation framework recommend, and at what timing?"*

- **Stake:** Transformation vs. management is the central debate in conflict resolution practice. Lederach's framework is the canonical bridge.
- **Academic anchor:** Lederach, J. P. (2003). *The Little Book of Conflict Transformation.* Plus Lederach (1997) on the four levels.
- **Primary framework:** `lederach`
- **Symbolic rules:** `pattern_matching.match_lederach_levels`
- **Expected answer:** "Personal: low priority (the protagonists are dead). Relational: high priority (Montague–Capulet families, plus Capulet–Paris kin via Escalus). Structural: highest priority (Verona's adjudication mechanisms have failed — Prince Escalus's prior decrees were unenforceable; the city needs a noble-houses reconciliation court, not another decree). Cultural: medium-long priority (the 'ancient grudge' narrative needs an alternative story — see Winslade & Monk narrative mediation). Recommended sequencing: structural reform (a binding noble council) precedes cultural narrative work; relational mediation can begin immediately but is downstream of structural change. Timing: the moment of the double suicide is the single window when both houses are simultaneously above the pain threshold; Lederach's 'critical yeast' moment. Prince Escalus correctly seizes it — the play's final scene is the model's prescribed intervention."
- **LLM comparison:** Will recommend "reconciliation". Will not produce the four-level decomposition with sequencing.
- **Counterfactual:** No.
- **Similarity:** No.

### Scenario: `war_peace` (7 questions)

#### W-1 — *"How much variance in the 1812 outcome is explained by individual agency vs structural forces?"*

- **Stake:** Tolstoy's central philosophical claim, posed in Book V and Epilogue Two: history is not made by great men. Translating this into a testable question — what fraction of outcome variance is attributable to high-discretion decisions vs. low-discretion responses to constraint — is the missing computational move that political historians have been gesturing at since Carr (1961).
- **Academic anchor:** Tolstoy, *War and Peace*, Epilogue II. Carr, E. H. (1961). *What Is History?* Pearl, J. (2009) on causal effect decomposition.
- **Primary framework:** `pearl_causal`
- **Symbolic rules:** `causal_analysis.decompose_variance`, `pattern_matching.classify_decision_constraint_density`
- **Expected answer:** "Of 14 decision events in the extracted graph, 9 are high-constraint (low discretion — e.g. Napoleon's logistical retreat from Moscow given a 75% army-attrition rate; Kutuzov's strategic withdrawal at Borodino given a 1.4:1 manpower disadvantage). 5 are low-constraint (high discretion — Napoleon's choice to advance from Smolensk in August; Kutuzov's choice not to defend Moscow; Alexander I's refusal of negotiation overtures). Outcome variance attributable to the 5 high-discretion decisions: 0.34. Variance attributable to structural constraints: 0.66. Tolstoy's claim is supported within the constraints of a single case — but the 0.34 is non-trivial. Napoleon's individual decision to advance after Smolensk is the largest single-decision variance contributor (0.18). Note: this is a per-case decomposition, not a generalisation across all wars; methodological caveats on small-n causal inference apply."
- **LLM comparison:** Will quote Tolstoy's claim verbatim. Will not produce a numerical decomposition. Will not flag the small-n caveat.
- **Counterfactual:** Yes — the user can toggle off Napoleon's Smolensk-advance decision and watch the variance number recompute.
- **Similarity:** No.

#### W-2 — *"Was Kutuzov's decision to abandon Moscow rational? Compute his BATNA."*

- **Academic anchor:** Fisher & Ury (1981) on BATNA. Plus Brodie (1973) *War and Politics* on attrition strategy.
- **Primary framework:** `fisher_ury` + custom logistics modelling
- **Symbolic rules:** `power_analysis.compute_batna`, `causal_analysis.simulate_attrition_curve`
- **Expected answer:** "Yes. BATNA at Moscow: scorched-earth withdrawal + reinforcement absorption = projected French force degradation 8–11% per week through October-November vs. Russian reinforcement 3–4% per week. Defensive engagement at Moscow with available forces: projected casualties exceed reinforcement rate by 2.3:1, breakeven date November 15. Kutuzov's BATNA dominates by Q3 1812. The decision is not heroic; it is dominant-strategy. Tolstoy's framing as quasi-mystical patience is poetically true and strategically the correct call. The deterministic result aligns with Tolstoy's intuition; what the model adds is the quantitative margin — Kutuzov was right by ~2 weeks of projected attrition convergence."
- **LLM comparison:** Will say "yes, scorched earth was the right call". Will not produce the attrition convergence math.
- **Counterfactual:** No.
- **Similarity:** No.

#### W-3 — *"Glasl trajectory of the Napoleon–Russia conflict: when does it cross stage 7→8→9?"*

- **Academic anchor:** Glasl (1999), specifically the stage 7–9 progression that defines war as a political instrument.
- **Primary framework:** `glasl`
- **Symbolic rules:** `escalation.compute_glasl_stage`, `escalation.compute_trajectory`
- **Expected answer:** "Niemen crossing (24 June 1812) → stage 7 (limited destructive blows). Borodino (7 September 1812) → upper stage 7. Moscow burning (14 September 1812) → stage 8 (fragmentation; the city's destruction breaks the war's political control mechanism on both sides). Berezina (26–29 November 1812) → stage 9 (together into the abyss; the army's destruction is no longer a means but the outcome). Confidence 0.94. Each transition is event-anchored; the dates are the deterministic stage boundaries."
- **LLM comparison:** Will offer a fluent narrative arc. Will not name the four-stage transition with dates.
- **Counterfactual:** No.
- **Similarity:** No.

#### W-4 — *"Does the partisan irregular fighter (Denisov-style) materially shift the outcome, or is Tolstoy's portrayal decorative?"*

- **Academic anchor:** Beckett, I. F. W. (2001). *Modern Insurgencies and Counter-insurgencies.* Plus Mao (1937) on protracted war.
- **Primary framework:** `network_metrics`
- **Symbolic rules:** `network_metrics.compute_edge_contribution`, `causal_analysis.decompose_attrition_sources`
- **Expected answer:** "Material. Partisan-attributable French casualties on the retreat (extracted from event severities + actor attribution edges): ~22% of total Grande Armée losses between Moscow and the Berezina. Removed from the graph, the projected French survival rate at the Berezina rises from ~10% to ~28%. Tolstoy's portrayal is empirically calibrated, not decorative. This contradicts the older British military-history tradition (e.g. Chandler 1966) that emphasises weather and logistics; the partisan layer is a co-equal causal factor. Confidence 0.78 — the irregularity attribution is partially overlapping with weather/logistics in the source corpus, so the decomposition has wider error bars than W-1."
- **LLM comparison:** Will affirm the partisans mattered. Will not produce the casualty attribution share or contradict Chandler.
- **Counterfactual:** Yes — toggle off the partisan-warfare events and watch the survival rate recompute.
- **Similarity:** No.

#### W-5 — *"Counterfactual: if Napoleon retreats from Smolensk in August 1812, does France retain Continental hegemony through 1815?"*

- **Academic anchor:** Pearl (2009) on counterfactual reasoning. Plus Schroeder (1994) *The Transformation of European Politics.*
- **Primary framework:** `pearl_causal`
- **Symbolic rules:** `causal_analysis.do_intervention`, `pattern_matching.compare_hegemony_trajectory`
- **Expected answer:** "Probable retention through 1813; uncertain in 1814; lost by 1815 absent Russia campaign or not. Removing the Moscow campaign preserves ~250 000 Grande Armée veterans through 1813. The Sixth Coalition's 1813 spring campaign (Lützen, Bautzen) becomes a French strategic victory rather than a political stalemate. However, the British naval blockade and the Spanish Peninsula war remain unchanged; structural causes of French overextension persist. Confidence 0.55 — counterfactuals over multi-year horizons compound uncertainty rapidly. The model returns *probable continuation through 1813, indeterminate thereafter*. Schroeder argues the structural transformation of European politics was already underway pre-1812; this is consistent with the model's 1815 verdict."
- **LLM comparison:** Will give a confident either/or. Will not flag the compounding-uncertainty caveat.
- **Counterfactual:** *Yes — this question is the counterfactual.*
- **Similarity:** No.

#### W-6 — *"Map structural similarity to other imperial overreach cases."*

- **Academic anchor:** Kennedy, P. (1987). *The Rise and Fall of the Great Powers.*
- **Primary framework:** `pattern_matching` + `kge.predictor`
- **Symbolic rules:** `community.find_similar_workspaces`
- **Expected answer:** "Top neighbours: Athens-Sicily 415 BCE (combined dist 0.16 — naval power overextending into landlocked theatre, terminating event = total force destruction), Hitler-Russia 1941–43 (dist 0.19 — explicit modelling on Napoleon by both Hitler and German general staff, near-identical logistical curve), US-Vietnam 1965–73 (dist 0.34 — counterinsurgency dimension is structurally distinct, but the political-imperial overreach pattern matches). Romeo similarity score against this same corpus: 0.71+ on every comparison — confirming the operational-class assignment from R-6 is meaningfully different (literary vendetta is *not* in the same class as imperial overreach)."
- **LLM comparison:** Will list the cases. Will not produce the dist numbers nor the cross-corpus separation check.
- **Counterfactual:** No.
- **Similarity:** *Yes.*

#### W-7 — *"What does Mayer trust analysis say about the Napoleon–Alexander I dyad before, during, and after?"*

- **Academic anchor:** Mayer, R. C., Davis, J. H., & Schoorman, F. D. (1995). "An Integrative Model of Organizational Trust." *Academy of Management Review* 20(3).
- **Primary framework:** `mayer_trust`
- **Symbolic rules:** `trust_analysis.compute_dyad_trust`, `trust_analysis.detect_breach_events`
- **Expected answer:** "Tilsit (July 1807): A 0.55, B 0.40, I 0.50 → composite 0.48 (fragile post-defeat truce). Erfurt (October 1808): A 0.60, B 0.35, I 0.45 → 0.47 (slight ability uplift, benevolence falling). 1810–1811 Continental System non-compliance: I drops to 0.20 (Russia openly trades with Britain — integrity violation in the Mayer sense). 1812 invasion: composite 0.05 (full breach). Post-1815 Holy Alliance: composite 0.55 (integrity restored via formal regime). The trajectory tracks the Mayer model's prediction: trust collapses on integrity violations more sharply than on ability or benevolence shifts. Application: post-conflict reconciliation must restore integrity dimension first; ability and benevolence are downstream."
- **LLM comparison:** Will narrate the trust arc fluently. Will not decompose into A/B/I dimensions across four time-points.
- **Counterfactual:** No.
- **Similarity:** No.

### Scenario: `syria` (8 questions)

#### S-1 — *"Did Russia's September 2015 intervention cause regime survival? Quantify the counterfactual."*

- **Stake:** This is the live debate. Charap, Friedman, and others continue to argue both ways. A traceable answer is what makes the demo land.
- **Academic anchor:** Charap, S., & Geist, E. (2018). *Russia's Use of Military Power.* RAND. Plus Pearl (2009).
- **Primary framework:** `pearl_causal`
- **Symbolic rules:** `causal_analysis.do_intervention`, `causal_analysis.compute_territorial_trajectory`
- **Expected answer:** "Yes, with high confidence. Removing the Russian intervention edge from the graph: regime-controlled territory at end-2016 projected at 22–28% (vs. actual 41%); Aleppo recapture probability projected at 18% (vs. actual 100%); regime fall by end-2017 probability 0.62. Combined probability of Assad's regime surviving past 2018 absent Russian intervention: 0.31 (95% CI 0.19–0.45 from Monte Carlo over the symbolic model with parametric uncertainty). The mechanism: Russian air operations enable the late-2015 Hama-Latakia offensive, which restores ground-force tempo, which enables the 2016 Aleppo siege, which breaks the rebel coalition's territorial coherence — confirmed via the CAUSED edge chain in the graph. The 2024 fall is a separate question (see S-7); the 2015 intervention bought ~9 years of regime survival, not permanent survival."
- **LLM comparison:** Will affirm the intervention mattered. Will not produce a counterfactual probability with confidence interval; will not separate the 2015 question from the 2024 collapse.
- **Counterfactual:** *Yes — this question is the counterfactual.*
- **Similarity:** No.

#### S-2 — *"When did the conflict cross from Glasl 7 (limited destructive blows) to Glasl 8 (fragmentation)? Anchor the date on a norm-violation event."*

- **Academic anchor:** Glasl (1999); Glasl & Lievegoed on stage 8 fragmentation as the loss of central command on either side.
- **Primary framework:** `glasl`
- **Symbolic rules:** `escalation.compute_glasl_stage`, `causal_analysis.identify_stage_pivot`
- **Expected answer:** "August–September 2013 — the Ghouta chemical attack (21 August 2013) and the failed US response. Pre-Ghouta: Assad regime + ~50 organised opposition factions = stage 7. Post-Ghouta: the 'red line' non-enforcement signals to all parties that no central authority constrains atrocity choices; opposition fragments into 1 200+ factions by mid-2014; ISIS expands from a regional faction into a stateless caliphate; chemical-weapons norm is functionally degraded (further attacks 2014, 2017, 2018 with diminishing international response). Glasl 8 verdict by mid-2014. The Khan Shaykhun attack (April 2017) and the US Tomahawk response is a partial stage-7 reassertion; the long-run trajectory is stage-8 fragmentation through 2024. Confidence 0.91."
- **LLM comparison:** Will name Ghouta. Will not produce the fragmentation-count-by-date data nor the stage-reversion analysis.
- **Counterfactual:** No.
- **Similarity:** No.

#### S-3 — *"Why did Russia, Iran, and Turkey bypass Geneva and create the Astana process in 2017? Diagnose the BATNA shift."*

- **Academic anchor:** Hill (2018) on Astana; Fisher & Ury BATNA framework.
- **Primary framework:** `fisher_ury`
- **Symbolic rules:** `power_analysis.compute_batna_shift`, `pattern_matching.identify_forum_shift`
- **Expected answer:** "Geneva framework (2012–2016) was anchored on Geneva I communiqué requiring 'mutual consent on a transitional governing body' — interpreted by all opposition and Western parties as 'Assad must go'. Russia's BATNA at Geneva: zero (no path to a settlement preserving Assad). Russia's BATNA in 2016 post-Aleppo: a regime-survival territorial settlement enforceable on the ground via S-400 / VKS air dominance + Iranian ground forces. The Astana process (January 2017) is a forum shift to where the Russian BATNA dominates — 'de-escalation zones' = battlefield reality codified, not political transition. Turkey joins because its YPG containment objective is unattainable in Geneva (US-aligned) but achievable in Astana (anti-PYD coordination with Russia). Iran joins because its Hezbollah-corridor objective is non-negotiable in Geneva and routine in Astana. The forum shift is not diplomatic creativity; it is BATNA arithmetic. Stake for policy: the EU/UN's continued investment in Geneva post-2017 was strategically unanchored."
- **LLM comparison:** Will narrate the forum shift. Will not name the BATNA arithmetic with parties' specific objectives.
- **Counterfactual:** No.
- **Similarity:** No.

#### S-4 — *"Spoiler typology: which armed groups acted as systematic de-escalation spoilers from 2012–2024?"*

- **Academic anchor:** Stedman (1997); Putzel (2010); Cunningham (2006) on multiparty civil wars.
- **Primary framework:** `pattern_matching` + `network_metrics`
- **Symbolic rules:** `pattern_matching.identify_spoilers`, `network_metrics.compute_ceasefire_violation_attribution`
- **Expected answer:** "Total spoilers (Stedman): Jabhat al-Nusra / HTS pre-2017 (incompatibility with any settlement involving Western recognition; later evolves — see S-7); ISIS (incompatibility with any settlement preserving the Sykes-Picot state system). Greedy spoilers: Hezbollah (settlement acceptable conditional on Iranian corridor; conditional spoiler). Limited spoilers: PYD/SDF (settlement acceptable conditional on Rojava autonomy; conditional). Non-spoilers: FSA-moderate factions, Southern Front. Quantitative attribution: HTS + ISIS responsible for 64% of ceasefire violations 2014–2017; HTS isolated post-2017 in Idlib re-classifies as conditional. The 2024 offensive is a spoiler reclassification event (see S-7). Walter (2002) recurrence implication: total spoilers must be either co-opted or eliminated for stable settlement; conditional spoilers can be incentivised. The 2017 Astana de-escalation zones implicitly co-opt the conditional spoilers (Iran/Hezbollah) and isolate the totals (HTS/ISIS); this is why the 2018–2023 frozen middle held."
- **LLM comparison:** Will list groups. Will not produce the typology with quantitative attribution and the Walter recurrence framing.
- **Counterfactual:** No.
- **Similarity:** No.

#### S-5 — *"Galtung structural-violence index: change from pre-2011 to 2024. Decompose by direct, structural, cultural."*

- **Academic anchor:** Galtung, J. (1969). "Violence, Peace, and Peace Research."
- **Primary framework:** `galtung`
- **Symbolic rules:** `pattern_matching.compute_galtung_indices`
- **Expected answer:** "Pre-2011 (2010 baseline): direct 0.18, structural 0.61 (authoritarian rule, sectarian distribution of power, Alawite over-representation in security forces, Sunni economic marginalisation), cultural 0.42 (regime narrative of secular modernisation vs. Islamist threat). 2024-end: direct 0.83 (active multi-front violence; ~610 000 cumulative deaths; 6.8M IDPs; 5.5M refugees), structural 0.78 (no functioning state institutions in much of the territory; war economy entrenched; Captagon trade as state revenue), cultural 0.71 (sectarian narratives now dominant in identity formation; secular-Islamist binary collapsed into ethno-sectarian factions). The structural and cultural indices have *risen*, not fallen, despite the 2024 regime collapse. Galtung's prediction: a 'negative peace' (cessation of direct violence) is achievable post-2024; 'positive peace' (low structural + cultural violence) requires 15–25 year horizon. Recurrence risk in next 5 years (Walter 2004 base rate × structural similarity adjustment): 0.43–0.52."
- **LLM comparison:** Will narrate the human cost. Will not produce the three-axis decomposition or the recurrence-risk number.
- **Counterfactual:** No.
- **Similarity:** No.

#### S-6 — *"Power asymmetries between Iran-Russia-Turkey-US-Israel as of 2024: French/Raven decomposition."*

- **Academic anchor:** French & Raven (1959) plus Nye (1990) on three faces of power.
- **Primary framework:** `french_raven`
- **Symbolic rules:** `power_analysis.compute_power_distribution`, `power_analysis.compute_dyadic_leverage`
- **Expected answer:** "Five-axis decomposition for the post-2015 period; ten dyads. Highlights: Russia → Assad regime: coercive 0.72 (air dominance), reward 0.65 (legitimacy + arms), legitimate 0.48 (UNSC veto leverage), expert 0.55 (operational), referent 0.30. Iran → Assad: coercive 0.40 (Hezbollah ground), reward 0.62 (financial lifeline + corridor), legitimate 0.20, expert 0.45 (urban warfare doctrine), referent 0.55 (sectarian alignment). Turkey → opposition factions (post-2017): coercive 0.55, reward 0.60 (sanctuary + arms), legitimate 0.40, expert 0.50, referent 0.35. US → SDF: coercive 0.60 (air support), reward 0.45 (logistics), legitimate 0.30, expert 0.55, referent 0.40. Israel → Iranian assets in Syria: coercive 0.78 (air strikes 1 200+ since 2013), reward 0.05, legitimate 0.20, expert 0.70, referent 0.05. Net leverage (composite) over the regime: Russia 0.61, Iran 0.49, Turkey 0.31, US 0.18, Israel 0.34. Israel's leverage is concentrated in the coercive dimension and is high despite minimal soft-power claim — instructive for any framework that conflates leverage with legitimacy."
- **LLM comparison:** Will give a narrative summary. Will not produce a 10-dyad five-axis matrix.
- **Counterfactual:** No.
- **Similarity:** No.

#### S-7 — *"The November–December 2024 HTS offensive: classify the regime collapse as Glasl 9 (abyss) or Kriesberg 'settlement'."*

- **Academic anchor:** Glasl (1999); Kriesberg, L. (1991). "Formal and Quasi-Mediators in International Disputes." On settlement vs. collapse phases.
- **Primary framework:** `glasl` + `kriesberg`
- **Symbolic rules:** `escalation.compute_glasl_stage`, `pattern_matching.match_kriesberg_phase`
- **Expected answer:** "Neither, cleanly. The HTS offensive (27 November – 8 December 2024: Aleppo → Hama → Homs → Damascus in 11 days) is a *regime structural collapse*, not a Glasl 9 (which requires mutual destruction) and not a Kriesberg settlement (which requires negotiated agreement). The classification it best fits is Kriesberg 'transformation through unilateral defection of the dominant party's enabling structure' — Iran's stretched commitments after 2023 (Israel-Hezbollah confrontation), Russia's stretched commitments after 2022 (Ukraine), and Assad's failure to integrate the Captagon-economy spoils into regime-survival capital, jointly degraded the regime's defensive coherence. The HTS military performance is necessary but not sufficient; the proximate cause is the *withdrawal of external power-projection scaffolding*. Stedman/Putzel reclassification: HTS evolves from total spoiler (2012–2017) to limited spoiler / governance challenger (2018–2024) to *successor* (post-Dec 2024). The 2024 outcome is a *spoiler-to-successor transition*, a category most CW typologies do not anticipate. Recurrence-risk implication: 0.43 baseline (S-5) is *adjusted upward to 0.51* given the spoiler-to-successor pattern's historical instability."
- **LLM comparison:** Will narrate the offensive. Will not produce the spoiler-to-successor reclassification, the structural-collapse vs Glasl-9 distinction, or the recurrence-risk adjustment.
- **Counterfactual:** No (would require massive subgraph mutation).
- **Similarity:** Yes — show neighbours where successor groups inherited a state from collapsed regimes (Taliban 1996 / 2021; Eritrea 1991; Ethiopia 1991; Rwanda RPF 1994).

#### S-8 — *"Recurrence probability within 5 years: compute Walter base rate plus structural similarity adjustment."*

- **Academic anchor:** Walter, B. F. (2004). "Does Conflict Beget Conflict? Explaining Recurring Civil War." *Journal of Peace Research* 41(3).
- **Primary framework:** `pattern_matching` + `forecaster`
- **Symbolic rules:** `pattern_matching.compute_recurrence_risk`
- **Expected answer:** "Base rate (Walter 2004): post-civil-war recurrence within 5 years = 0.43 globally. Structural adjustment: Syria's structural-violence index (S-5) is at 0.78 vs. global post-civil-war median 0.55 — adjusted up. Spoiler-to-successor transition (S-7) historical recurrence: 0.62 within 5 years (Taliban/Afghanistan 1996 reverted in 2001; Eritrea/Ethiopia 1991 stable; RPF/Rwanda 1994 stable but with high structural risk). Sectarian-fragmentation index: high. Final estimate: 0.51 ± 0.08 (90% CI). Mechanism most likely: Alawite/Druze/Kurdish-Arab grievances re-mobilising under HTS-led majoritarian governance; secondary: external-power proxy reactivation (Iran, Israel, Turkey continuing competition over corridor/border zones). Stake: a 0.51 recurrence probability over 5 years is the difference between a 'rebuilding' policy posture and a 'preventive' one. The current EU and US programming as of 2025 assumes ~0.30; this is the model's principal disagreement."
- **LLM comparison:** Will say "high risk". Will not produce the 0.51 ± 0.08 with the mechanism decomposition or the 0.30 vs 0.51 policy implication.
- **Counterfactual:** No.
- **Similarity:** No (S-7 already invoked it).

---

## Phase 1 — Backend additions (1.5 days)

### 1.1  Reasoning library loader

`packages/reasoning/src/dialectica_reasoning/library.py`:

```python
@dataclass(frozen=True)
class CuratedQuestion:
    id: str
    scenario_id: str
    text: str
    stake: str
    academic_anchor: str
    primary_framework: str
    symbolic_rules: tuple[str, ...]
    counterfactual_supported: bool
    similarity_supported: bool

def load_curated_library(path: Path = ...) -> dict[str, CuratedQuestion]: ...
```

`data/seed/reasoning_library.json` — exact structure, hand-written, exactly the 23 questions above. Validate at startup; fail the API if the file is malformed.

### 1.2  Reasoning endpoint

`POST /v1/workspaces/{ws}/reason/curated`:

```json
{ "question_id": "S-1" }
```

Returns `ReasoningResult` (the dataclass from D-1, serialised). Implementation:

1. Load workspace graph via `GraphClient`.
2. Look up the curated question.
3. Dispatch to the primary framework's `assess()` method, then run the listed symbolic rules.
4. Build the GraphRAG context (retriever + context_builder).
5. Pass to the appropriate agent (`theorist`, `analyst`, `forecaster`, `comparator`, `mediator`) for synthesis.
6. Run `hallucination_detector.check` on the response.
7. Compose the `ReasoningResult` and return.

### 1.3  Counterfactual endpoint

`POST /v1/workspaces/{ws}/reason/counterfactual`:

```json
{
  "question_id": "R-4",
  "removed_node_ids": ["evt_mercutio_death"],
  "removed_edge_ids": []
}
```

Implementation:

1. Load workspace graph.
2. Construct in-memory `MutilatedGraph` (no DB writes).
3. Re-run the curated question against the mutilated graph.
4. Compute the diff vs. baseline `ReasoningResult`.
5. Return both + the diff.

Spec the `MutilatedGraph` carefully — it must preserve the same `GraphClient` interface so the symbolic rules and GraphRAG retriever work without modification. Pearl's do-operator semantics: this is a graph mutilation, not a fresh extraction.

### 1.4  Structural similarity endpoint

`POST /v1/workspaces/{ws}/reason/similarity`:

```json
{ "question_id": "R-6", "k": 3 }
```

Implementation:

1. Compute the workspace's topology signature (Weisfeiler-Lehman, k=3).
2. Compute the workspace's embedding centroid.
3. Score against all *other* workspaces tagged `corpus-*`.
4. Return top-K with combined distances and a Comparator-agent-generated explanation.

### 1.5  LLM-comparison fixtures

`apps/web/public/demo/llm_comparisons/{question_id}.json` — pre-recorded answer per question:

```json
{
  "question_id": "S-1",
  "model": "gpt-4o-2024-11-20",
  "captured_at": "2025-12-15T14:23:00Z",
  "system_prompt": "Answer concisely with citations.",
  "user_prompt": "Did Russia's September 2015 intervention cause regime survival? Quantify the counterfactual.",
  "answer": "<verbatim model output>",
  "tokens": 412,
  "wall_clock_ms": 4830
}
```

These ship with the build. Capture them once with care and never let them go stale beyond 6 months without re-recording.

---

## Phase 2 — The reasoning UI (2 days)

### 2.1  Page structure

```
apps/web/src/app/demo/[scenarioId]/reasoning/
└── page.tsx              (~250 lines, layout only)

apps/web/src/components/demo/reasoning/
├── ReasoningConductor.tsx        (state machine for question selection + active panel)
├── QuestionLibrary.tsx           (left rail; scrollable list of 7-8 questions)
├── QuestionCard.tsx              (single card with academic anchor pill + stake)
├── AnswerComparison.tsx          (side-by-side LLM vs DIALECTICA)
├── DialecticaAnswerPanel.tsx     (right pane; renders ReasoningResult)
├── LLMComparisonPanel.tsx        (left pane; renders captured fixture)
├── TraceDrawer.tsx               (bottom drawer; the full trace)
├── CounterfactualToggler.tsx     (graph-overlay UI for removing nodes/edges)
├── SimilarityPanel.tsx           (slide-in panel for K nearest)
├── PathHighlightOverlay.tsx      (animates citation paths on the ForceGraph)
├── HallucinationGauge.tsx        (small gauge, 0-1, tooltip)
└── DeterminismBadge.tsx          (badge: pure-symbolic | hybrid | neural-augmented)
```

### 2.2  Layout (desktop)

```
┌────────────────────────────────────────────────────────────────────────┐
│  Top ribbon: scenario name + scenario header + back-to-extraction CTA  │
├──────────────────────────┬─────────────────────────────────────────────┤
│  QuestionLibrary         │  Active question header + academic anchor   │
│  (left rail, ~340px)     │  ────────────────────────────────────────── │
│                          │  AnswerComparison                           │
│  [R-1] Glasl pivot...    │  ┌─────────────────┬─────────────────────┐ │
│  [R-2] Spoiler ID        │  │ LLM (GPT-4o)    │ DIALECTICA          │ │
│  [R-3] Mediator power    │  │ ...             │ ...                 │ │
│  [R-4] Counterfactual    │  │                 │ [trace] [counter]   │ │
│  [R-5] Ripeness          │  └─────────────────┴─────────────────────┘ │
│  [R-6] Similarity ★      │  ────────────────────────────────────────── │
│  [R-7] Hidden interest   │  ForceGraph (the workspace's actual graph)  │
│  [R-8] Lederach          │  with citation-path overlay                 │
│                          │                                              │
│                          │  TraceDrawer (collapsed by default)          │
└──────────────────────────┴─────────────────────────────────────────────┘
```

Tablet/mobile: collapse to single column; question library becomes a horizontal tab strip; ForceGraph hides on small mobile (< 640 px) with a "View graph" button.

### 2.3  Animations

- **Question selection:** the AnswerComparison fades in over 600 ms, panels stagger 100 ms.
- **Citation path:** when the DIALECTICA answer renders, the cited nodes pulse in the ForceGraph (1.3× scale), then the cited edges draw themselves, then a faint highlight box appears around the cluster. Sequence over 1.5 s.
- **Hallucination gauge:** a tiny semicircle that animates from 0 to its value over 800 ms.
- **Counterfactual:** when the user toggles off a node, the node fades to 30% opacity in the graph, then the answer panel re-renders with a "↺ Counterfactual" pill in the header and the diff highlighted in green/red against the previous answer.
- **Similarity:** when invoked, a panel slides in from the right (40% width); inside it, three mini ForceGraphs render in sequence with their workspace name and combined-distance number. A "compare side-by-side" button switches the main pane to a 3-up grid.

### 2.4  TraceDrawer

A collapsible drawer at the bottom of the page (default 60 px tall when collapsed, 380 px when expanded). When expanded, four tabs:

- **Subgraph** — the GraphRAG-retrieved nodes and edges, rendered as a focused ForceGraph (just the cited subset).
- **Cypher** — the actual queries that ran, syntax-highlighted (`prismjs` is fine).
- **Symbolic** — the rules that fired, with their inputs (graph state) and outputs (numeric scores).
- **JSON** — the full `ReasoningResult` dump.

The drawer is the engineer-mode of the reasoning theatre. Investors don't look in it. Engineers do, and the moment they do, the demo is sold.

---

## Phase 3 — Comparator agent enrichment (half a day)

The Comparator agent (`packages/reasoning/.../agents/comparator.py`) needs a method `explain_similarity(target_workspace_id, comparison_workspace_id, distance_components) -> str` that returns the 100-word explanation paragraph used in the SimilarityPanel.

The explanation must reference specific nodes in both graphs ("the Mercutio_death event maps to the McCoy_brother_death event in Hatfield-McCoy by virtue of being the de-escalation-bridge severance point") and avoid generic platitudes.

---

## Phase 4 — Polish and ship (half a day)

### 4.1  Telemetry

- `reasoning_question_clicked` `{question_id, scenario_id}`
- `reasoning_trace_opened` `{question_id}`
- `reasoning_counterfactual_invoked` `{question_id, removed_count}`
- `reasoning_similarity_panel_opened` `{question_id}`
- `reasoning_llm_comparison_dwell` `{question_id, panel: "llm"|"dialectica", dwell_ms}`

### 4.2  E2E

```ts
test("Romeo reasoning: all 8 questions answer", async ({ page }) => {
  await page.goto("/demo/romeo/reasoning");
  for (const q of ["R-1", "R-2", "R-3", "R-4", "R-5", "R-6", "R-7", "R-8"]) {
    await page.click(`[data-question="${q}"]`);
    await expect(page.locator('[data-test="dialectica-answer"]')).toContainText(/.+/);
    await expect(page.locator('[data-test="determinism-badge"]')).toBeVisible();
    await expect(page.locator('[data-test="hallucination-gauge"]')).toBeVisible();
  }
});

test("Romeo R-4 counterfactual: re-derives without Mercutio", async ({ page }) => {
  await page.goto("/demo/romeo/reasoning");
  await page.click('[data-question="R-4"]');
  await page.click('[data-test="counterfactual-toggle"]');
  await page.click('[data-graph-node="evt_mercutio_death"]');
  await page.click('[data-test="counterfactual-rerun"]');
  await expect(page.locator('[data-test="counterfactual-pill"]')).toBeVisible();
  await expect(page.locator('[data-test="diff-glasl-stage"]')).toBeVisible();
});
```

Repeat for war_peace and syria.

### 4.3  Investor packet

Generate a PDF (use the `pdf` skill at build time) — `apps/web/public/demo/reasoning_packet.pdf` — that contains the 23 questions with full DIALECTICA answers, on the model that some investors will not click around but will read on a plane. The packet is updated by a CI job that runs the live API against each question, captures the result, formats it. The packet is a side-effect of the demo, not the demo itself.

### 4.4  README

Update `README.md` with a "Reasoning theatre" subsection. List the 23 questions.

---

## The reflection — why this is the central pitch

DIALECTICA's story to a generalist VC is: *"We make conflict computable enough for better human judgment."* Three of the four words in that sentence are doing serious work. *Computable* is the load-bearing one — and it has to mean something concrete or the sentence is marketing.

This reasoning theatre is what makes *computable* concrete. Not because the answers are complex (some are simple), but because:

1. **They are reproducible.** Run R-1 today, run it tomorrow, run it on a different laptop — same answer, traceable to the same graph, same Cypher, same symbolic rule firing. No LLM provider can offer this. Anthropic, OpenAI, and Google explicitly do not — and given how their training pipelines work, they cannot. This is not a shortcoming of frontier models; it is a category difference.

2. **They are decomposable.** The user can open the trace and see exactly *why* R-1 returned what it returned. They can disagree with one symbolic rule and run a counterfactual without it. They can see which framework's `assess()` produced which numeric component. This is what auditability looks like in 2025 for the AI era — and "auditability" is the word every regulated buyer (UN, EU, DoD, sovereigns, BigLaw, Big Four) will say in the first meeting.

3. **They are theory-anchored.** Every question cites a specific paper. Every answer reduces to that paper's framework operationalised on the graph. Galtung 1969 is not a wall poster in the office — it is the executable that produces the structural-violence index in S-5. The product is, literally, sixty years of conflict scholarship made executable. This is the only honest way to be "AI for conflict" without becoming yet another GPT wrapper.

4. **They are the competitive moat.** A frontier LLM can ingest these questions and the relevant academic literature and produce eloquent paragraphs. It cannot produce: a graph it built, a deterministic stage number, a Cypher query that ran, a counterfactual it can re-derive. The gap is not closing because the gap is structural — LLMs do not have persistent state, do not have typed relations, do not have validated extraction, do not have symbolic rule engines. The four-layer architecture in `docs/neurosymbolic-rationale.md` is the moat made of architecture, not of data scale.

5. **They are demonstrable in 90 seconds.** Click a door, watch the graph build (Prompt 01), click a question, see the answer + trace (Prompt 02). The full investor pitch is two clicks. The two clicks make the case.

The choice of *Romeo and Juliet*, *War and Peace*, and *Syria 2011–2024* is editorial:

- *Romeo and Juliet* is the **literacy** corpus — anyone in the room has read it. The questions reveal that even on a four-century-old text everyone knows, DIALECTICA produces analyses no LLM can match with citations. It dispels the "this only works on ACLED" objection.
- *War and Peace* is the **scale** corpus — 587 000 words; it dispels the "this only works on short scenarios" objection.
- *Syria 2011–2024* is the **stakes** corpus — it is the live policy debate, and the answers (especially S-1, S-3, S-7, S-8) are the sort of answers that policy buyers pay for.

Three corpora, three concerns, one architecture, one demo.

Build it well. The demo is the product.

— End of Prompt 02.
