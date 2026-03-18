# Neurosymbolic Rationale — DIALECTICA by TACITUS

## Table of Contents

1. [Why Neurosymbolic?](#1-why-neurosymbolic)
2. [The DIALECTICA Architecture](#2-the-dialectica-architecture)
3. [Neural Components](#3-neural-components)
4. [Symbolic Components](#4-symbolic-components)
5. [The Bridge Protocol](#5-the-bridge-protocol)
6. [Hallucination Detection and Mitigation](#6-hallucination-detection-and-mitigation)
7. [Theory-Grounded Reasoning](#7-theory-grounded-reasoning)
8. [Advantages over Pure LLM Approaches](#8-advantages-over-pure-llm-approaches)
9. [Future Research Directions](#9-future-research-directions)

---

## 1. Why Neurosymbolic?

Conflict analysis occupies a unique position at the intersection of unstructured
human communication and rigorous analytical reasoning. Neither pure neural
approaches nor pure symbolic approaches are sufficient on their own.

### Limitations of Pure Neural Approaches

Large language models excel at parsing unstructured text, identifying sentiment,
and generating fluent summaries. However, when applied to conflict analysis in
isolation they exhibit critical shortcomings:

- **Hallucination under ambiguity.** Conflict domains are inherently ambiguous.
  Actors make contradictory claims, timelines are disputed, and the same event
  may be described in radically different ways by different parties. LLMs faced
  with this ambiguity tend to confabulate plausible-sounding but fabricated
  details — a failure mode that is catastrophic when the output feeds into
  mediation strategy or policy recommendations.

- **No relational memory.** LLMs process text as flat sequences. They cannot
  natively maintain a persistent, structured representation of who said what to
  whom, which commitments remain active, or how escalation trajectories have
  evolved over time. Each query starts from scratch unless an external knowledge
  structure is provided.

- **Opaque reasoning.** When an LLM concludes that a conflict has reached Glasl
  stage 7 or that a trust breach has occurred, there is no inspectable chain of
  inference — only a probability distribution over tokens. In high-stakes
  domains such as peace processes, legal disputes, or organizational crises,
  stakeholders require auditable reasoning traces.

- **No constraint enforcement.** LLMs cannot guarantee that their outputs
  respect domain constraints such as UCDP fatality thresholds for conflict
  classification, Allen's interval algebra for temporal consistency, or the
  structural rules of a conflict ontology.

### Limitations of Pure Symbolic Approaches

Symbolic systems — ontologies, rule engines, graph databases — provide
structure, auditability, and constraint enforcement. But they falter on the
input side of the problem:

- **Brittleness with unstructured text.** Symbolic systems require structured
  input. They cannot directly consume messy, contradictory, multilingual natural
  language documents — the primary data source for conflict analysis.

- **No semantic generalization.** A rule engine can detect that Actor A violated
  Norm N because an explicit `VIOLATES` edge exists in the graph. It cannot
  detect that two narratives are semantically similar, that an event description
  implies an escalation even without an explicit causal link, or that a new
  conflict case structurally resembles a historical precedent.

- **Combinatorial explosion.** As the number of actors, events, and
  relationships grows, purely rule-based inference becomes computationally
  expensive and increasingly difficult to maintain.

- **No tolerance for ambiguity.** Real conflict data is noisy, incomplete, and
  contested. A pure symbolic system either accepts a fact or rejects it; it
  cannot gracefully handle the confidence gradients that characterize
  real-world intelligence.

### The Neurosymbolic Synthesis

DIALECTICA resolves these tensions by combining both paradigms in a principled
four-layer architecture. Neural models handle what they do best — parsing
unstructured text, generating embeddings, detecting semantic similarity, and
predicting patterns from learned representations. Symbolic structures handle
what they do best — maintaining typed relationships, enforcing domain
constraints, providing auditable inference chains, and preserving temporal
consistency. The key architectural invariant is that **deterministic symbolic
conclusions are never overridden by probabilistic neural inference**. This is
the inviolable principle that makes the system trustworthy in high-stakes
conflict domains.

---

## 2. The DIALECTICA Architecture

DIALECTICA implements a four-layer neurosymbolic pipeline, defined as the
`NeurosymbolicArchitecture` Pydantic model in
`packages/ontology/src/dialectica_ontology/neurosymbolic.py`.

```
Document Upload
     |
     v
┌─────────────────────────────────────────────────┐
│  Layer 1: Neural Ingestion                      │
│  GLiNER pre-filter + Gemini Flash extraction    │
│  + Pydantic v2 schema validation                │
└─────────────────────┬───────────────────────────┘
                      |
                      v
┌─────────────────────────────────────────────────┐
│  Layer 2: Symbolic Representation               │
│  Conflict Grammar ontology (15 nodes, 20 edges, │
│  39 enums) stored in Spanner Graph / Neo4j      │
└─────────────────────┬───────────────────────────┘
                      |
                      v
┌─────────────────────────────────────────────────┐
│  Layer 3: Reasoning and Inference               │
│  9 symbolic rule modules fire first             │
│  7 neural components fill gaps second           │
│  Bridge protocol enforces ordering              │
└─────────────────────┬───────────────────────────┘
                      |
                      v
┌─────────────────────────────────────────────────┐
│  Layer 4: Decision Support                      │
│  6 AI agents + hallucination detection          │
│  + SSE streaming + human-in-the-loop            │
└─────────────────────────────────────────────────┘
```

### Layer 1 — Neural Ingestion

Extract actors, claims, events, sentiments, commitments, threats, concessions,
timelines, and uncertainty from messy text using the ontology as an extraction
schema. Each extraction carries a confidence score.

- **GLiNER** (medium v2.5, ~500 MB local model) pre-filters document chunks by
  entity density, prioritizing entity-rich passages for downstream extraction.
- **Gemini 2.5 Flash** performs tier-appropriate structured extraction against
  the Conflict Grammar schema.
- **Pydantic v2** validates every extracted node against `ConflictNode`
  subclass models before it enters the graph.

The extraction pipeline is a 10-step LangGraph `StateGraph` with conditional
edges (validate-then-repair loops with up to 3 retries), defined in
`packages/extraction/src/dialectica_extraction/pipeline.py`.

### Layer 2 — Symbolic Representation

Encode extracted entities into the Conflict Grammar graph with typed relations,
controlled vocabularies, and temporal metadata.

- **15 node types** (Actor, Conflict, Event, Issue, Interest, Norm, Process,
  Outcome, Narrative, EmotionalState, TrustState, PowerDynamic, Location,
  Evidence, Role) each grounded in specific conflict theories.
- **20 edge types** (PARTY_TO, PARTICIPATES_IN, HAS_INTEREST, CAUSED,
  ALLIED_WITH, OPPOSED_TO, VIOLATES, RESOLVED_THROUGH, etc.) with typed
  source/target label constraints.
- **39 enums** covering actor types, conflict scales, event taxonomies, Glasl
  stages, Kriesberg phases, emotion intensities, trust bases, and more.
- **Three-tier progressive disclosure**: Essential (7 nodes / 6 edges),
  Standard (12 / 13), Full (15 / 20).
- **Dual-backend storage**: Google Cloud Spanner Graph (primary, GQL + native
  768-dim vector index) and Neo4j 5-community (secondary, Cypher + APOC).

### Layer 3 — Reasoning and Inference

Contradiction checks, commitment tracking, escalation detection, argument maps,
procedural rules, and causal hypotheses. The architectural invariant is that
deterministic symbolic rules fire first and their conclusions stand; neural
components fill gaps second.

- **9 symbolic modules** implemented in
  `packages/reasoning/src/dialectica_reasoning/symbolic/`:
  Glasl escalation rules, Ury/Brett/Goldberg loopback, trust breach detection,
  UCDP conflict classification, temporal logic (Allen's interval algebra), norm
  violation detection, BATNA/ZOPA computation, causal chain analysis, and
  cross-case structural similarity.
- **7 neural components** defined in the `NeuralLayer` model:
  R-GAT (relational graph attention), RotatE (link prediction), temporal
  attention, narrative similarity, conflict pattern matching, escalation
  prediction, and outcome prediction.
- **GraphRAG** hybrid retrieval: vector search for top-k semantically similar
  nodes followed by N-hop graph traversal from each seed, with temporal
  filtering and confidence thresholds.

### Layer 4 — Decision Support

Surface options, risks, missing evidence, and competing interpretations for
human decision-makers. TACITUS is decision-support, not autonomous resolution.

- **6 AI agents**: Analyst, Advisor, Comparator, Forecaster, Mediator,
  Theorist — each with a specialized role defined in
  `packages/reasoning/src/dialectica_reasoning/agents/`.
- **SSE streaming** via `stream_analyze()` for real-time reasoning traces.
- **Hallucination detection** on every LLM synthesis output.
- **Human-in-the-loop validation** promotes neural suggestions to new symbolic
  rules (the learning loop).

---

## 3. Neural Components

### LLM Extraction Pipeline

The extraction pipeline transforms unstructured conflict documents into
structured knowledge graph entities through 10 steps:

| Step | Module | Description |
|------|--------|-------------|
| 1 | `chunk_document` | Split text into 2,000-char overlapping chunks (sentence-boundary aware, 200-char overlap) |
| 2 | `gliner_prefilter` | GLiNER NER scores entity density per chunk |
| 3 | `extract_entities` | Gemini Flash extracts typed entities per ontology tier |
| 4 | `validate_schema` | Pydantic v2 validates against `ConflictNode` models |
| 5 | `repair_extraction` | Send validation errors back to Gemini (max 3 retries) |
| 6 | `extract_relationships` | Gemini extracts typed edges between validated nodes |
| 7 | `resolve_coreference` | Cross-chunk entity merging + alias matching |
| 8 | `validate_structural` | Conflict Grammar structural rules + temporal + symbolic validation |
| 9 | `compute_embeddings` | Vertex AI `text-embedding-005` (768-dim) |
| 10 | `write_to_graph` | Batch upsert nodes and edges to graph database |

The pipeline uses a conditional routing pattern: after schema validation, chunks
with invalid entities are routed to a repair step that sends validation errors
back to Gemini for correction, looping until entities validate or 3 retries are
exhausted. This validate-then-repair loop is critical for maintaining ontology
compliance without discarding partially valid extractions.

### Embedding Generation

Two embedding regimes operate in DIALECTICA:

- **Semantic embeddings** (768-dim): Generated by Vertex AI `text-embedding-005`
  during extraction step 9. These power vector search in GraphRAG retrieval and
  are stored natively in Spanner Graph's COSINE_DISTANCE vector index.
- **Structural embeddings** (128-dim recommended): Generated by GNN models
  (R-GAT, RotatE) that encode graph topology. These capture relational patterns
  invisible to text-based embeddings — such as structural similarity between
  conflicts with analogous actor-issue-event topologies.

Node types that receive learned embeddings: Actor, Conflict, Event, and
Narrative.

### GraphRAG Retrieval

The `ConflictGraphRAGRetriever`
(`packages/reasoning/src/dialectica_reasoning/graphrag/retriever.py`) implements
hybrid retrieval:

1. **Embed query** via the configured embedding function.
2. **Vector search** for top-k semantically similar nodes (cosine distance,
   configurable confidence threshold of 0.3).
3. **Graph expansion**: traverse N hops (default 2) from each seed node to
   capture relational context.
4. **Temporal filtering** (optional): restrict results to a date range.
5. **Rank** by combined relevance score and confidence.

The `ConflictContextBuilder`
(`packages/reasoning/src/dialectica_reasoning/graphrag/context_builder.py`)
then assembles retrieved subgraphs into structured context for LLM synthesis.
This is not naive RAG — the graph traversal step ensures that the LLM sees
connected relational context, not isolated text fragments.

---

## 4. Symbolic Components

### Ontology Constraints

The TACITUS Core Ontology v2.0 (the "Conflict Grammar") enforces structural
integrity through multiple validation layers:

1. **Schema validation** — Every extracted node must parse as a valid
   `ConflictNode` Pydantic v2 subclass with all required fields, correct enum
   values, and valid confidence scores (`validators/schema.py`).
2. **Structural validation** — Edges must connect valid source/target label
   pairs. Required relationships must exist. No orphan nodes in controlled
   contexts (`validators/structural.py`).
3. **Temporal validation** — Allen's interval algebra on `valid_from` /
   `valid_to` fields ensures temporal consistency. Events cannot cause effects
   that precede them; commitments cannot expire before they are made
   (`validators/temporal.py`).
4. **Symbolic validation** — Domain-specific rule checks enforce
   theory-grounded constraints: Glasl stage consistency (no skipping stages),
   UCDP fatality thresholds, emotion intensity bounds
   (`validators/symbolic.py`).

### The 9 Symbolic Rule Modules

Implemented in `packages/reasoning/src/dialectica_reasoning/symbolic/`:

| Module | File | What It Does |
|--------|------|-------------|
| **Glasl escalation rules** | `escalation.py` | Detects stage transitions using Glasl's 9-stage model; recommends tier-appropriate interventions (moderation for stages 1-3, process consulting for 4-6, power intervention for 7-9) |
| **Ury/Brett/Goldberg loopback** | `constraint_engine.py` | When a power contest fails, deterministically recommends return to interest-based bargaining |
| **Trust breach detection** | `trust_analysis.py` | Fires when integrity dimension drops > 0.3 in the Mayer/Davis/Schoorman trust model; triggers alert and surfaces evidence |
| **UCDP conflict classification** | `constraint_engine.py` | Applies the 25-battle-death threshold; classifies incompatibility as territory vs. government |
| **Temporal logic** | `constraint_engine.py` | Allen's interval algebra on temporal fields; detects before/after/overlaps/contains relationships |
| **Norm violation detection** | `constraint_engine.py` | Traverses Event -[VIOLATES]-> Norm chains in the conflict graph |
| **BATNA/ZOPA computation** | `constraint_engine.py` | Computes Zone of Possible Agreement from party reservation values and alternatives |
| **Causal chain analysis** | `causal_analysis.py` | Traverses Event -[CAUSED]-> Event paths for escalation pattern detection and root cause identification |
| **Cross-case structural similarity** | `pattern_matching.py` | Subgraph isomorphism for recognizing recurring conflict patterns across cases |

Additional symbolic capabilities include Zartman Mutually Hurting Stalemate /
Mutually Enticing Opportunity ripeness scoring (`ripeness.py`), French and Raven
power base mapping (`power_analysis.py`), network centrality and community
detection (`network_metrics.py`), and OWL-style inference for materializing
implicit edges (`inference.py`).

### Theory Frameworks

Each of the 16 theory modules in
`packages/ontology/src/dialectica_ontology/theory/` inherits from
`TheoryFramework(ABC)` and implements:

- `describe()` — Explain the theory and its concepts.
- `assess(snapshot: ConflictSnapshot)` — Apply the theory to a workspace
  summary, producing findings, confidence scores, and recommendations.
- `score()` — Compute a numerical assessment metric.

Each `TheoryConcept` is explicitly linked to the ontology via
`related_node_types` and `related_edge_types`, creating a formal mapping between
academic theory and graph structure.

---

## 5. The Bridge Protocol

The Bridge Protocol defines how symbolic and neural components interact. It is
formalized as the `BridgeProtocol` Pydantic model in `neurosymbolic.py` and
implements the **reason-then-embed** pattern:

### The Four-Step Pattern

```
Step 1: Symbolic rules fire first
        (deterministic, explainable, auditable)
            |
            v
Step 2: Neural layer fills gaps
        (predictions, similarities, anomalies)
            |
            v
Step 3: Human-in-the-loop validates neural suggestions
        (domain experts review probabilistic outputs)
            |
            v
Step 4: Validated suggestions become new symbolic rules
        (learning loop: neural insight hardens into deterministic rule)
```

### The Inviolable Principle

> Deterministic conclusions are NEVER overridden by probabilistic inference.
> The symbolic layer provides the auditability and accountability required in
> high-stakes conflict domains.

This means that if the Glasl escalation rules deterministically classify a
conflict at stage 6, a neural model predicting stage 4 does not downgrade the
assessment. The neural prediction is surfaced as a competing interpretation for
human review, but it does not override the rule-based conclusion.

### Why This Order Matters

The reason-then-embed ordering serves several purposes:

1. **Explainability first.** Symbolic conclusions come with inspectable
   inference chains. Analysts can trace exactly which rules fired and why.
2. **Gap-filling, not overriding.** Neural components address questions that
   rules cannot answer — such as "which historical conflicts structurally
   resemble this one?" or "what is the probability of de-escalation given this
   actor network?" These are genuinely probabilistic questions.
3. **Progressive trust building.** When human validators repeatedly confirm a
   neural suggestion, it can be promoted to a symbolic rule. This creates a
   principled path for the system to learn without sacrificing auditability.
4. **Liability clarity.** In domains where analytical conclusions have real
   consequences — mediation strategy, humanitarian intervention, legal
   proceedings — it must be clear whether a conclusion is deterministic (from
   rules) or probabilistic (from models).

### Scientific Risks

The `BridgeProtocol` model explicitly codifies three scientific risks and their
mitigations:

| Risk | Description | Mitigation |
|------|-------------|------------|
| **Ontology loss** | If the schema is too rigid, it flattens meaningful ambiguity. Real conflicts involve contested facts, fluid identities, and irreducible uncertainty. | Controlled vocabularies with escape hatches, confidence scores on every node and edge, and preserved `source_text` fields that retain the original language. |
| **Extraction error propagation** | LLM misreads can look authoritative once encoded as typed graph nodes. A hallucinated actor or fabricated causal link gains unwarranted credibility by virtue of being in the knowledge graph. | Confidence scores distinguish high-certainty from low-certainty extractions. HITL validation flags uncertain entities. A stated/inferred distinction separates what the source document explicitly says from what the system infers. |
| **Normative overreach** | The system may identify strategically efficient outcomes without understanding procedural fairness, political legitimacy, or cultural context. Optimization is not the same as justice. | TACITUS is designed as decision-support, not autonomous resolution. It surfaces options and risks; humans make decisions. The system never recommends a single "correct" outcome. |

---

## 6. Hallucination Detection and Mitigation

Every LLM synthesis output in DIALECTICA passes through the
`HallucinationDetector`
(`packages/reasoning/src/dialectica_reasoning/hallucination_detector.py`), which
implements a GraphEval-inspired claim verification pipeline.

### Detection Pipeline

```
LLM Response Text
       |
       v
1. Extract atomic claims as (subject, predicate, object) triples
       |
       v
2. Verify each triple against the workspace knowledge graph
       |
       v
3. Score each claim: SUPPORTED | UNSUPPORTED | CONTRADICTED
       |
       v
4. Compute overall hallucination rate
       |
       v
5. Flag responses exceeding the 30% threshold
```

### Claim Extraction

The detector extracts atomic claims using pattern matching:

- **Relational patterns**: "X attacked Y", "X allied with Y", "X opposed Z"
  yield (subject, predicate, object) triples.
- **Attributive patterns**: "X is Y", "X has Y" yield existence claims.
- **Fallback**: If no relational patterns match, capitalized entity names are
  extracted and checked for presence in the graph.

Claims are capped at 20 per response to bound verification cost.

### Graph Verification

Each claim is verified against the workspace knowledge graph:

1. **Subject lookup**: Does the claimed subject entity exist in the graph?
   (Fuzzy matching via substring containment on normalized names.)
2. **Object lookup**: Does the claimed object entity exist?
3. **Edge verification**: For relational claims, does an edge of the claimed
   type exist between the subject and object nodes?

Claims are scored as:
- **SUPPORTED** — Subject exists and (for relational claims) the relationship is
  present in the graph.
- **UNSUPPORTED** — Subject or object not found, or relationship not present.
- **CONTRADICTED** — Evidence in the graph directly contradicts the claim.

### Threshold and Flagging

The hallucination rate is computed as:

```
hallucination_rate = (unsupported + contradicted) / total_claims
```

Responses with a hallucination rate exceeding 30% (`_HALLUCINATION_THRESHOLD =
0.3`) are flagged. The `AnalysisResponse` dataclass includes a
`hallucination_risk` field that is populated for every query.

### Multi-Layer Mitigation Strategy

Hallucination mitigation in DIALECTICA is not a single checkpoint but a
multi-layer strategy:

1. **Grounded retrieval** — GraphRAG retrieves actual graph nodes and edges, not
   arbitrary text chunks. The LLM synthesizes from structured evidence.
2. **Citation enforcement** — Every `AnalysisResponse` includes a `citations`
   list with node IDs, names, types, and relevance scores. Claims must trace
   back to specific graph entities.
3. **Post-hoc verification** — The `HallucinationDetector` checks the generated
   response against the same graph that provided the evidence.
4. **Confidence propagation** — Low-confidence extractions are marked as such
   throughout the pipeline. The synthesis prompt can be instructed to caveat
   conclusions based on low-confidence inputs.
5. **Symbolic guardrails** — Deterministic symbolic conclusions serve as hard
   constraints. If the symbolic layer has already determined that two actors are
   OPPOSED_TO each other, the LLM cannot assert they are allied without the
   response being flagged.

---

## 7. Theory-Grounded Reasoning

DIALECTICA is grounded in 16 conflict theories implemented as formal modules in
`packages/ontology/src/dialectica_ontology/theory/`. Each theory is not merely
referenced — it is operationalized as executable code that maps to specific
ontology structures.

### The 16 Theory Frameworks

| Theory Module | Academic Basis | What It Operationalizes |
|---------------|---------------|------------------------|
| **Burton** | John Burton's Human Needs Theory | Distinguishes non-negotiable needs from negotiable interests |
| **Deutsch** | Morton Deutsch's Cooperation-Competition Theory | Classifies conflict dynamics as cooperative, competitive, or mixed-motive |
| **Fisher/Ury** | "Getting to Yes" — principled negotiation | Positions vs. interests analysis; BATNA computation; objective criteria identification |
| **French/Raven** | Five Bases of Power | Maps power relationships (coercive, reward, legitimate, expert, referent) between actors |
| **Galtung** | Johan Galtung's ABC Triangle | Attitude-Behavior-Contradiction decomposition of conflict structure |
| **Glasl** | Friedrich Glasl's 9-Stage Escalation Model | Stage classification, transition triggers, tier-appropriate intervention recommendations |
| **Kriesberg** | Louis Kriesberg's Conflict Phases | Phase identification (emergence, escalation, de-escalation, settlement, post-settlement) |
| **Lederach** | John Paul Lederach's Conflict Transformation | Multi-level peacebuilding: personal, relational, structural, cultural |
| **Mayer Trust** | Mayer/Davis/Schoorman Integrative Trust Model | Three-factor trust assessment (ability, benevolence, integrity) with breach detection |
| **Pearl Causal** | Judea Pearl's Causal Inference | Causal graph construction; do-calculus reasoning on intervention effects |
| **Plutchik** | Robert Plutchik's Wheel of Emotions | Emotion classification and intensity mapping for conflict actors |
| **Thomas-Kilmann** | Thomas-Kilmann Conflict Mode Instrument | Classifies conflict handling styles (competing, collaborating, compromising, avoiding, accommodating) |
| **Ury/Brett/Goldberg** | "Getting Disputes Resolved" | Dispute resolution system design: interests, rights, and power-based approaches with loop-back mechanisms |
| **Winslade/Monk** | Narrative Mediation | Narrative analysis, dominant story identification, alternative story construction |
| **Zartman** | I. William Zartman's Ripeness Theory | Mutually Hurting Stalemate and Mutually Enticing Opportunity assessment |
| **Base** | Abstract base class | Defines the `TheoryFramework` interface: `describe()`, `assess()`, `score()` |

### How Theories Map to the Ontology

Each theory framework defines `TheoryConcept` objects that declare explicit
mappings to ontology node and edge types:

- Glasl's escalation model maps to `Conflict` nodes (via `glasl_stage` and
  `glasl_level` enum fields), `Event` nodes (escalation triggers), and
  `CAUSED` edges (escalation chains).
- Fisher/Ury maps to `Interest` nodes (underlying interests), `Issue` nodes
  (positions), `Norm` nodes (objective criteria), and `HAS_INTEREST` edges.
- Mayer trust maps to `TrustState` nodes (with ability, benevolence, and
  integrity dimensions) and `TRUSTS` edges between actors.
- French/Raven maps to `PowerDynamic` nodes (with power base classification)
  and `HAS_POWER_OVER` edges.

This is not decorative — the mappings are used at runtime. When the Theorist
agent applies Glasl's framework to a workspace, it queries the graph for
`Conflict` nodes, reads their `glasl_stage` fields, traverses `CAUSED` chains,
and produces a `TheoryAssessment` with findings, confidence, and
`Intervention` recommendations that include `theory_basis` citations.

### Multi-Theory Analysis

The Theorist agent can apply multiple theories to the same conflict
simultaneously, producing competing interpretations. For example:

- Galtung's ABC triangle may diagnose the contradiction as structural.
- Glasl's model may classify escalation at stage 5 (loss of face).
- Zartman's ripeness theory may assess that a Mutually Hurting Stalemate has
  not yet been reached.
- Fisher/Ury may identify unexplored interest-based options.

These are presented as parallel lenses, not a single verdict. The decision-maker
chooses which theoretical frame is most relevant to their context.

---

## 8. Advantages over Pure LLM Approaches

DIALECTICA's neurosymbolic architecture provides concrete advantages over
systems that rely solely on LLMs with retrieval-augmented generation (RAG):

### Structural Persistence

Pure LLM/RAG systems retrieve text chunks and forget them after each query.
DIALECTICA maintains a persistent, typed knowledge graph where actors,
relationships, events, and causal chains accumulate over time. This enables
longitudinal analysis — tracking how a conflict evolves across months or years
of document ingestion.

### Constraint-Based Consistency

An LLM might describe the same actor as both "allied with" and "opposed to"
another actor in different responses. DIALECTICA's symbolic layer enforces
relational consistency through the Conflict Grammar. Contradictions are
detected, surfaced, and resolved (or preserved as contested claims with
evidence).

### Auditable Inference Chains

When DIALECTICA reports that a conflict is at Glasl stage 6, the user can trace
the reasoning: which events triggered the stage transition, which symbolic rule
fired, what evidence supports the classification. Pure LLM responses offer no
such trace.

### Theory-Grounded Analysis

Pure LLM approaches may reference conflict theories in their output, but they
do so from memorized training data — which may be outdated, incomplete, or
incorrectly recalled. DIALECTICA's theory modules are formalized, tested, and
version-controlled. When Glasl's model is applied, it is applied correctly
because the rules are code, not recalled text.

### Bounded Hallucination

The multi-layer hallucination detection pipeline (grounded retrieval, citation
enforcement, post-hoc verification, symbolic guardrails) provides quantifiable
hallucination rates. Pure LLM systems have no intrinsic mechanism to measure
how much of their output is fabricated.

### Multi-Tenancy and Access Control

The knowledge graph enforces tenant isolation at the data layer. Every node and
edge is scoped to a `tenant_id` and `workspace_id`. Pure LLM approaches
typically lack this kind of structural access control — all context is mixed in
the prompt window.

### Progressive Disclosure

The three-tier system (Essential, Standard, Full) allows the same conflict to be
analyzed at different levels of depth. Essential tier (7 nodes, 6 edges)
provides rapid situational awareness. Full tier (15 nodes, 20 edges) provides
complete neurosymbolic intelligence. This is impossible with unstructured LLM
outputs.

### Reproducibility

Given the same graph state and query, the symbolic reasoning modules produce
identical results. The deterministic components of the analysis are fully
reproducible. Pure LLM systems are inherently stochastic — the same prompt may
yield different conclusions.

---

## 9. Future Research Directions

### GNN Training on Conflict Graphs

The neural layer currently defines 7 components (R-GAT, RotatE, temporal
attention, narrative similarity, conflict pattern matching, escalation
prediction, outcome prediction) as architectural specifications. Training these
models on real conflict graph data is a primary research frontier. Key
challenges include:

- **Data scarcity.** Labeled conflict graph datasets are rare. Transfer
  learning from general knowledge graph embedding benchmarks
  (FB15k-237, WN18RR) to the Conflict Grammar domain requires careful
  adaptation.
- **Heterogeneous graph modeling.** The ontology's 15 node types and 20 edge
  types create a highly heterogeneous graph. Standard GNN architectures must be
  extended with type-aware message passing (hence R-GAT rather than vanilla
  GAT).
- **Temporal dynamics.** Conflict graphs are not static. Events, alliances, and
  escalation states change over time. Temporal GNN architectures (TGAT, TGN)
  that respect `valid_from` / `valid_to` semantics are needed.

### Causal Inference Integration

The Pearl causal theory module provides a foundation for causal reasoning, but
full integration of do-calculus into the reasoning engine remains an open
challenge. This would enable counterfactual analysis: "What would have happened
if intervention X had been applied at time T?"

### Multilingual Extraction

Current extraction uses English-centric LLMs. Extending the pipeline to
reliably extract entities from Arabic, French, Russian, Spanish, and Chinese
conflict documents — while maintaining ontology compliance — is essential for
global applicability.

### Adversarial Robustness

Conflict data may be deliberately manipulated by parties seeking to influence
analysis. Research into adversarial robustness — detecting planted narratives,
fabricated evidence, and coordinated information campaigns — is critical for
deployment in active conflict zones.

### Federated Learning Across Workspaces

The current architecture isolates workspaces for security and privacy. Research
into privacy-preserving federated learning could enable cross-workspace pattern
detection (e.g., "this conflict resembles 47 historical cases in other
workspaces") without exposing sensitive data.

### Explainable Neural Components

While the symbolic layer is inherently explainable, the neural components
(embeddings, GNN predictions) are not. Research into explainability methods for
graph neural networks — such as GNNExplainer, attention visualization, and
counterfactual subgraph generation — would strengthen the overall
interpretability of the system.

### Automated Theory Selection

Currently, analysts choose which theory frameworks to apply. Research into
automated theory selection — using conflict features to recommend the most
applicable theoretical lenses — could improve analytical efficiency while
ensuring that relevant perspectives are not overlooked.

### Real-Time Streaming Analysis

The SSE streaming infrastructure is in place, but real-time analysis of
incoming event streams (news feeds, social media, diplomatic cables) with
continuous graph updates and automated alert generation represents a significant
engineering and research challenge.

---

## References

### Architecture Source Files

| Component | Path |
|-----------|------|
| Neurosymbolic architecture model | `packages/ontology/src/dialectica_ontology/neurosymbolic.py` |
| 15 node primitives | `packages/ontology/src/dialectica_ontology/primitives.py` |
| 20 edge types | `packages/ontology/src/dialectica_ontology/relationships.py` |
| 39 enums | `packages/ontology/src/dialectica_ontology/enums.py` |
| 3 tiers | `packages/ontology/src/dialectica_ontology/tiers.py` |
| 16 theory modules | `packages/ontology/src/dialectica_ontology/theory/` |
| 4 compatibility mappers | `packages/ontology/src/dialectica_ontology/compatibility/` |
| Extraction pipeline | `packages/extraction/src/dialectica_extraction/pipeline.py` |
| GraphRAG retriever | `packages/reasoning/src/dialectica_reasoning/graphrag/retriever.py` |
| Context builder | `packages/reasoning/src/dialectica_reasoning/graphrag/context_builder.py` |
| Query engine | `packages/reasoning/src/dialectica_reasoning/query_engine.py` |
| Hallucination detector | `packages/reasoning/src/dialectica_reasoning/hallucination_detector.py` |
| Symbolic rule modules | `packages/reasoning/src/dialectica_reasoning/symbolic/` |
| AI agents | `packages/reasoning/src/dialectica_reasoning/agents/` |
| Architecture overview | `docs/architecture.md` |
