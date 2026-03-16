"""Theory frameworks package — 15 conflict resolution theory implementations."""

from dialectica_ontology.theory.base import (
    ConflictSnapshot,
    DiagnosticQuestion,
    Intervention,
    TheoryAssessment,
    TheoryConcept,
    TheoryFramework,
)
from dialectica_ontology.theory.glasl import GlaslFramework
from dialectica_ontology.theory.fisher_ury import FisherUryFramework
from dialectica_ontology.theory.kriesberg import KriesbergFramework
from dialectica_ontology.theory.galtung import GaltungFramework
from dialectica_ontology.theory.lederach import LederachFramework
from dialectica_ontology.theory.zartman import ZartmanFramework
from dialectica_ontology.theory.deutsch import DeutschFramework
from dialectica_ontology.theory.thomas_kilmann import ThomasKilmannFramework
from dialectica_ontology.theory.french_raven import FrenchRavenFramework
from dialectica_ontology.theory.mayer_trust import MayerTrustFramework
from dialectica_ontology.theory.plutchik import PlutchikFramework
from dialectica_ontology.theory.pearl_causal import PearlCausalFramework
from dialectica_ontology.theory.winslade_monk import WinsladeMonkFramework
from dialectica_ontology.theory.ury_brett_goldberg import UryBrettGoldbergFramework
from dialectica_ontology.theory.burton import BurtonFramework

__all__ = [
    "TheoryFramework",
    "TheoryConcept",
    "ConflictSnapshot",
    "TheoryAssessment",
    "Intervention",
    "DiagnosticQuestion",
    "GlaslFramework",
    "FisherUryFramework",
    "KriesbergFramework",
    "GaltungFramework",
    "LederachFramework",
    "ZartmanFramework",
    "DeutschFramework",
    "ThomasKilmannFramework",
    "FrenchRavenFramework",
    "MayerTrustFramework",
    "PlutchikFramework",
    "PearlCausalFramework",
    "WinsladeMonkFramework",
    "UryBrettGoldbergFramework",
    "BurtonFramework",
]
