"""
UCDP Compatibility — Bidirectional mapping between DIALECTICA and UCDP coding.

Maps DIALECTICA EventType/node types to UCDP codes and vice versa.
Used for data import/export and interoperability with existing conflict databases.

UCDP (Uppsala Conflict Data Program) classifies armed conflicts by
incompatibility type, intensity level, and conflict type.
"""

from __future__ import annotations

from dialectica_ontology.enums import (
    ConflictDomain,
    Incompatibility,
    Intensity,
    ViolenceType,
)

# ─── UCDP incompatibility type -> DIALECTICA Incompatibility ────────────────

_UCDP_INCOMPATIBILITY_TO_DIALECTICA: dict[str, Incompatibility] = {
    "government": Incompatibility.GOVERNMENT,
    "territory": Incompatibility.TERRITORY,
    "government, territory": Incompatibility.GOVERNMENT,  # dual-coded, primary is govt
}

_DIALECTICA_TO_UCDP_INCOMPATIBILITY: dict[Incompatibility, str] = {
    Incompatibility.GOVERNMENT: "government",
    Incompatibility.TERRITORY: "territory",
    # The remaining Incompatibility values (RESOURCE, RIGHTS, RELATIONSHIP,
    # IDENTITY) extend beyond UCDP's binary classification.
}


# ─── UCDP intensity thresholds -> DIALECTICA Intensity ──────────────────────

# UCDP defines:
#   minor conflict: 25-999 battle-related deaths per calendar year
#   war: 1000+ battle-related deaths per calendar year
_UCDP_INTENSITY_THRESHOLDS: list[tuple[int, Intensity]] = [
    (0, Intensity.LOW),  # Below UCDP threshold (< 25)
    (25, Intensity.MODERATE),  # UCDP minor conflict
    (100, Intensity.HIGH),  # Upper minor conflict
    (1000, Intensity.SEVERE),  # UCDP war threshold
    (10000, Intensity.EXTREME),  # Major war
]


# ─── UCDP conflict type -> DIALECTICA mappings ──────────────────────────────

# UCDP type_of_violence codes:
#   1 = state-based conflict
#   2 = non-state conflict
#   3 = one-sided violence
_UCDP_CONFLICT_TYPE_TO_DOMAIN: dict[int, ConflictDomain] = {
    1: ConflictDomain.ARMED,
    2: ConflictDomain.ARMED,
    3: ConflictDomain.ARMED,
}

_UCDP_CONFLICT_TYPE_TO_VIOLENCE: dict[int, ViolenceType] = {
    1: ViolenceType.DIRECT,
    2: ViolenceType.DIRECT,
    3: ViolenceType.DIRECT,
}

_UCDP_CONFLICT_TYPE_LABELS: dict[int, str] = {
    1: "state-based armed conflict",
    2: "non-state conflict",
    3: "one-sided violence",
}


# ─── Public API ──────────────────────────────────────────────────────────────


def ucdp_to_dialectica_incompatibility(ucdp_type: str) -> Incompatibility:
    """Convert a UCDP incompatibility type to a DIALECTICA Incompatibility.

    Args:
        ucdp_type: UCDP incompatibility string (``"government"``,
            ``"territory"``, or ``"government, territory"``).
            Case-insensitive.

    Returns:
        Matching DIALECTICA ``Incompatibility``.

    Raises:
        KeyError: If the UCDP type is not recognised.
    """
    key = ucdp_type.strip().lower()
    if key not in _UCDP_INCOMPATIBILITY_TO_DIALECTICA:
        raise KeyError(f"Unknown UCDP incompatibility type: {ucdp_type!r}")
    return _UCDP_INCOMPATIBILITY_TO_DIALECTICA[key]


def dialectica_to_ucdp_incompatibility(incompatibility: Incompatibility) -> str:
    """Convert a DIALECTICA Incompatibility to a UCDP incompatibility string.

    Only ``GOVERNMENT`` and ``TERRITORY`` have direct UCDP equivalents.

    Args:
        incompatibility: A ``Incompatibility`` enum member.

    Returns:
        UCDP incompatibility type string.

    Raises:
        KeyError: If the incompatibility has no UCDP equivalent.
    """
    if incompatibility not in _DIALECTICA_TO_UCDP_INCOMPATIBILITY:
        raise KeyError(
            f"No UCDP mapping for Incompatibility: {incompatibility!r}. "
            f"UCDP only codes 'government' and 'territory'."
        )
    return _DIALECTICA_TO_UCDP_INCOMPATIBILITY[incompatibility]


def ucdp_to_dialectica_intensity(battle_deaths: int) -> Intensity:
    """Convert a UCDP battle-death count to a DIALECTICA Intensity level.

    Uses UCDP thresholds:
    - < 25: LOW (below UCDP coding threshold)
    - 25-99: MODERATE (UCDP minor conflict)
    - 100-999: HIGH (upper minor conflict)
    - 1000-9999: SEVERE (UCDP war)
    - 10000+: EXTREME (major war)

    Args:
        battle_deaths: Number of battle-related deaths in a calendar year.

    Returns:
        Matching DIALECTICA ``Intensity``.

    Raises:
        ValueError: If battle_deaths is negative.
    """
    if battle_deaths < 0:
        raise ValueError(f"battle_deaths must be non-negative, got {battle_deaths}")
    result = Intensity.LOW
    for threshold, intensity in _UCDP_INTENSITY_THRESHOLDS:
        if battle_deaths >= threshold:
            result = intensity
        else:
            break
    return result


def ucdp_conflict_type_to_domain(type_of_violence: int) -> ConflictDomain:
    """Convert a UCDP type_of_violence code to a DIALECTICA ConflictDomain.

    Args:
        type_of_violence: UCDP violence type code (1=state-based,
            2=non-state, 3=one-sided).

    Returns:
        Matching DIALECTICA ``ConflictDomain``.

    Raises:
        KeyError: If the code is not recognised.
    """
    if type_of_violence not in _UCDP_CONFLICT_TYPE_TO_DOMAIN:
        raise KeyError(f"Unknown UCDP type_of_violence: {type_of_violence!r}. Expected 1, 2, or 3.")
    return _UCDP_CONFLICT_TYPE_TO_DOMAIN[type_of_violence]


def ucdp_conflict_type_to_violence(type_of_violence: int) -> ViolenceType:
    """Convert a UCDP type_of_violence code to a DIALECTICA ViolenceType.

    Args:
        type_of_violence: UCDP violence type code (1, 2, or 3).

    Returns:
        Matching DIALECTICA ``ViolenceType`` (always ``DIRECT`` for UCDP).

    Raises:
        KeyError: If the code is not recognised.
    """
    if type_of_violence not in _UCDP_CONFLICT_TYPE_TO_VIOLENCE:
        raise KeyError(f"Unknown UCDP type_of_violence: {type_of_violence!r}. Expected 1, 2, or 3.")
    return _UCDP_CONFLICT_TYPE_TO_VIOLENCE[type_of_violence]


def ucdp_conflict_type_label(type_of_violence: int) -> str:
    """Return a human-readable label for a UCDP type_of_violence code.

    Args:
        type_of_violence: UCDP violence type code (1, 2, or 3).

    Returns:
        Human-readable string label.

    Raises:
        KeyError: If the code is not recognised.
    """
    if type_of_violence not in _UCDP_CONFLICT_TYPE_LABELS:
        raise KeyError(f"Unknown UCDP type_of_violence: {type_of_violence!r}. Expected 1, 2, or 3.")
    return _UCDP_CONFLICT_TYPE_LABELS[type_of_violence]
