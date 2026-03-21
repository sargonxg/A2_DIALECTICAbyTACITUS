# ADR-004: PLOVER Over CAMEO for Event Coding

**Status:** Accepted
**Date:** 2025-02-10

## Context
Conflict event coding standards: CAMEO (200+ numeric codes, legacy), PLOVER (16 human-readable types, modern). GDELT uses CAMEO; newer datasets adopt PLOVER.

## Decision
Use PLOVER as the primary event coding standard. Maintain bidirectional CAMEO mapping for GDELT compatibility. PLOVER's 16 types map cleanly to ACO EventType enum with severity nuances per mode.

## Consequences
- **Positive:** Human-readable codes; cleaner mapping to ACO; QuadClass alignment; mode-level severity
- **Negative:** Must maintain CAMEO compatibility layer for GDELT; some CAMEO granularity lost
- **Mitigation:** Keep cameo.py compatibility module; GDELT root codes (14-20) map to PLOVER equivalents
