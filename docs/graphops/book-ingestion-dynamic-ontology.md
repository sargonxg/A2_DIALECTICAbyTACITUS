# Book And Text Ingestion Architecture

Date: 2026-05-01

## Working Principle

DIALECTICA should not send raw books or case files directly into final extraction. The reliable path is:

```text
source -> canonical cleaning -> episode pre-structure -> source chunks
-> evidence spans -> ontology primitive extraction -> rule/review signals
-> graph-ready rows -> Neo4j/Delta/benchmark artifacts
```

## Research And Implementation Anchors

- Google LangExtract emphasizes source-grounded structured extraction, long-document chunking, multiple passes, and interactive review of extracted spans.
- BookNLP is the closest open-source reference for book-specific NLP: character/entity handling, literary event detection, and coreference constraints.
- Microsoft GraphRAG’s indexing workflow separates documents, text units, entities, relationships, optional claims, graph augmentation, and community reports.
- Stanford CoreNLP shows the traditional deterministic pieces that still matter: relation extraction, quote extraction, coreference annotations, temporal expression normalization, and token-pattern rules.

## What DIALECTICA Implements Now

Frontend/API extraction:

- removes common Project Gutenberg header/footer boilerplate;
- segments books by `ACT`, `SCENE`, `CHAPTER`, or fallback narrative turns;
- segments non-book material by event windows;
- creates `SourceChunk`, `Episode`, `EvidenceSpan`, `Claim`, `Actor`, `Event`, `Constraint`, `Commitment`, `Narrative`, and `ActorState` candidates;
- emits a `PreExtractionPlan` primitive with segmentation mode, removed sections, required nodes/edges, and custom mappings;
- emits a `dynamicOntology` plan with extraction passes and validation rules.

Databricks extraction:

- reads staged upload rows from `raw_documents`;
- strips common Gutenberg boilerplate;
- splits text into sentence windows;
- writes Delta `primitive_candidates` and `graph_ready_nodes`;
- creates deterministic candidate rows for source documents, chunks, episodes, evidence spans, claims, actors, events, constraints, commitments, and narratives.

## Dynamic Ontology Contract

Aletheia dynamic ontology creation is now exposed through:

- `POST /api/graphops/ontology/create`
- pipeline-plan artifacts through `POST /api/graphops/pipelines/create`
- visual planning in `/graphops`

Every custom type must map to a TACITUS core primitive:

```text
Character -> Actor
Scene -> Episode
FeudFrame -> Narrative
BanishmentOrRule -> Constraint
VowOrPromise -> Commitment
Institution -> Actor
VetoPoint -> Leverage
ImplementationRisk -> Claim
RepairOffer -> Commitment
TrustRepair -> ActorState
```

## Next Engineering Targets

1. Add human review decisions that can accept/reject candidate primitives before graph writeback.
2. Add export of `graph_ready_edges`, not only graph-ready nodes.
3. Add optional BookNLP/LangExtract-inspired adapters behind a stable extraction interface.
4. Add quote attribution for literary and meeting-transcript sources.
5. Add temporal expression normalization for exact dates, relative dates, phases, and scene order.
6. Add community detection/report generation after Neo4j/Delta graph materialization.
7. Add benchmark comparisons between raw LLM summary, deterministic extraction, and graph-grounded answers.

## Source Links

- Google LangExtract: https://github.com/google/langextract
- BookNLP: https://github.com/booknlp/booknlp
- Microsoft GraphRAG dataflow: https://microsoft.github.io/graphrag/index/default_dataflow/
- Stanford CoreNLP: https://www-nlp.stanford.edu/software/corenlp.shtml
