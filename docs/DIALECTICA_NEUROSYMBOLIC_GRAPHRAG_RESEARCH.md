# DIALECTICA Neurosymbolic GraphRAG Research Memo

Date: 2026-05-01

This memo preserves the current research direction for DIALECTICA as the TACITUS ontology-driven ingestion, graph, retrieval, reasoning, review, and evaluation backbone. It is intentionally opinionated and implementation-facing.

## Executive Decisions

1. Neo4j AuraDB is the primary live graph memory for the near-term workbench and demo path.
2. Databricks Delta remains the durable analytical substrate for source rows, extraction candidates, graph-ready nodes and edges, review decisions, benchmark runs, and workflow audit logs.
3. The next engineering order is graph writeback, then hybrid retrieval planning, then trace/explanation viewing, then human review.
4. The eight stable conflict primitives remain the core ontology: Actor, Claim, Interest, Constraint, Leverage, Commitment, Event, Narrative.
5. Every extracted object must carry provenance, confidence, ontology version, source identity, and review status before it can become durable graph memory.
6. Rules should write RuleSignal artifacts instead of mutating primitive facts.
7. Benchmarks must compare plain LLM, vector RAG, GraphRAG, and neurosymbolic GraphRAG with provenance, temporal, causal, contradiction, and abstention metrics.

## Research-Backed Architecture Notes

Neo4j GraphRAG supports retriever-based RAG patterns, including vector, hybrid, and Cypher-expanded retrieval. DIALECTICA should expose typed retrieval plans before execution so every answer can be audited and benchmarked.

LangExtract is valuable for long-document extraction because its stated design emphasizes precise source grounding, structured outputs, long-document chunking, multiple passes, and interactive visualization. DIALECTICA should treat ungrounded extraction as review-only.

Microsoft GraphRAG is best used as a secondary enrichment channel for global/community questions. It should not replace the core eight-primitive extraction pipeline.

Databricks Agent Evaluation and MLflow should be used for offline evaluation and production monitoring when the deployed answer pipeline is ready. The benchmark engine should log request, response, retrieved context, trace, rule firings, costs, and latency.

Ragas provides useful baseline metrics for RAG evaluation, including faithfulness, context precision, context recall, response relevancy, factual correctness, and rubric scoring. DIALECTICA still needs custom metrics for provenance fidelity, causal precision, temporal accuracy, contradiction handling, and abstention quality.

## Production Data Contract

The minimum durable graph contract is:

- SourceDocument, SourceChunk, EvidenceSpan
- Actor, Claim, Interest, Constraint, Leverage, Commitment, Event, Narrative
- RuleSignal, RuleFire, AnswerConstraint, BenchmarkTarget, BenchmarkRun
- ReviewDecision

All graph writes must be idempotent. Node identity is stable on `id`. Relationship identity is deterministic from source, relationship type, and target. Retries must not duplicate nodes or edges.

## Current Implementation Mapping

Implemented before this memo:

- GraphOps ingestion endpoint for text, samples, TXT, and PDF.
- Local deterministic eight-primitive extraction.
- Dynamic ontology planning.
- Neurosymbolic rule evaluation.
- Benchmark endpoint and local scoring.
- Praxis context bundle endpoint.
- Workbench readiness endpoint.
- Local run persistence.
- Databricks staging and workflow triggers.

Implemented in the current wave:

- Reusable graph writeback planner and Neo4j writer: `apps/web/src/lib/graphopsGraph.ts`.
- Standalone graph writeback endpoint: `POST /api/graphops/graph/upsert`.
- Typed retrieval plan builder: `apps/web/src/lib/graphopsRetrieval.ts`.
- Retrieval planning endpoint: `POST /api/graphops/retrieval/plan`.
- Analyst trace bundle builder: `apps/web/src/lib/graphopsTrace.ts`.
- Trace bundle endpoint: `POST /api/graphops/trace/build`.

## Architecture Sources To Keep Rechecking

- Neo4j GraphRAG Python: https://neo4j.com/docs/neo4j-graphrag-python/current/user_guide_rag.html
- LangExtract: https://github.com/google/langextract
- Microsoft GraphRAG dataflow: https://microsoft.github.io/graphrag/index/default_dataflow/
- Databricks Agent Evaluation: https://docs.databricks.com/aws/en/generative-ai/agent-evaluation
- Ragas metrics: https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/

