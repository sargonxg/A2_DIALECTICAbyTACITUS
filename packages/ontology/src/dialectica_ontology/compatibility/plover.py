"""
PLOVER Compatibility — Bidirectional mapping between DIALECTICA and PLOVER coding.

Maps DIALECTICA EventType/node types to PLOVER codes and vice versa.
Used for data import/export and interoperability with existing conflict databases.

PLOVER (Political Language Ontology for Verifiable Event Records) defines
16 top-level event types and a QuadClass classification.
"""
from __future__ import annotations

from dialectica_ontology.enums import EventType, QuadClass


# ─── PLOVER event code <-> DIALECTICA EventType ─────────────────────────────

# PLOVER uses uppercase string codes that map 1:1 to DIALECTICA EventType
_PLOVER_TO_DIALECTICA: dict[str, EventType] = {
    "AGREE": EventType.AGREE,
    "CONSULT": EventType.CONSULT,
    "SUPPORT": EventType.SUPPORT,
    "COOPERATE": EventType.COOPERATE,
    "AID": EventType.AID,
    "YIELD": EventType.YIELD,
    "INVESTIGATE": EventType.INVESTIGATE,
    "DEMAND": EventType.DEMAND,
    "DISAPPROVE": EventType.DISAPPROVE,
    "REJECT": EventType.REJECT,
    "THREATEN": EventType.THREATEN,
    "PROTEST": EventType.PROTEST,
    "EXHIBIT_FORCE_POSTURE": EventType.EXHIBIT_FORCE_POSTURE,
    "REDUCE_RELATIONS": EventType.REDUCE_RELATIONS,
    "COERCE": EventType.COERCE,
    "ASSAULT": EventType.ASSAULT,
}

_DIALECTICA_TO_PLOVER: dict[EventType, str] = {v: k for k, v in _PLOVER_TO_DIALECTICA.items()}

# ─── PLOVER QuadClass mapping ───────────────────────────────────────────────

# Each PLOVER event type belongs to one of four quadrants.
_PLOVER_QUADCLASS: dict[str, QuadClass] = {
    "AGREE": QuadClass.VERBAL_COOPERATION,
    "CONSULT": QuadClass.VERBAL_COOPERATION,
    "SUPPORT": QuadClass.VERBAL_COOPERATION,
    "COOPERATE": QuadClass.MATERIAL_COOPERATION,
    "AID": QuadClass.MATERIAL_COOPERATION,
    "YIELD": QuadClass.MATERIAL_COOPERATION,
    "INVESTIGATE": QuadClass.VERBAL_COOPERATION,
    "DEMAND": QuadClass.VERBAL_CONFLICT,
    "DISAPPROVE": QuadClass.VERBAL_CONFLICT,
    "REJECT": QuadClass.VERBAL_CONFLICT,
    "THREATEN": QuadClass.VERBAL_CONFLICT,
    "PROTEST": QuadClass.MATERIAL_CONFLICT,
    "EXHIBIT_FORCE_POSTURE": QuadClass.MATERIAL_CONFLICT,
    "REDUCE_RELATIONS": QuadClass.MATERIAL_CONFLICT,
    "COERCE": QuadClass.MATERIAL_CONFLICT,
    "ASSAULT": QuadClass.MATERIAL_CONFLICT,
}

_EVENT_TYPE_TO_QUADCLASS: dict[EventType, QuadClass] = {
    _PLOVER_TO_DIALECTICA[code]: qc for code, qc in _PLOVER_QUADCLASS.items()
}


# ─── Public API ──────────────────────────────────────────────────────────────

def plover_to_dialectica(plover_code: str) -> EventType:
    """Convert a PLOVER event code to a DIALECTICA EventType.

    Args:
        plover_code: PLOVER event code string (e.g. ``"AGREE"``, ``"ASSAULT"``).
            Case-insensitive.

    Returns:
        Matching DIALECTICA ``EventType``.

    Raises:
        KeyError: If the PLOVER code is not recognised.
    """
    key = plover_code.strip().upper()
    if key not in _PLOVER_TO_DIALECTICA:
        raise KeyError(f"Unknown PLOVER event code: {plover_code!r}")
    return _PLOVER_TO_DIALECTICA[key]


def dialectica_to_plover(event_type: EventType) -> str:
    """Convert a DIALECTICA EventType to its PLOVER event code.

    Args:
        event_type: A ``EventType`` enum member.

    Returns:
        The corresponding PLOVER uppercase code string.

    Raises:
        KeyError: If the event type has no PLOVER equivalent.
    """
    if event_type not in _DIALECTICA_TO_PLOVER:
        raise KeyError(f"No PLOVER mapping for EventType: {event_type!r}")
    return _DIALECTICA_TO_PLOVER[event_type]


def plover_quadclass(plover_code: str) -> QuadClass:
    """Return the PLOVER QuadClass for a given PLOVER event code.

    Args:
        plover_code: PLOVER event code string. Case-insensitive.

    Returns:
        The ``QuadClass`` that the event code belongs to.

    Raises:
        KeyError: If the PLOVER code is not recognised.
    """
    key = plover_code.strip().upper()
    if key not in _PLOVER_QUADCLASS:
        raise KeyError(f"Unknown PLOVER event code: {plover_code!r}")
    return _PLOVER_QUADCLASS[key]


def event_type_quadclass(event_type: EventType) -> QuadClass:
    """Return the PLOVER QuadClass for a DIALECTICA EventType.

    Args:
        event_type: A ``EventType`` enum member.

    Returns:
        The ``QuadClass`` that the event type maps to.

    Raises:
        KeyError: If the event type has no QuadClass mapping.
    """
    if event_type not in _EVENT_TYPE_TO_QUADCLASS:
        raise KeyError(f"No QuadClass mapping for EventType: {event_type!r}")
    return _EVENT_TYPE_TO_QUADCLASS[event_type]
