# DIALECTICA Benchmarking Guide

How the DIALECTICA benchmarking system works, how to run benchmarks, interpret
results, and create custom gold-standard corpora.

---

## Overview

The benchmarking system evaluates the extraction pipeline's accuracy by comparing
its output against human-annotated gold-standard corpora. It measures entity
extraction, relationship extraction, and hallucination detection across multiple
conflict domains.

**Key components:**
- Backend: `POST /v1/admin/benchmark/run` endpoint
- Frontend: `/admin/benchmarks` dashboard with visual charts
- Gold standards: `data/seed/samples/` JSON files with annotated entities and edges
- Test suite: `packages/api/tests/test_benchmark.py`

---

## Available Corpora

DIALECTICA ships with 4 gold-standard benchmark corpora spanning different
conflict domains and text types:

| Corpus ID | Source Text | Domain | Entities | Edges | Tests |
|-----------|------------|--------|----------|-------|-------|
| `jcpoa` | Iran nuclear deal (JCPOA text excerpts) | Geopolitical / treaty | ~25 | ~30 | Actor extraction, treaty norms, process types |
| `romeo_juliet` | Shakespeare's Romeo and Juliet (selected scenes) | Interpersonal / literary | ~15 | ~20 | Character detection, emotional states, escalation |
| `crime_punishment` | Dostoevsky's Crime and Punishment (key chapters) | Psychological / literary | ~18 | ~22 | Internal conflict, moral reasoning, trust dynamics |
| `war_peace` | Tolstoy's War and Peace (battle + diplomacy scenes) | Armed conflict / literary | ~20 | ~25 | Multi-party conflict, power dynamics, events |

Each corpus contains:
- Source text passages for extraction
- Gold-standard entity annotations (node type, key properties)
- Gold-standard relationship annotations (edge type, source, target)
- Metadata (domain, expected tier, difficulty level)

---

## Running Benchmarks

### Via API (command line)

```bash
# Single corpus
curl -s -X POST http://localhost:8080/v1/admin/benchmark/run \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $ADMIN_API_KEY" \
  -d '{
    "corpus_id": "jcpoa",
    "tier": "standard",
    "include_graph_augmented": true
  }' | python -m json.tool
```

Parameters:
- `corpus_id` (required): One of the available corpus IDs
- `tier` (optional, default: `"standard"`): Extraction tier (`essential`, `standard`, `full`)
- `include_graph_augmented` (optional, default: `false`): Also run graph-augmented extraction and compare

### Via Make target

```bash
make benchmark
```

This runs the JCPOA benchmark with the standard tier against a running API server.

### Via test suite

```bash
make test-benchmark
# Runs: uv run pytest packages/api/tests/test_benchmark.py -v
```

The test suite validates benchmark infrastructure without requiring a live API
or external services.

### All corpora at once

```bash
for corpus in jcpoa romeo_juliet crime_punishment war_peace; do
  echo "=== $corpus ==="
  curl -s -X POST http://localhost:8080/v1/admin/benchmark/run \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $ADMIN_API_KEY" \
    -d "{\"corpus_id\":\"$corpus\",\"tier\":\"standard\"}" | python -m json.tool
done
```

---

## Interpreting Results

### Response format

```json
{
  "corpus_id": "jcpoa",
  "tier": "standard",
  "timestamp": "2026-04-06T12:00:00Z",
  "entity_metrics": {
    "precision": 0.85,
    "recall": 0.78,
    "f1": 0.81,
    "true_positives": 21,
    "false_positives": 4,
    "false_negatives": 6
  },
  "relationship_metrics": {
    "precision": 0.72,
    "recall": 0.65,
    "f1": 0.68,
    "true_positives": 19,
    "false_positives": 7,
    "false_negatives": 10
  },
  "hallucination_rate": 0.06,
  "duration_ms": 4523,
  "graph_augmented": null
}
```

### Metrics explained

| Metric | Formula | What It Means |
|--------|---------|---------------|
| **Precision** | TP / (TP + FP) | Of everything extracted, what fraction is correct? High precision = few false extractions. |
| **Recall** | TP / (TP + FN) | Of everything in the gold standard, what fraction was found? High recall = few missed entities. |
| **F1** | 2 * (P * R) / (P + R) | Harmonic mean of precision and recall. Primary benchmark metric. |
| **Hallucination rate** | Hallucinated / Total extracted | Fraction of extracted entities that have no match in the gold standard and no grounding in source text. |

### Target thresholds

| Metric | Minimum | Good | Excellent |
|--------|---------|------|-----------|
| Entity F1 | 0.65 | 0.75 | 0.85+ |
| Relationship F1 | 0.55 | 0.65 | 0.75+ |
| Hallucination rate | < 0.15 | < 0.10 | < 0.05 |

### Entity matching rules

An extracted entity is considered a **true positive** if:
1. It matches a gold-standard entity by node type (exact match)
2. The `name` or key identifying property has a fuzzy similarity >= 0.8
3. Key properties (e.g., `actor_type`, `event_type`) match exactly

An extracted entity with no gold-standard match is a **false positive**.
A gold-standard entity with no extraction match is a **false negative**.
A false positive with no grounding in the source text is a **hallucination**.

### Relationship matching rules

An extracted relationship is a **true positive** if:
1. Edge type matches the gold standard (exact match)
2. Source and target entities are both true positives
3. Direction is correct (source -> target)

---

## Frontend Dashboard

The benchmarking dashboard is available at `/admin/benchmarks` in the web
application. It provides:

- **Run benchmarks**: Select corpus, tier, and options, then run directly from the UI
- **Results table**: All benchmark runs sorted by timestamp with key metrics
- **Trend charts**: F1, precision, recall, and hallucination rate over time
- **Corpus comparison**: Side-by-side comparison of results across corpora
- **Drill-down**: Click a run to see entity-level and relationship-level details

### Accessing the dashboard

1. Navigate to `/admin/benchmarks`
2. Admin authentication is required (API key with admin level)
3. Select a corpus from the dropdown
4. Click "Run Benchmark"
5. Results appear in the table and charts update automatically

---

## Creating Custom Benchmark Corpora

### Gold standard JSON format

Create a JSON file in `data/seed/samples/` with this structure:

```json
{
  "corpus_id": "my_custom_corpus",
  "name": "My Custom Benchmark",
  "description": "Description of what this corpus tests",
  "domain": "workplace",
  "difficulty": "medium",
  "source_text": "The full text that the extraction pipeline will process...",
  "gold_standard": {
    "nodes": [
      {
        "label": "Actor",
        "name": "Jane Smith",
        "actor_type": "person",
        "role_title": "Senior Manager",
        "confidence": 1.0
      },
      {
        "label": "Actor",
        "name": "ACME Corp",
        "actor_type": "organization",
        "org_type": "corporation",
        "confidence": 1.0
      },
      {
        "label": "Conflict",
        "name": "Workplace Harassment Dispute",
        "scale": "micro",
        "domain": "workplace",
        "status": "active",
        "confidence": 1.0
      },
      {
        "label": "Event",
        "event_type": "MAKE_STATEMENT",
        "severity": 0.3,
        "description": "Formal complaint filed",
        "occurred_at": "2026-01-15T00:00:00Z",
        "confidence": 1.0
      }
    ],
    "edges": [
      {
        "edge_type": "PARTY_TO",
        "source": "Jane Smith",
        "target": "Workplace Harassment Dispute",
        "confidence": 1.0
      },
      {
        "edge_type": "PARTICIPATES_IN",
        "source": "Jane Smith",
        "target": "Formal complaint filed",
        "confidence": 1.0
      }
    ]
  }
}
```

### Node requirements

Every gold-standard node must have:
- `label`: One of the 15 node types (Actor, Conflict, Event, Issue, etc.)
- All required properties for that node type (see `docs/ontology.md`)
- `confidence`: Set to `1.0` for gold-standard annotations
- A unique identifying property (`name` for most types, `description` for Interest)

### Edge requirements

Every gold-standard edge must have:
- `edge_type`: One of the 20 edge types (PARTY_TO, CAUSED, etc.)
- `source`: Name/identifier of the source node (must match a gold-standard node)
- `target`: Name/identifier of the target node (must match a gold-standard node)
- Valid source/target label combination (see `relationships.py` edge schemas)

### Best practices for gold standards

1. **Annotate conservatively**: Only include entities that are clearly present in the text. Ambiguous cases hurt benchmark reliability.
2. **Cover all tiers**: Include entities from Essential, Standard, and Full tiers to test tier-specific extraction.
3. **Include negative cases**: Texts that mention entities ambiguously help test precision.
4. **Document decisions**: Add a `notes` field explaining annotation choices for border cases.
5. **Minimum size**: Aim for at least 10 entities and 10 edges per corpus for statistical significance.
6. **Cross-validate**: Have a second annotator review the gold standard before committing.

### Registering a custom corpus

After creating the JSON file, register it in the benchmark system:

1. Place the file in `data/seed/samples/`
2. The benchmark endpoint auto-discovers corpora by scanning the directory for files with a `gold_standard` key
3. Run your benchmark: `curl -X POST .../v1/admin/benchmark/run -d '{"corpus_id":"my_custom_corpus"}'`

---

## Benchmark Results in BigQuery

When BigQuery analytics is enabled (`BIGQUERY_ENABLED=true`), all benchmark
results are automatically written to the `benchmark_results` table:

```sql
SELECT
  corpus_id,
  tier,
  entity_f1,
  relationship_f1,
  hallucination_rate,
  timestamp
FROM `your-project.dialectica_analytics.benchmark_results`
ORDER BY timestamp DESC
LIMIT 20
```

This enables longitudinal analysis of extraction quality over time, across
model versions, and across corpora.

---

## Key File Locations

| File | Purpose |
|------|---------|
| `packages/api/src/dialectica_api/routers/benchmark.py` | Benchmark API endpoint |
| `packages/api/tests/test_benchmark.py` | Benchmark test suite |
| `data/seed/samples/*.json` | Gold-standard corpora |
| `apps/web/src/app/admin/benchmarks/page.tsx` | Frontend dashboard |
| `packages/api/src/dialectica_api/analytics.py` | BigQuery analytics client |
