# Open-source TACITUS test corpus

Use open, public-domain, or official public documents. Avoid closed datasets and sources that require special licenses. The goal is to test DIALECTICA as TACITUS' backbone across very different kinds of human friction.

## Tier 0: repo-native smoke tests

Start with data already in the repo:

| File | What it tests |
| --- | --- |
| `data/seed/samples/hr_mediation.json` | workplace conflict, trust, interests, mediation |
| `data/seed/samples/jcpoa.json` | diplomacy, norms, negotiation constraints |
| `data/seed/samples/commercial_dispute.json` | commercial dispute, issues, interests, process |
| `data/seed/benchmarks/romeo_juliet_gold.json` | literary conflict extraction gold set |
| `data/seed/benchmarks/crime_punishment_gold.json` | guilt, norm violation, evidence ambiguity |
| `data/seed/benchmarks/war_peace_gold.json` | large multi-actor political/social conflict |

## Tier 1: public-domain books and plays

These are useful because they are messy, narrative, multi-actor, and full of motives, alliances, betrayals, norms, and escalation.

| Work | Source type | Why DIALECTICA should handle it |
| --- | --- | --- |
| Shakespeare, `Romeo and Juliet` | Project Gutenberg / public domain | family conflict, escalation, mediator failure, emotions |
| Shakespeare, `Julius Caesar` | Project Gutenberg / public domain | coalition formation, betrayal, legitimacy, power |
| Dostoevsky, `Crime and Punishment` | Project Gutenberg / public domain | norm violation, guilt, investigation, evidence |
| Tolstoy, `War and Peace` | Project Gutenberg / public domain | war, diplomacy, elite networks, temporal graph scale |
| Austen, `Pride and Prejudice` | Project Gutenberg / public domain | social status, misperception, trust repair |
| Thucydides, `History of the Peloponnesian War` | Project Gutenberg / public domain | strategic coercion, alliance networks, Melian Dialogue |
| Machiavelli, `The Prince` | Project Gutenberg / public domain | power analysis, strategic advice, norm ambiguity |
| Douglass, `Narrative of the Life of Frederick Douglass` | Project Gutenberg / public domain | coercive power, norms, identity, liberation conflict |

Best first book test: `Romeo and Juliet`.

Why: the repo already has a gold benchmark, the conflict is obvious, and failures are easy to inspect.

## Tier 2: official public documents

Use these to test structured institutional conflict.

| Document family | Why it matters |
| --- | --- |
| UN Security Council resolutions | norms, violations, sanctions, actor positions |
| UN General Assembly speeches | narratives, claims, framing, grievances |
| Peace agreements | commitments, processes, outcomes, verification |
| Treaties and declarations | norm graphs and obligation extraction |
| U.S. Federal Register notices | stakeholder conflict, regulation, evidence, public comments |
| Congressional hearings from govinfo | claims, counterclaims, power, institutional roles |
| Court opinions in the public domain | legal issues, evidence, holdings, reasoning chains |

## Tier 3: TACITUS-owned unstructured data

These are likely the most valuable because they map directly to product needs:

| Data | What to extract |
| --- | --- |
| founder notes and memos | strategic assumptions, product conflicts, decisions |
| user interviews | needs, pain points, trust failures, stakeholder language |
| mediation transcripts | actors, interests, concessions, emotion shifts |
| customer support logs | repeated friction patterns and escalation triggers |
| sales calls | objections, buying coalitions, blockers |
| community discussions | narrative clusters and trust dynamics |
| meeting notes | commitments, unresolved issues, owners |

## Concrete experiments

### Experiment 1: Can DIALECTICA extract a minimal conflict graph?

Data: first act of `Romeo and Juliet`.

Expected graph:

- Actors: Romeo, Juliet, Capulet, Montague, Tybalt, Benvolio, Prince.
- Conflict: Capulet-Montague feud.
- Issues: family honor, public violence, forbidden relationship.
- Events: street fight, prince warning, party encounter.
- Edges: `PARTY_TO`, `OPPOSED_TO`, `PARTICIPATES_IN`, `CAUSED`.

Pass condition: at least 80% of obvious actors and the central feud appear.

### Experiment 2: Can it distinguish stated claims from inferred interests?

Data: Melian Dialogue from Thucydides.

Expected:

- Stated claims: Athens' demand, Melos' neutrality argument.
- Inferred interests: survival, deterrence, reputation, empire credibility.
- Power dynamic: Athens has coercive military power.

Pass condition: interests are not treated as direct quotes unless supported.

### Experiment 3: Can it build an evidence-backed norm graph?

Data: one UN Security Council resolution.

Expected:

- Norms: obligations, prohibitions, reporting requirements.
- Actors: UN Security Council, member states, named parties.
- Edges: `GOVERNED_BY`, `VIOLATES`, `EVIDENCED_BY`.

Pass condition: key norms have evidence links.

### Experiment 4: Can Databricks find graph quality gaps?

Data: any seeded workspace plus one new book/document extraction.

Run:

```text
01_neo4j_delta_operational_signals.py
02_review_queue.py
```

Expected:

- Delta tables are created.
- `review_queue` contains unsupported nodes and low-confidence edges.
- A human can validate or reject weak graph claims.

### Experiment 5: Can KGE produce useful but non-authoritative candidates?

Data: graph with at least 200 edges.

Run:

```text
03_kge_from_delta_link_predictions.py
```

Expected:

- `kge_link_candidates` contains suggested links.
- None are automatically merged into the authoritative graph.
- Human validation remains required.

## Tools to use

| Tool | Role |
| --- | --- |
| Databricks Jobs | schedule graph snapshot, review queue, KGE runs |
| Databricks SQL | dashboards over Delta tables |
| Databricks secret scopes | Neo4j and Gemini credentials |
| Neo4j Browser | inspect graph structure and reasoning write-back |
| Neo4j Spark Connector | higher-throughput Neo4j/Delta transfer once the Python-driver notebook proves the flow |
| Project Gutenberg | public-domain book corpus |
| Internet Archive | additional public-domain and public records metadata |
| UN Digital Library | official UN records and resolutions |
| govinfo | U.S. public government documents |
| PyKEEN | knowledge graph embedding/link prediction |
| MLflow | track KGE experiments and extraction-quality runs |

## First 72-hour sequence

1. Rotate exposed secrets.
2. Create Databricks secret scope `tacitus`.
3. Seed Neo4j with repo sample data.
4. Run notebook `01`.
5. Run notebook `02`.
6. Extract `Romeo and Juliet` Act 1 into a new workspace.
7. Run notebooks `01` and `02` again.
8. Inspect `review_queue` and correct obvious mistakes.
9. Add a UN resolution as a second workspace.
10. Run notebook `03` only after the graph has at least 200 edges.

## What good looks like

DIALECTICA becomes useful when each graph claim has this shape:

```text
claim -> evidence -> confidence -> symbolic check -> optional neural suggestion -> human validation
```

Databricks should own the recurring operational loop. Neo4j should remain the live reasoning graph. Gemini should extract and summarize, but not silently promote uncertain claims.
