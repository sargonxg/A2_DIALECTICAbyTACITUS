"""
ACLED Compatibility — Bidirectional mapping between DIALECTICA and ACLED coding.

Maps DIALECTICA EventType/node types to ACLED codes and vice versa.
Used for data import/export and interoperability with existing conflict databases.

ACLED (Armed Conflict Location & Event Data) uses 6 top-level event types,
each with sub-event types, plus an actor type taxonomy.
"""
from __future__ import annotations

from dialectica_ontology.enums import ActorType, EventType


# ─── ACLED event type + sub-type -> DIALECTICA EventType ─────────────────────

# Keys are (event_type, sub_event_type) tuples from ACLED data.
# Where sub-type is empty string, the mapping applies to the top-level type.
_ACLED_TO_DIALECTICA: dict[tuple[str, str], EventType] = {
    # Battles
    ("Battles", "Armed clash"): EventType.ASSAULT,
    ("Battles", "Government regains territory"): EventType.ASSAULT,
    ("Battles", "Non-state actor overtakes territory"): EventType.ASSAULT,
    # Explosions / Remote violence
    ("Explosions/Remote violence", "Air/drone strike"): EventType.ASSAULT,
    ("Explosions/Remote violence", "Shelling/artillery/missile attack"): EventType.ASSAULT,
    ("Explosions/Remote violence", "Remote explosive/landmine/IED"): EventType.ASSAULT,
    ("Explosions/Remote violence", "Suicide bomb"): EventType.ASSAULT,
    # Violence against civilians
    ("Violence against civilians", "Violence against civilians"): EventType.COERCE,
    ("Violence against civilians", "Attack"): EventType.ASSAULT,
    ("Violence against civilians", "Abduction/forced disappearance"): EventType.COERCE,
    ("Violence against civilians", "Sexual violence"): EventType.ASSAULT,
    # Protests
    ("Protests", "Peaceful protest"): EventType.PROTEST,
    ("Protests", "Protest with intervention"): EventType.PROTEST,
    ("Protests", "Excessive force against protesters"): EventType.COERCE,
    # Riots
    ("Riots", "Violent demonstration"): EventType.PROTEST,
    ("Riots", "Mob violence"): EventType.ASSAULT,
    # Strategic developments
    ("Strategic developments", "Agreement"): EventType.AGREE,
    ("Strategic developments", "Arrests"): EventType.COERCE,
    ("Strategic developments", "Change to group/activity"): EventType.REDUCE_RELATIONS,
    ("Strategic developments", "Disrupted weapons use"): EventType.EXHIBIT_FORCE_POSTURE,
    ("Strategic developments", "Headquarters or base established"): EventType.EXHIBIT_FORCE_POSTURE,
    ("Strategic developments", "Looting/property destruction"): EventType.ASSAULT,
    ("Strategic developments", "Non-violent transfer of territory"): EventType.YIELD,
    ("Strategic developments", "Other"): EventType.INVESTIGATE,
}

# Reverse mapping: DIALECTICA EventType -> primary ACLED (type, sub_type).
# Uses the most representative ACLED category for each EventType.
_DIALECTICA_TO_ACLED: dict[EventType, tuple[str, str]] = {
    EventType.AGREE: ("Strategic developments", "Agreement"),
    EventType.CONSULT: ("Strategic developments", "Other"),
    EventType.SUPPORT: ("Strategic developments", "Other"),
    EventType.COOPERATE: ("Strategic developments", "Agreement"),
    EventType.AID: ("Strategic developments", "Other"),
    EventType.YIELD: ("Strategic developments", "Non-violent transfer of territory"),
    EventType.INVESTIGATE: ("Strategic developments", "Other"),
    EventType.DEMAND: ("Protests", "Peaceful protest"),
    EventType.DISAPPROVE: ("Protests", "Peaceful protest"),
    EventType.REJECT: ("Strategic developments", "Other"),
    EventType.THREATEN: ("Strategic developments", "Other"),
    EventType.PROTEST: ("Protests", "Peaceful protest"),
    EventType.EXHIBIT_FORCE_POSTURE: ("Strategic developments", "Headquarters or base established"),
    EventType.REDUCE_RELATIONS: ("Strategic developments", "Change to group/activity"),
    EventType.COERCE: ("Violence against civilians", "Violence against civilians"),
    EventType.ASSAULT: ("Battles", "Armed clash"),
}

# ─── ACLED actor type -> DIALECTICA ActorType ────────────────────────────────

_ACLED_ACTOR_TO_DIALECTICA: dict[str, ActorType] = {
    "State Forces": ActorType.STATE,
    "Rebel Groups": ActorType.ORGANIZATION,
    "Political Militias": ActorType.ORGANIZATION,
    "Identity Militias": ActorType.INFORMAL_GROUP,
    "Rioters": ActorType.INFORMAL_GROUP,
    "Protesters": ActorType.INFORMAL_GROUP,
    "Civilians": ActorType.PERSON,
    "External/Other Forces": ActorType.COALITION,
}

_DIALECTICA_ACTOR_TO_ACLED: dict[ActorType, list[str]] = {
    ActorType.PERSON: ["Civilians"],
    ActorType.ORGANIZATION: ["Rebel Groups", "Political Militias"],
    ActorType.STATE: ["State Forces"],
    ActorType.COALITION: ["External/Other Forces"],
    ActorType.INFORMAL_GROUP: ["Identity Militias", "Rioters", "Protesters"],
}


# ─── Public API ──────────────────────────────────────────────────────────────

def acled_to_dialectica(acled_event_type: str, acled_sub_type: str) -> EventType:
    """Convert an ACLED event type and sub-type to a DIALECTICA EventType.

    Args:
        acled_event_type: ACLED top-level event type (e.g. ``"Battles"``).
        acled_sub_type: ACLED sub-event type (e.g. ``"Armed clash"``).

    Returns:
        Matching DIALECTICA ``EventType``.

    Raises:
        KeyError: If the ACLED type/sub-type combination is not recognised.
    """
    key = (acled_event_type.strip(), acled_sub_type.strip())
    if key not in _ACLED_TO_DIALECTICA:
        raise KeyError(
            f"Unknown ACLED event: type={acled_event_type!r}, sub_type={acled_sub_type!r}"
        )
    return _ACLED_TO_DIALECTICA[key]


def dialectica_to_acled(event_type: EventType) -> tuple[str, str]:
    """Convert a DIALECTICA EventType to its primary ACLED event type and sub-type.

    Args:
        event_type: A ``EventType`` enum member.

    Returns:
        A ``(event_type, sub_event_type)`` tuple of ACLED strings.

    Raises:
        KeyError: If the event type has no ACLED equivalent.
    """
    if event_type not in _DIALECTICA_TO_ACLED:
        raise KeyError(f"No ACLED mapping for EventType: {event_type!r}")
    return _DIALECTICA_TO_ACLED[event_type]


def acled_actor_to_dialectica(acled_actor_type: str) -> ActorType:
    """Convert an ACLED actor type to a DIALECTICA ActorType.

    Args:
        acled_actor_type: ACLED actor type string (e.g. ``"State Forces"``).

    Returns:
        Matching DIALECTICA ``ActorType``.

    Raises:
        KeyError: If the ACLED actor type is not recognised.
    """
    key = acled_actor_type.strip()
    if key not in _ACLED_ACTOR_TO_DIALECTICA:
        raise KeyError(f"Unknown ACLED actor type: {acled_actor_type!r}")
    return _ACLED_ACTOR_TO_DIALECTICA[key]


def dialectica_actor_to_acled(actor_type: ActorType) -> list[str]:
    """Convert a DIALECTICA ActorType to a list of ACLED actor type strings.

    Args:
        actor_type: A ``ActorType`` enum member.

    Returns:
        List of ACLED actor type strings that map to this DIALECTICA type.

    Raises:
        KeyError: If the actor type has no ACLED equivalent.
    """
    if actor_type not in _DIALECTICA_ACTOR_TO_ACLED:
        raise KeyError(f"No ACLED mapping for ActorType: {actor_type!r}")
    return _DIALECTICA_ACTOR_TO_ACLED[actor_type]
