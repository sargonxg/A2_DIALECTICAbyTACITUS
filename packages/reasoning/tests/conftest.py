"""Shared fixtures for reasoning tests — JCPOA and HR mediation data."""

from __future__ import annotations

import os

import pytest

from dialectica_ontology.primitives import Actor, Conflict, Event

SEED_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "seed", "samples")


@pytest.fixture
def jcpoa_actors():
    """Core JCPOA actors."""
    return [
        Actor(name="Iran", actor_type="state"),
        Actor(name="United States", actor_type="state"),
        Actor(name="IAEA", actor_type="organization"),
        Actor(name="European Union", actor_type="organization"),
        Actor(name="Russia", actor_type="state"),
        Actor(name="China", actor_type="state"),
    ]


@pytest.fixture
def jcpoa_conflict():
    return Conflict(
        name="JCPOA Nuclear Agreement",
        scale="macro",
        domain="geopolitical",
        status="active",
    )


@pytest.fixture
def jcpoa_events():
    from datetime import datetime

    return [
        Event(
            event_type="agree",
            severity=0.1,
            occurred_at=datetime(2015, 7, 14),
            description="JCPOA signed",
        ),
        Event(
            event_type="reject",
            severity=0.6,
            occurred_at=datetime(2018, 5, 8),
            description="US withdraws from JCPOA",
        ),
        Event(
            event_type="coerce",
            severity=0.7,
            occurred_at=datetime(2018, 11, 5),
            description="US reimposesall sanctions",
        ),
        Event(
            event_type="protest",
            severity=0.4,
            occurred_at=datetime(2019, 5, 8),
            description="Iran reduces compliance",
        ),
    ]


@pytest.fixture
def hr_actors():
    return [
        Actor(name="Employee A", actor_type="person"),
        Actor(name="Manager B", actor_type="person"),
        Actor(name="HR Department", actor_type="organization"),
    ]


@pytest.fixture
def hr_conflict():
    return Conflict(
        name="Workplace Harassment Dispute",
        scale="micro",
        domain="workplace",
        status="active",
    )
