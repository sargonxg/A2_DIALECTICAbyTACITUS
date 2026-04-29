# TACITUS CEO/CTO Workflows

This is the practical product direction for DIALECTICA as the backbone of
TACITUS.

## 1. Conflict Intelligence Workbench

Input:

- books,
- transcripts,
- complaints,
- reports,
- policy memos,
- legal filings,
- meeting notes.

Process:

```text
upload/source -> chunk -> extract ontology candidates -> validate -> Neo4j graph
-> Databricks quality queue -> analyst review -> graph-grounded answer
```

Output:

- actor map,
- escalation chain,
- interest map,
- norm/violation map,
- evidence trail,
- recommended questions for a mediator or analyst.

## 2. Human Friction Early Warning

Target users:

- HR,
- founders,
- team leads,
- mediation professionals,
- legal operations.

Graph signals:

- unresolved commitments,
- contested scope,
- rising negative emotion,
- low trust,
- power asymmetry,
- missing process,
- repeated narrative drift.

Databricks computes:

- friction trend,
- missing evidence,
- low-confidence claims,
- review priority,
- conflict-stage movement.

## 3. Policy Thinking Engine

Target users:

- policy analysts,
- city agencies,
- NGOs,
- public-sector strategy teams.

Graph objects:

- Actor,
- Norm,
- Interest,
- Constraint,
- Process,
- Outcome,
- Evidence,
- Narrative.

Questions TACITUS should answer:

- What constraints make this policy infeasible?
- Which actors hold veto power?
- Which interests are stated versus hidden?
- Which legal or procedural norms govern action?
- What intervention process could reduce friction?

## 4. Neurosymbolic Benchmark Lab

Goal:

Prove that graph-grounded TACITUS beats a baseline LLM for conflict reasoning.

Benchmark dimensions:

- graph overlap,
- provenance F1,
- causal precision,
- contradiction detection,
- commitment tracking,
- policy constraint extraction,
- narrative drift detection.

Databricks tables:

- `benchmark_items`,
- `benchmark_prompts`,
- `benchmark_answers`,
- `benchmark_judgments`.

Comparison:

```text
Baseline LLM: text -> answer
DIALECTICA: text -> graph -> symbolic checks -> graph context -> answer
```

Expected advantage:

- fewer unsupported claims,
- more precise causal chains,
- clearer source attribution,
- better separation of positions and interests,
- better handling of ambiguity and contradiction.

## 5. Operating Console

The protected `/graphops` page should become the operator cockpit:

- Databricks job map,
- run status,
- graph layer explanation,
- ontology contract,
- live Neo4j query tester,
- benchmark plan,
- quality queue,
- examples and demos.

Current password:

```text
username: tacitus
password: adialectica1900
```

Keep this as temporary lab access. Rotate before wider sharing.
