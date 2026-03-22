"""
PLOVER Compatibility — Full bidirectional mapping between DIALECTICA and PLOVER coding.

PLOVER (Political Language Ontology for Verifiable Event Records) defines
16 top-level event types and a QuadClass classification. This module maps
PLOVER types to ACO primitives, including severity and mode nuances.
"""

from __future__ import annotations

from enum import StrEnum

from dialectica_ontology.enums import EventType, QuadClass

# ─── PLOVER 16 Event Types ──────────────────────────────────────────────────


class PloverEventType(StrEnum):
    """The 16 PLOVER top-level event types."""

    AGREE = "AGREE"
    AID = "AID"
    ARREST = "ARREST"
    ASSAULT = "ASSAULT"
    CONSULT = "CONSULT"
    COOPERATE = "COOPERATE"
    COERCE = "COERCE"
    DEMAND = "DEMAND"
    DISAPPROVE = "DISAPPROVE"
    MOBILIZE = "MOBILIZE"
    PROTEST = "PROTEST"
    REJECT = "REJECT"
    RETREAT = "RETREAT"
    RESTRICT = "RESTRICT"
    SANCTION = "SANCTION"
    THREATEN = "THREATEN"


# ─── PLOVER event code <-> DIALECTICA EventType ─────────────────────────────

_PLOVER_TO_DIALECTICA: dict[str, EventType] = {
    "AGREE": EventType.AGREE,
    "AID": EventType.AID,
    "ARREST": EventType.COERCE,  # ARREST maps to coercive action
    "ASSAULT": EventType.ASSAULT,
    "CONSULT": EventType.CONSULT,
    "COOPERATE": EventType.COOPERATE,
    "COERCE": EventType.COERCE,
    "DEMAND": EventType.DEMAND,
    "DISAPPROVE": EventType.DISAPPROVE,
    "MOBILIZE": EventType.EXHIBIT_FORCE_POSTURE,
    "PROTEST": EventType.PROTEST,
    "REJECT": EventType.REJECT,
    "RETREAT": EventType.YIELD,  # RETREAT maps to yielding
    "RESTRICT": EventType.REDUCE_RELATIONS,
    "SANCTION": EventType.REDUCE_RELATIONS,  # SANCTION = reducing relations
    "THREATEN": EventType.THREATEN,
}

_DIALECTICA_TO_PLOVER: dict[EventType, str] = {v: k for k, v in _PLOVER_TO_DIALECTICA.items()}

# ─── PLOVER QuadClass mapping ───────────────────────────────────────────────

_PLOVER_QUADCLASS: dict[str, QuadClass] = {
    "AGREE": QuadClass.VERBAL_COOPERATION,
    "AID": QuadClass.MATERIAL_COOPERATION,
    "ARREST": QuadClass.MATERIAL_CONFLICT,
    "ASSAULT": QuadClass.MATERIAL_CONFLICT,
    "CONSULT": QuadClass.VERBAL_COOPERATION,
    "COOPERATE": QuadClass.MATERIAL_COOPERATION,
    "COERCE": QuadClass.MATERIAL_CONFLICT,
    "DEMAND": QuadClass.VERBAL_CONFLICT,
    "DISAPPROVE": QuadClass.VERBAL_CONFLICT,
    "MOBILIZE": QuadClass.MATERIAL_CONFLICT,
    "PROTEST": QuadClass.MATERIAL_CONFLICT,
    "REJECT": QuadClass.VERBAL_CONFLICT,
    "RETREAT": QuadClass.MATERIAL_COOPERATION,
    "RESTRICT": QuadClass.MATERIAL_CONFLICT,
    "SANCTION": QuadClass.MATERIAL_CONFLICT,
    "THREATEN": QuadClass.VERBAL_CONFLICT,
}

_EVENT_TYPE_TO_QUADCLASS: dict[EventType, QuadClass] = {
    _PLOVER_TO_DIALECTICA[code]: qc for code, qc in _PLOVER_QUADCLASS.items()
}

# ─── PLOVER mode → ACO severity nuances ─────────────────────────────────────

_PLOVER_MODE_SEVERITY: dict[str, float] = {
    # PROTEST modes
    "PROTEST:peaceful": 0.3,
    "PROTEST:march": 0.4,
    "PROTEST:strike": 0.5,
    "PROTEST:riot": 0.8,
    # ASSAULT modes
    "ASSAULT:attack": 0.7,
    "ASSAULT:bombing": 0.9,
    "ASSAULT:massacre": 1.0,
    "ASSAULT:shelling": 0.85,
    # COERCE modes
    "COERCE:blockade": 0.6,
    "COERCE:occupation": 0.7,
    "COERCE:detention": 0.5,
    # THREATEN modes
    "THREATEN:ultimatum": 0.6,
    "THREATEN:nuclear": 0.9,
    # SANCTION modes
    "SANCTION:economic": 0.5,
    "SANCTION:military": 0.7,
    "SANCTION:diplomatic": 0.4,
}

# Default severity by base type
_DEFAULT_SEVERITY: dict[str, float] = {
    "AGREE": 0.1,
    "AID": 0.1,
    "ARREST": 0.5,
    "ASSAULT": 0.8,
    "CONSULT": 0.1,
    "COOPERATE": 0.1,
    "COERCE": 0.6,
    "DEMAND": 0.3,
    "DISAPPROVE": 0.2,
    "MOBILIZE": 0.5,
    "PROTEST": 0.4,
    "REJECT": 0.3,
    "RETREAT": 0.2,
    "RESTRICT": 0.4,
    "SANCTION": 0.5,
    "THREATEN": 0.5,
}


# ─── Public API ──────────────────────────────────────────────────────────────


def plover_to_dialectica(plover_code: str) -> EventType:
    """Convert a PLOVER event code to a DIALECTICA EventType.

    Args:
        plover_code: PLOVER event code string (e.g. "AGREE", "ASSAULT").
            Case-insensitive.

    Returns:
        Matching DIALECTICA EventType.

    Raises:
        KeyError: If the PLOVER code is not recognised.
    """
    key = plover_code.strip().upper()
    if key not in _PLOVER_TO_DIALECTICA:
        raise KeyError(f"Unknown PLOVER event code: {plover_code!r}")
    return _PLOVER_TO_DIALECTICA[key]


def dialectica_to_plover(event_type: EventType) -> str:
    """Convert a DIALECTICA EventType to its PLOVER event code."""
    if event_type not in _DIALECTICA_TO_PLOVER:
        raise KeyError(f"No PLOVER mapping for EventType: {event_type!r}")
    return _DIALECTICA_TO_PLOVER[event_type]


def plover_quadclass(plover_code: str) -> QuadClass:
    """Return the PLOVER QuadClass for a given PLOVER event code."""
    key = plover_code.strip().upper()
    if key not in _PLOVER_QUADCLASS:
        raise KeyError(f"Unknown PLOVER event code: {plover_code!r}")
    return _PLOVER_QUADCLASS[key]


def event_type_quadclass(event_type: EventType) -> QuadClass:
    """Return the PLOVER QuadClass for a DIALECTICA EventType."""
    if event_type not in _EVENT_TYPE_TO_QUADCLASS:
        raise KeyError(f"No QuadClass mapping for EventType: {event_type!r}")
    return _EVENT_TYPE_TO_QUADCLASS[event_type]


def plover_severity(plover_code: str, mode: str | None = None) -> float:
    """Get ACO severity for a PLOVER event, optionally with mode nuance.

    Args:
        plover_code: PLOVER event type (e.g., "PROTEST").
        mode: Optional sub-mode (e.g., "riot", "peaceful").

    Returns:
        Severity float between 0.0 and 1.0.
    """
    key = plover_code.strip().upper()
    if mode:
        mode_key = f"{key}:{mode.lower()}"
        if mode_key in _PLOVER_MODE_SEVERITY:
            return _PLOVER_MODE_SEVERITY[mode_key]
    return _DEFAULT_SEVERITY.get(key, 0.5)


def plover_to_primitives(
    plover_code: str,
    mode: str | None = None,
    performer: str = "",
    target: str = "",
    description: str = "",
) -> dict:
    """Convert a PLOVER event to ACO Event node fields.

    Returns dict ready for Event(**result) construction.
    """
    event_type = plover_to_dialectica(plover_code)
    severity = plover_severity(plover_code, mode)

    return {
        "event_type": event_type.value,
        "severity": severity,
        "description": description or f"{plover_code} event",
        "performer_id": performer,
        "target_id": target,
        "source_text": f"PLOVER:{plover_code}" + (f":{mode}" if mode else ""),
    }
