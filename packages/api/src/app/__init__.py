"""Path shim for repo-root optional app extensions."""

from __future__ import annotations

from pathlib import Path

_here = Path(__file__).resolve()
_candidates = [
    _here.parents[4] / "app",
    Path("/app/app"),
]

for _candidate in _candidates:
    if _candidate.exists():
        __path__.append(str(_candidate))  # type: ignore[name-defined]
