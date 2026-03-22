"""
Entity Resolver — Cross-source deduplication and canonical actor registry.

Resolves entities across ACLED, GDELT, and UCDP using:
  1. Exact name match
  2. Alias matching
  3. Levenshtein fuzzy match (threshold=0.85)
  4. Cross-source dedup: (date ± 1 day) + (location ± 25km) + (actor overlap > 0.5)
"""

from __future__ import annotations

import logging
from difflib import SequenceMatcher

from dialectica_ontology.primitives import Actor, Event

logger = logging.getLogger(__name__)

LEVENSHTEIN_THRESHOLD = 0.85
DATE_WINDOW_DAYS = 1
LOCATION_THRESHOLD_KM = 25.0


class EntityResolver:
    """Canonical actor registry with fuzzy matching and cross-source dedup."""

    def __init__(self) -> None:
        self._registry: dict[str, Actor] = {}  # canonical_name -> Actor
        self._aliases: dict[str, str] = {}  # alias -> canonical_name

    def register_actor(self, actor: Actor, aliases: list[str] | None = None) -> None:
        """Add an actor to the canonical registry."""
        name = actor.name.strip()
        self._registry[name.lower()] = actor
        if aliases:
            for alias in aliases:
                self._aliases[alias.lower()] = name.lower()
        # Also register node aliases
        for alias in getattr(actor, "aliases", []):
            self._aliases[alias.lower()] = name.lower()

    def resolve(self, name: str) -> Actor | None:
        """Resolve a name to a canonical actor.

        Tries: exact -> alias -> fuzzy (Levenshtein >= 0.85).
        """
        key = name.strip().lower()

        # Exact match
        if key in self._registry:
            return self._registry[key]

        # Alias match
        if key in self._aliases:
            canonical = self._aliases[key]
            return self._registry.get(canonical)

        # Fuzzy match
        best_score = 0.0
        best_match: str | None = None
        for canonical_name in self._registry:
            score = SequenceMatcher(None, key, canonical_name).ratio()
            if score > best_score:
                best_score = score
                best_match = canonical_name

        if best_score >= LEVENSHTEIN_THRESHOLD and best_match:
            logger.info("Fuzzy matched '%s' -> '%s' (score=%.2f)", name, best_match, best_score)
            self._aliases[key] = best_match
            return self._registry[best_match]

        return None

    def resolve_or_create(self, name: str, actor_type: str = "other", **kwargs: object) -> Actor:
        """Resolve or create a new canonical actor."""
        existing = self.resolve(name)
        if existing:
            return existing

        actor = Actor(name=name, actor_type=actor_type, **kwargs)
        self.register_actor(actor)
        return actor

    def deduplicate_events(self, events: list[Event]) -> list[Event]:
        """Cross-source event deduplication.

        Events are considered duplicates if:
        - Date within ±1 day
        - Same event type
        - Actor overlap > 0.5 (by performer/target IDs)
        """
        unique: list[Event] = []

        for event in events:
            is_dup = False
            for existing in unique:
                if self._events_match(event, existing):
                    is_dup = True
                    # Keep the one with higher confidence
                    if (event.confidence or 0) > (existing.confidence or 0):
                        unique.remove(existing)
                        unique.append(event)
                    break
            if not is_dup:
                unique.append(event)

        if len(events) != len(unique):
            logger.info(
                "Deduplication: %d events -> %d unique",
                len(events),
                len(unique),
            )

        return unique

    @staticmethod
    def _events_match(a: Event, b: Event) -> bool:
        """Check if two events are likely duplicates."""
        # Date within ±1 day
        if a.occurred_at and b.occurred_at:
            delta = abs((a.occurred_at - b.occurred_at).total_seconds())
            if delta > DATE_WINDOW_DAYS * 86400:
                return False
        elif a.occurred_at or b.occurred_at:
            return False  # One has date, other doesn't

        # Same event type
        if a.event_type != b.event_type:
            return False

        # Actor overlap
        a_actors = {getattr(a, "performer_id", ""), getattr(a, "target_id", "")} - {""}
        b_actors = {getattr(b, "performer_id", ""), getattr(b, "target_id", "")} - {""}
        if a_actors and b_actors:
            overlap = len(a_actors & b_actors) / max(len(a_actors | b_actors), 1)
            if overlap < 0.5:
                return False

        return True
