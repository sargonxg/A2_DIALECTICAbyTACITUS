# ADR-002: Symbolic Firewall — Deterministic Conclusions Are Inviolable

**Status:** Accepted
**Date:** 2025-01-20

## Context
DIALECTICA combines symbolic rules (treaty checks, legal constraints) with neural predictions (GNN, LLM). Users must trust that verified legal facts cannot be overridden by probabilistic guesses.

## Decision
Implement a SymbolicFirewall that ensures conclusions tagged `confidence_type=deterministic` are never overridden by `probabilistic` predictions. Deterministic conclusions always have `confidence=1.0` and must cite a `source_rule`.

## Consequences
- **Positive:** Legal/treaty conclusions are always trustworthy; clear provenance chain; auditable
- **Negative:** Neural predictions may be suppressed even when correct; requires careful contradiction detection
- **Mitigation:** Contradiction detection uses semantic patterns, not string matching; rejected predictions are logged for human review
