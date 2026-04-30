# DIALECTICA Neurosymbolic Rule Layer

The rule layer is the deterministic guardrail between graph memory and LLM generation. It does not replace LLMs. It constrains them.

## Purpose

For conflict analysis, the failure modes are predictable:

- chronology becomes causality;
- weak claims become confident prose;
- commitments and constraints are collapsed into generic summaries;
- source reliability disappears;
- ontology coverage is too weak for the answer being asked;
- mediation readiness is inferred without enough graph evidence.

The rule layer turns these failure modes into executable signals.

## Current Executable Slice

Implemented:

- `apps/web/src/lib/graphopsRules.ts`
- `POST /api/graphops/rules/evaluate`
- ingestion results include `ruleEvaluation`
- `/graphops` can evaluate the selected sample or current extraction

Rules currently implemented:

- Commitment Constraint Propagation
- Causal vs Temporal Separation
- Power Asymmetry Process Risk
- Source Trust Claim Downgrade
- Ontology Coverage Gate
- Ripeness Signal
- Narrative Identity Escalation
- Legal Constraint Option Filter

Each rule returns:

- rule id;
- rule name;
- category;
- severity;
- rationale;
- evidence ids;
- affected primitive ids;
- recommended action;
- benchmark target.

## Book Conflict-Resolution Lens

The first high-value lens is a public-domain book analyzed as a conflict system, not as a summary.

Example: *Romeo and Juliet*

The graph should model:

- actors: Romeo, Juliet, Capulet, Montague, Tybalt, Mercutio, Prince, Friar Laurence;
- episodes: family feud, secret bond, violent escalation, banishment, failed intervention;
- primitives: Actor, Claim, Event, Narrative, Constraint, Commitment, ActorState, EvidenceSpan;
- rule signals: narrative identity escalation, causal-vs-temporal separation, power/process risk, ontology coverage;
- benchmarks: ontology coverage, temporal accuracy, graph-grounded answer quality.

The goal is to ask questions like:

- How do love, power, secrecy, banishment, and failed mediation interact?
- Which events are merely sequential and which are causally supported?
- Which constraints shape the possible interventions?
- Which narratives intensify the conflict?
- What would a mediator need to verify before proposing an intervention?

## Answer Constraints

Rule evaluation returns answer constraints for LLM generation:

- do not state causal claims unless a `CAUSED` edge or causal source span exists;
- mark low-confidence claims as candidate or unverified;
- prefer cited evidence spans over summary-only claims;
- separate temporal order, commitments, constraints, leverage, and narrative frames;
- if ontology coverage is weak, ask for more sources or targeted extraction.

## Benchmark Targets

Rule signals automatically name benchmark targets:

- commitment recall;
- ambiguity handling;
- provenance fidelity;
- causal precision;
- temporal accuracy;
- intervention usefulness;
- source reliability;
- ontology coverage;
- policy constraint accuracy.

## Next Implementation Step

Persist rule signals into Neo4j and Delta:

- `RuleSignal`
- `RuleFire`
- `AnswerConstraint`
- `BenchmarkTarget`
- `ReviewDecision`

These should be linked to:

- workspace;
- case;
- episode;
- extraction run;
- evidence spans;
- affected graph primitives.
