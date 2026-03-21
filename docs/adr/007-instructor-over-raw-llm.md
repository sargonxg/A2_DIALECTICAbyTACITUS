# ADR-007: Instructor + LiteLLM Over Raw LLM Calls

**Status:** Accepted
**Date:** 2025-03-10

## Context
The extraction pipeline needs structured output (Pydantic models) from LLMs. Options: raw Vertex AI JSON mode, Instructor (Pydantic validation + retry), LangChain output parsers.

## Decision
Use Instructor with LiteLLM as the backend for structured extraction. Instructor provides automatic Pydantic validation, retry on schema errors (max_retries=3), and provider-agnostic access. Keep raw Gemini as fallback.

## Consequences
- **Positive:** Type-safe extraction; automatic retry on validation failure; provider-agnostic via LiteLLM; clean Pydantic response models
- **Negative:** Additional dependency; LiteLLM adds a layer of abstraction; some provider-specific features not exposed
- **Mitigation:** Fallback to raw GeminiExtractor when Instructor unavailable; LiteLLM supports all major providers
