# GraphOps Product Operating Model

`/graphops` is the protected DIALECTICA operator console. It should answer one
practical question first:

```text
I need to understand this conflict. What should I ingest, structure, verify,
query, benchmark, and decide next?
```

## Product Flow

1. Define the mission: mediation, policy analysis, field intelligence,
   literary conflict research, or Praxis human friction.
2. Select or generate an ontology profile from user role, source type,
   objective, geography, time window, known actors, sensitivity, and question
   type.
3. Ingest sources into Databricks Delta with source trust and provenance.
4. Extract TACITUS primitives with Databricks AI Functions.
5. Validate candidates against ontology, evidence, temporal, and provenance
   gates.
6. Write accepted facts to Neo4j as a workspace-scoped situation graph.
7. Snapshot graph state back to Delta for quality scoring, review queues, KGE,
   and benchmarks.
8. Answer user questions with graph-grounded context and show what is verified,
   inferred, uncertain, or missing.

## Graph Layers

| Layer | Job |
| --- | --- |
| Identity | Separate users, projects, workspaces, and situations. |
| Source | Track documents, chunks, evidence, claims, source trust, and license. |
| Situation | Model actors, events, conflicts, issues, interests, norms, processes, outcomes. |
| Temporal | Separate chronology, causality, phase transitions, and relapse windows. |
| Reasoning | Store inference traces, contradiction signals, review decisions, and operational signals. |
| Profile | Adapt extraction and query behavior to the specific use case. |

## Repeatable Benchmark Strategy

The benchmark must compare:

- baseline LLM answer from raw text only,
- DIALECTICA answer grounded in ontology, Neo4j facts, evidence, and graph
  retrieval,
- gold summary or expert rubric,
- judge output with provenance, graph overlap, causal precision, ambiguity, and
  unsupported-claim penalties.

Every run should record:

- source pack version,
- ontology profile version,
- prompt version,
- Databricks run id,
- graph snapshot/version,
- model endpoint,
- judge endpoint,
- row counts and failure categories.

## Aha Use Cases

- Mediation: separate positions from interests and show repair options.
- Policy: show which rules bind which actors and which constraints block which
  option.
- Intelligence understanding: keep rumor, direct observation, and inference
  separate.
- Praxis: turn collaboration friction into commitments, contested scope, trust
  risks, and next questions.
- Literary conflict: use open books as repeatable conflict corpora before
  sensitive private material.

## Current Live Proof

Databricks job `261036137711214` run `795929402349644` succeeded. It produced:

| Table | Rows |
| --- | ---: |
| `raw_text_chunks` | 333 |
| `ai_extraction_candidates` | 275 |
| `ontology_profile_coverage` | 4 |
| `source_reliability_signals` | 3 |
| `temporal_event_signals` | 3 |
| `claim_review_queue` | 216 |

Neo4j writeback is implemented but should be enabled only after rotating the
previously exposed Neo4j credentials and adding fresh values to Databricks and
deployment secrets.
