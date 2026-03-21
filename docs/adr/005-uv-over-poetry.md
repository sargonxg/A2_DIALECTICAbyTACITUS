# ADR-005: UV Workspaces Over Poetry for Monorepo

**Status:** Accepted
**Date:** 2025-03-01

## Context
DIALECTICA is a Python monorepo with 5+ packages and cross-dependencies. Poetry's workspace support is limited; UV provides native workspace support with millisecond resolution.

## Decision
Migrate from Poetry to UV workspaces. Each package uses PEP 621 `[project]` format with hatchling build backend. Single `uv.lock` at root. CI uses `astral-sh/setup-uv@v5`.

## Consequences
- **Positive:** 10-100x faster dependency resolution; single lockfile; native workspace support; PEP 621 standard
- **Negative:** UV is newer with smaller ecosystem; some CI templates assume pip/poetry
- **Mitigation:** UV is rapidly becoming the Python standard; `uv run` replaces `poetry run` 1:1
