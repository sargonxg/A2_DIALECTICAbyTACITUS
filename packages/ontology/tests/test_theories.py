"""Tests for dialectica_ontology.theory — Theory framework implementations."""

from dialectica_ontology.theory.base import TheoryFramework
from dialectica_ontology.theory.glasl import GlaslFramework
from dialectica_ontology.theory.fisher_ury import FisherUryFramework
from dialectica_ontology.theory.kriesberg import KriesbergFramework
from dialectica_ontology.theory.galtung import GaltungFramework
from dialectica_ontology.theory.lederach import LederachFramework
from dialectica_ontology.theory.zartman import ZartmanFramework
from dialectica_ontology.theory.deutsch import DeutschFramework


# ─── Base framework ─────────────────────────────────────────────────────────

def test_framework_base_is_abstract():
    """TheoryFramework should define the interface."""
    assert hasattr(TheoryFramework, "describe")
    assert hasattr(TheoryFramework, "assess")
    assert hasattr(TheoryFramework, "score")


# ─── Glasl ───────────────────────────────────────────────────────────────────

def test_glasl_framework_creation():
    g = GlaslFramework()
    assert g.name == "Glasl Escalation Model"
    assert "9" in g.describe() or "nine" in g.describe().lower() or "escalation" in g.describe().lower()


def test_glasl_recommend_intervention():
    g = GlaslFramework()
    assert "moderation" in g.recommend_intervention(1).lower() or "facilitation" in g.recommend_intervention(1).lower()
    assert "mediation" in g.recommend_intervention(5).lower()
    assert "power" in g.recommend_intervention(9).lower()


def test_glasl_stage_detection():
    g = GlaslFramework()
    stage = g.detect_stage({"polarization": 0.8, "violence": 0.9})
    assert 1 <= stage <= 9


def test_glasl_assess():
    g = GlaslFramework()
    result = g.assess({"glasl_stage": 7})
    assert isinstance(result, dict)


def test_glasl_score():
    g = GlaslFramework()
    s = g.score({"glasl_stage": 7})
    assert 0.0 <= s <= 1.0


# ─── Fisher/Ury ─────────────────────────────────────────────────────────────

def test_fisher_ury_creation():
    f = FisherUryFramework()
    assert "Fisher" in f.name or "Interest" in f.name


def test_fisher_ury_zopa():
    f = FisherUryFramework()
    zopa = f.compute_zopa(100.0, 120.0)
    assert zopa is not None
    assert zopa >= 0


def test_fisher_ury_no_zopa():
    f = FisherUryFramework()
    zopa = f.compute_zopa(150.0, 100.0)
    assert zopa is None or zopa < 0


def test_fisher_ury_assess():
    f = FisherUryFramework()
    result = f.assess({})
    assert isinstance(result, dict)


# ─── Kriesberg ───────────────────────────────────────────────────────────────

def test_kriesberg_creation():
    k = KriesbergFramework()
    assert "Kriesberg" in k.name or "lifecycle" in k.name.lower()


def test_kriesberg_assess():
    k = KriesbergFramework()
    result = k.assess({"phase": "escalating"})
    assert isinstance(result, dict)


# ─── Galtung ────────────────────────────────────────────────────────────────

def test_galtung_creation():
    g = GaltungFramework()
    assert "Galtung" in g.name or "violence" in g.name.lower()


def test_galtung_assess():
    g = GaltungFramework()
    result = g.assess({})
    assert isinstance(result, dict)


# ─── Lederach ───────────────────────────────────────────────────────────────

def test_lederach_creation():
    l = LederachFramework()
    assert "Lederach" in l.name or "nested" in l.name.lower()


# ─── Zartman ────────────────────────────────────────────────────────────────

def test_zartman_creation():
    z = ZartmanFramework()
    assert "Zartman" in z.name or "ripeness" in z.name.lower()


def test_zartman_ripeness():
    z = ZartmanFramework()
    result = z.assess({"stalemate": True, "pain": 0.8})
    assert isinstance(result, dict)


# ─── Deutsch ────────────────────────────────────────────────────────────────

def test_deutsch_creation():
    d = DeutschFramework()
    assert "Deutsch" in d.name or "cooperation" in d.name.lower()
