"""
CAMEO Compatibility — Bidirectional mapping between DIALECTICA and CAMEO coding.

Maps DIALECTICA EventType/node types to CAMEO codes and vice versa.
Used for data import/export and interoperability with existing conflict databases.

CAMEO (Conflict and Mediation Event Observations) defines actor codes and a
hierarchical event code system (top-level 01-20).
"""

from __future__ import annotations

from dialectica_ontology.enums import ActorType, EventType

# ─── CAMEO actor codes -> DIALECTICA ActorType ───────────────────────────────

_CAMEO_ACTOR_TO_DIALECTICA: dict[str, ActorType] = {
    "GOV": ActorType.STATE,
    "MIL": ActorType.STATE,
    "REB": ActorType.ORGANIZATION,
    "OPP": ActorType.ORGANIZATION,
    "PTY": ActorType.ORGANIZATION,
    "JUD": ActorType.STATE,
    "SPY": ActorType.STATE,
    "IGO": ActorType.COALITION,
    "NGO": ActorType.ORGANIZATION,
    "IMG": ActorType.COALITION,
    "MNC": ActorType.ORGANIZATION,
    "EDU": ActorType.ORGANIZATION,
    "BUS": ActorType.ORGANIZATION,
    "MED": ActorType.ORGANIZATION,
    "REL": ActorType.ORGANIZATION,
    "CVL": ActorType.PERSON,
    "LAB": ActorType.INFORMAL_GROUP,
    "CRM": ActorType.INFORMAL_GROUP,
    "REF": ActorType.INFORMAL_GROUP,
    "MOD": ActorType.INFORMAL_GROUP,
    "RAD": ActorType.INFORMAL_GROUP,
    "SET": ActorType.INFORMAL_GROUP,
    "UAF": ActorType.INFORMAL_GROUP,
    "AGR": ActorType.INFORMAL_GROUP,
    "HLH": ActorType.ORGANIZATION,
    "LEG": ActorType.STATE,
    "ELI": ActorType.PERSON,
    "COP": ActorType.STATE,
}

# Reverse mapping: one DIALECTICA ActorType -> list of CAMEO codes
_DIALECTICA_TO_CAMEO_ACTOR: dict[ActorType, list[str]] = {}
for _code, _actor_type in _CAMEO_ACTOR_TO_DIALECTICA.items():
    _DIALECTICA_TO_CAMEO_ACTOR.setdefault(_actor_type, []).append(_code)

# ─── CAMEO event codes (top-level) -> DIALECTICA EventType ──────────────────

# CAMEO top-level event codes (01-20) with their primary label.
_CAMEO_EVENT_TO_DIALECTICA: dict[str, EventType] = {
    "01": EventType.AGREE,  # Make public statement
    "02": EventType.SUPPORT,  # Appeal
    "03": EventType.COOPERATE,  # Express intent to cooperate
    "04": EventType.CONSULT,  # Consult
    "05": EventType.COOPERATE,  # Engage in diplomatic cooperation
    "06": EventType.COOPERATE,  # Engage in material cooperation
    "07": EventType.AID,  # Provide aid
    "08": EventType.YIELD,  # Yield
    "09": EventType.INVESTIGATE,  # Investigate
    "10": EventType.DEMAND,  # Demand
    "11": EventType.DISAPPROVE,  # Disapprove
    "12": EventType.REJECT,  # Reject
    "13": EventType.THREATEN,  # Threaten
    "14": EventType.PROTEST,  # Protest
    "15": EventType.EXHIBIT_FORCE_POSTURE,  # Exhibit military posture
    "16": EventType.REDUCE_RELATIONS,  # Reduce relations
    "17": EventType.COERCE,  # Coerce
    "18": EventType.ASSAULT,  # Assault
    "19": EventType.ASSAULT,  # Fight
    "20": EventType.ASSAULT,  # Engage in unconventional mass violence
}

# Reverse mapping: DIALECTICA EventType -> list of CAMEO event codes
_DIALECTICA_TO_CAMEO_EVENT: dict[EventType, list[str]] = {}
for _code, _etype in _CAMEO_EVENT_TO_DIALECTICA.items():
    _DIALECTICA_TO_CAMEO_EVENT.setdefault(_etype, []).append(_code)


# ─── Public API ──────────────────────────────────────────────────────────────


def cameo_to_dialectica(cameo_code: str) -> ActorType:
    """Convert a CAMEO actor code to a DIALECTICA ActorType.

    Args:
        cameo_code: CAMEO actor code string (e.g. ``"GOV"``, ``"MIL"``).
            Case-insensitive.

    Returns:
        Matching DIALECTICA ``ActorType``.

    Raises:
        KeyError: If the CAMEO code is not recognised.
    """
    key = cameo_code.strip().upper()
    if key not in _CAMEO_ACTOR_TO_DIALECTICA:
        raise KeyError(f"Unknown CAMEO actor code: {cameo_code!r}")
    return _CAMEO_ACTOR_TO_DIALECTICA[key]


def dialectica_to_cameo(actor_type: ActorType) -> list[str]:
    """Convert a DIALECTICA ActorType to a list of matching CAMEO actor codes.

    Args:
        actor_type: A ``ActorType`` enum member.

    Returns:
        List of CAMEO actor code strings that map to this DIALECTICA type.

    Raises:
        KeyError: If the actor type has no CAMEO equivalent.
    """
    if actor_type not in _DIALECTICA_TO_CAMEO_ACTOR:
        raise KeyError(f"No CAMEO mapping for ActorType: {actor_type!r}")
    return _DIALECTICA_TO_CAMEO_ACTOR[actor_type]


def cameo_event_to_dialectica(cameo_event_code: str) -> EventType:
    """Convert a CAMEO event code to a DIALECTICA EventType.

    Accepts both top-level codes (``"01"``-``"20"``) and detailed codes
    (e.g. ``"0831"``); the top two digits are used for the mapping.

    Args:
        cameo_event_code: CAMEO event code string.

    Returns:
        Matching DIALECTICA ``EventType``.

    Raises:
        KeyError: If the CAMEO event code is not recognised.
    """
    # Extract top-level code (first two digits)
    code = cameo_event_code.strip()
    top_level = code[:2].zfill(2)
    if top_level not in _CAMEO_EVENT_TO_DIALECTICA:
        raise KeyError(f"Unknown CAMEO event code: {cameo_event_code!r}")
    return _CAMEO_EVENT_TO_DIALECTICA[top_level]


def dialectica_to_cameo_event(event_type: EventType) -> list[str]:
    """Convert a DIALECTICA EventType to a list of CAMEO top-level event codes.

    Args:
        event_type: A ``EventType`` enum member.

    Returns:
        List of CAMEO top-level event code strings (e.g. ``["18", "19", "20"]``).

    Raises:
        KeyError: If the event type has no CAMEO equivalent.
    """
    if event_type not in _DIALECTICA_TO_CAMEO_EVENT:
        raise KeyError(f"No CAMEO mapping for EventType: {event_type!r}")
    return _DIALECTICA_TO_CAMEO_EVENT[event_type]
