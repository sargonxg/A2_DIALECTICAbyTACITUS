# DIALECTICA Pipeline Configuration Studio

The Pipeline Configuration Studio is the product layer for building TACITUS graph workflows per user, case, source type, and objective. A workspace is the unit of work: a book, mediation case, policy dispute, argument corpus, field situation, or expert-method knowledge base.

## Why This Exists

DIALECTICA should not be a generic RAG upload box. It should help a user decide:

- what they need to understand;
- which sources are trusted, internal, public, media, or uncertain;
- which ontology profile is appropriate;
- how the situation should be divided into temporal episodes;
- which graph layers should be built;
- which agents should run at the end;
- how the result should be benchmarked.

The core thesis remains: probabilistic LLM output becomes useful for conflict analysis only when it is converted into scoped, source-backed, temporally aware graph memory.

## Workspace Project Types

Current project templates:

- **Book Conflict Lab**: public-domain books such as *Romeo and Juliet* or *War and Peace*.
- **Mediation Case File**: party statements, meeting notes, transcripts, and commitments.
- **Policy Friction Map**: statutes, policy memos, public comments, implementation constraints.
- **Argument Claim Graph**: debates, legal arguments, essays, claims, warrants, objections.
- **Field Situation Portal**: public reports, interviews, observations, source reliability, uncertainty.
- **Labor Union Mediation**: collective agreements, bargaining notes, union statements, employer offers.
- **Regional Border Process**: maps, local media, public statements, legal documents, meeting notes.
- **Expert Method Graph**: mediator manuals, legal reasoning, HR playbooks, expert thinking.

## Colored Pipeline Stages

1. **Ingest**: upload TXT/PDF/text, stage source metadata, preserve provenance.
2. **Ontology**: use Aletheia to generate a dynamic case-specific ontology profile.
3. **Temporal**: split the case into episodes, phases, turning points, valid time ranges.
4. **Structure**: extract TACITUS primitives such as Actor, Claim, Commitment, Constraint, Event, Narrative, ActorState, EvidenceSpan.
5. **Graph**: write source graph, situation graph, temporal graph, abstract knowledge graph, reasoning graph, and activity graph.
6. **Reason**: apply graph queries, GraphRAG, symbolic checks, abstract frameworks, and source-grounded retrieval.
7. **Act**: run agents that produce briefs, questions, review queues, and answer plans.
8. **Benchmark**: compare graph-grounded answers against baseline LLM answers.

## Aletheia Dynamic Ontology Engine

Aletheia creates and maintains dynamic ontology profiles. It can add custom concepts only if they map back to TACITUS core primitives.

Examples:

- `RedLine -> Constraint`
- `Vow -> Commitment`
- `Institution -> Actor`
- `VetoPoint -> Leverage`
- `Scene -> Episode`
- `TrustRepair -> ActorState`

Every ontology extension must include:

- workspace ID;
- case ID;
- ontology version;
- core mapping;
- validation status;
- source/provenance requirements;
- benchmark expectations.

## Example: Labor Union Mediation

Sources:

- collective agreement;
- union demands;
- employer offer;
- meeting notes;
- local media.

Ontology focus:

- Actor;
- Commitment;
- Constraint;
- Interest;
- Leverage;
- ActorState;
- Episode.

Episodes:

- pre-bargaining;
- strike threat;
- mediated session;
- tentative agreement;
- compliance review.

Graph outputs:

- commitment ledger;
- red-line map;
- trust-state timeline;
- mediator option graph.

Benchmark:

- commitment recall;
- provenance fidelity;
- intervention usefulness.

## Example: Regional Border Process

Sources:

- maps;
- local media;
- administrative law;
- stakeholder letters;
- meeting transcript.

Ontology focus:

- Actor;
- Claim;
- Narrative;
- Constraint;
- Event;
- Source;
- EvidenceSpan.

Episodes:

- historical claim;
- administrative change;
- public escalation;
- closed-door meeting;
- proposed settlement.

Graph outputs:

- claim-evidence graph;
- actor influence graph;
- norm constraint map;
- meeting prep brief.

Benchmark:

- causal precision;
- temporal accuracy;
- source reliability.

## Example: Romeo and Juliet Human Friction

Sources:

- Project Gutenberg *Romeo and Juliet*;
- scene summaries;
- optional scholarly notes.

Ontology focus:

- Actor;
- Narrative;
- Event;
- Constraint;
- Commitment;
- ActorState;
- Episode.

Episodes:

- family feud;
- secret bond;
- violent escalation;
- banishment;
- failed intervention.

Graph outputs:

- character conflict graph;
- love-power-constraint map;
- escalation timeline;
- counterfactual question set.

Benchmark:

- ontology coverage;
- temporal accuracy;
- graph-grounded answer quality.

## Backend Modes

### Databricks + Neo4j

Use Databricks as the lakehouse and operational batch engine. Sources and pipeline artifacts are staged to Databricks Workspace files, then jobs should convert them into Delta tables and extraction candidates. Neo4j is the live graph memory.

Relevant docs:

- Databricks Declarative Automation Bundles resources: https://docs.databricks.com/aws/en/dev-tools/bundles/resources
- Databricks Asset Bundles / jobs workflow: https://docs.databricks.com/en/jobs/how-to/use-bundles-with-jobs.html
- Databricks Mosaic AI Vector Search: https://docs.databricks.com/gcp/en/generative-ai/vector-search
- Neo4j Spark connector for Databricks: https://neo4j.com/docs/spark/current/databricks/

### Local Python

Use the local `dialectica` Python CLI for source loading, chunking, rule-based primitive extraction, in-memory tests, and JSONL artifacts. This is the low-cost fallback.

### Neo4j-Only

Use Neo4j as the direct operational graph backend. This requires rotated production credentials and server-side write paths only.

### FalkorDB Experimental

Potential lightweight graph backend for a future adapter. It should follow the same `GraphAdapter` interface and never bypass provenance requirements.

## Graph Layers

DIALECTICA should build multiple connected graph layers:

- **Source provenance graph**: documents, chunks, evidence spans, reliability.
- **Situation graph**: actors, events, commitments, constraints, narratives.
- **Episodic temporal graph**: episodes, phases, valid_from, valid_to, observed_at.
- **Abstract knowledge graph**: frameworks, concepts, legal/mediation methods, expert reasoning.
- **Reasoning trace graph**: inferences, contradictions, review decisions, answer plans.
- **Activity audit graph**: users, workspaces, pipeline runs, agent actions.

## Benchmark Blocks

Every pipeline should attach benchmarks:

- provenance fidelity;
- temporal accuracy;
- causal precision;
- commitment recall;
- ontology coverage;
- baseline vs graph-grounded answer quality.

## Current Implementation

Implemented in the web app:

- `/graphops` pipeline studio UI;
- `/api/graphops/pipelines/create`;
- project templates;
- colored block stages;
- Aletheia ontology profile artifact generation;
- pipeline artifact staging to Databricks Workspace files;
- benchmark block catalog;
- agent launch planning.

Still needed:

- Databricks job to read staged pipeline artifacts into Delta;
- fresh Neo4j secrets for production graph writes;
- live graph explorer from real Neo4j data;
- temporal episode splitter;
- full GraphRAG answer API with citations.
