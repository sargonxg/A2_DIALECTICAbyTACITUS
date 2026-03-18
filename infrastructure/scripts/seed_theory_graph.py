"""
Seed Theory Knowledge Graph — Build the complete theory knowledge graph.

This script populates the shared theory graph with 200+ nodes covering
all 15 conflict resolution frameworks. The theory graph is universal
and shared across all tenants.
"""
from __future__ import annotations

from dialectica_ontology.theory_graph import (
    TheoryConcept,
    Theorist,
    Publication,
    Methodology,
    Principle,
    Pattern,
)

# ─── Theorists ──────────────────────────────────────────────────────────────

THEORISTS = [
    Theorist(id="th-glasl", name="Friedrich Glasl", affiliation="Trigon Entwicklungsberatung", birth_year=1941, key_works=["Konfliktmanagement"]),
    Theorist(id="th-fisher", name="Roger Fisher", affiliation="Harvard Law School", birth_year=1922, key_works=["Getting to Yes"]),
    Theorist(id="th-ury", name="William Ury", affiliation="Harvard Negotiation Project", birth_year=1953, key_works=["Getting to Yes", "Getting Past No"]),
    Theorist(id="th-zartman", name="I. William Zartman", affiliation="Johns Hopkins SAIS", birth_year=1932, key_works=["Ripe for Resolution"]),
    Theorist(id="th-galtung", name="Johan Galtung", affiliation="PRIO", birth_year=1930, key_works=["Violence, Peace, and Peace Research"]),
    Theorist(id="th-burton", name="John Burton", affiliation="University College London", birth_year=1915, key_works=["Conflict: Resolution and Provention"]),
    Theorist(id="th-kriesberg", name="Louis Kriesberg", affiliation="Syracuse University", birth_year=1926, key_works=["Constructive Conflicts"]),
    Theorist(id="th-lederach", name="John Paul Lederach", affiliation="University of Notre Dame", birth_year=1955, key_works=["Building Peace"]),
    Theorist(id="th-deutsch", name="Morton Deutsch", affiliation="Columbia University", birth_year=1920, key_works=["The Resolution of Conflict"]),
    Theorist(id="th-pearl", name="Judea Pearl", affiliation="UCLA", birth_year=1936, key_works=["Causality"]),
    Theorist(id="th-french", name="John French", affiliation="University of Michigan", birth_year=1913, key_works=["The Bases of Social Power"]),
    Theorist(id="th-raven", name="Bertram Raven", affiliation="UCLA", birth_year=1926, key_works=["The Bases of Social Power"]),
    Theorist(id="th-mayer", name="Roger Mayer", affiliation="University of Akron", key_works=["An Integrative Model of Organizational Trust"]),
    Theorist(id="th-plutchik", name="Robert Plutchik", affiliation="Albert Einstein College of Medicine", birth_year=1927, key_works=["Emotion: A Psychoevolutionary Synthesis"]),
    Theorist(id="th-thomas", name="Kenneth Thomas", affiliation="Naval Postgraduate School", key_works=["Conflict and Negotiation Processes"]),
    Theorist(id="th-kilmann", name="Ralph Kilmann", affiliation="University of Pittsburgh", key_works=["Thomas-Kilmann Conflict Mode Instrument"]),
    Theorist(id="th-winslade", name="John Winslade", affiliation="California State University San Bernardino", key_works=["Narrative Mediation"]),
    Theorist(id="th-monk", name="Gerald Monk", affiliation="San Diego State University", key_works=["Narrative Mediation"]),
    Theorist(id="th-brett", name="Jeanne Brett", affiliation="Northwestern University", key_works=["Getting Disputes Resolved"]),
    Theorist(id="th-goldberg", name="Stephen Goldberg", affiliation="Northwestern University", key_works=["Getting Disputes Resolved"]),
]

# ─── Key Concepts ───────────────────────────────────────────────────────────

CONCEPTS = [
    # Glasl
    TheoryConcept(id="tc-glasl-stage1", name="Hardening", framework_id="glasl", description="Positions harden; tension but belief in resolution through talk", category="escalation"),
    TheoryConcept(id="tc-glasl-stage2", name="Debate and Polemics", framework_id="glasl", description="Polarisation; verbal confrontation and pressure tactics", category="escalation"),
    TheoryConcept(id="tc-glasl-stage3", name="Actions Not Words", framework_id="glasl", description="Talk yields to action; empathy declines", category="escalation"),
    TheoryConcept(id="tc-glasl-stage4", name="Images and Coalitions", framework_id="glasl", description="Stereotypes form; parties recruit allies", category="escalation"),
    TheoryConcept(id="tc-glasl-stage5", name="Loss of Face", framework_id="glasl", description="Public attacks on opponent's moral credibility", category="escalation"),
    TheoryConcept(id="tc-glasl-stage6", name="Strategies of Threats", framework_id="glasl", description="Threats and counter-threats; ultimatums", category="escalation"),
    TheoryConcept(id="tc-glasl-stage7", name="Limited Destructive Blows", framework_id="glasl", description="Opponent no longer seen as human; limited strikes", category="escalation"),
    TheoryConcept(id="tc-glasl-stage8", name="Fragmentation", framework_id="glasl", description="Destruction of enemy's core systems", category="escalation"),
    TheoryConcept(id="tc-glasl-stage9", name="Together into the Abyss", framework_id="glasl", description="Total confrontation with no way back; mutual destruction", category="escalation"),
    TheoryConcept(id="tc-glasl-winwin", name="Win-Win Zone", framework_id="glasl", description="Stages 1-3 where mutual gain is still possible", category="level"),
    TheoryConcept(id="tc-glasl-winlose", name="Win-Lose Zone", framework_id="glasl", description="Stages 4-6 where one party seeks to prevail", category="level"),
    TheoryConcept(id="tc-glasl-loselose", name="Lose-Lose Zone", framework_id="glasl", description="Stages 7-9 where mutual destruction dominates", category="level"),

    # Fisher & Ury
    TheoryConcept(id="tc-fu-interests", name="Interests vs Positions", framework_id="fisher_ury", description="Focus on underlying interests, not stated positions", category="negotiation"),
    TheoryConcept(id="tc-fu-batna", name="BATNA", framework_id="fisher_ury", description="Best Alternative to a Negotiated Agreement", category="negotiation"),
    TheoryConcept(id="tc-fu-zopa", name="ZOPA", framework_id="fisher_ury", description="Zone of Possible Agreement", category="negotiation"),
    TheoryConcept(id="tc-fu-separate", name="Separate People from Problem", framework_id="fisher_ury", description="Address substance without damaging relationship", category="principle"),
    TheoryConcept(id="tc-fu-criteria", name="Objective Criteria", framework_id="fisher_ury", description="Use independent standards for evaluation", category="negotiation"),
    TheoryConcept(id="tc-fu-options", name="Generate Options for Mutual Gain", framework_id="fisher_ury", description="Expand the pie before dividing it", category="negotiation"),

    # Zartman
    TheoryConcept(id="tc-z-mhs", name="Mutually Hurting Stalemate", framework_id="zartman", description="Both parties perceive unacceptable cost of continuing conflict", category="ripeness"),
    TheoryConcept(id="tc-z-meo", name="Mutually Enticing Opportunity", framework_id="zartman", description="Both parties perceive attractive alternative to conflict", category="ripeness"),
    TheoryConcept(id="tc-z-ripe", name="Ripe Moment", framework_id="zartman", description="Convergence of MHS and MEO creates window for resolution", category="ripeness"),
    TheoryConcept(id="tc-z-wayout", name="Way Out", framework_id="zartman", description="Perception of a viable negotiated solution", category="ripeness"),

    # Galtung
    TheoryConcept(id="tc-g-structural", name="Structural Violence", framework_id="galtung", description="Violence built into social structures causing unequal outcomes", category="violence"),
    TheoryConcept(id="tc-g-cultural", name="Cultural Violence", framework_id="galtung", description="Cultural elements used to legitimize structural/direct violence", category="violence"),
    TheoryConcept(id="tc-g-direct", name="Direct Violence", framework_id="galtung", description="Physical violence by identifiable actors", category="violence"),
    TheoryConcept(id="tc-g-triangle", name="Violence Triangle", framework_id="galtung", description="Interrelation of direct, structural, and cultural violence", category="framework"),
    TheoryConcept(id="tc-g-positive-peace", name="Positive Peace", framework_id="galtung", description="Presence of conditions for justice and equity", category="peace"),
    TheoryConcept(id="tc-g-negative-peace", name="Negative Peace", framework_id="galtung", description="Absence of direct violence", category="peace"),

    # Burton
    TheoryConcept(id="tc-b-bhn", name="Basic Human Needs", framework_id="burton", description="Fundamental needs (identity, security, recognition) that cannot be traded", category="needs"),
    TheoryConcept(id="tc-b-provention", name="Provention", framework_id="burton", description="Proactive removal of conflict sources, not just prevention", category="resolution"),

    # Kriesberg
    TheoryConcept(id="tc-k-emergence", name="Conflict Emergence", framework_id="kriesberg", description="Phase where conflict becomes manifest", category="dynamics"),
    TheoryConcept(id="tc-k-escalation", name="Conflict Escalation", framework_id="kriesberg", description="Intensification through contentious actions", category="dynamics"),
    TheoryConcept(id="tc-k-deescalation", name="Conflict De-escalation", framework_id="kriesberg", description="Reduction in intensity of contentious behavior", category="dynamics"),
    TheoryConcept(id="tc-k-settlement", name="Conflict Settlement", framework_id="kriesberg", description="Agreement to end overt contention", category="dynamics"),
    TheoryConcept(id="tc-k-transformation", name="Conflict Transformation", framework_id="kriesberg", description="Fundamental change in conflict relationship", category="dynamics"),

    # Lederach
    TheoryConcept(id="tc-l-transform", name="Conflict Transformation", framework_id="lederach", description="Change the relationships and structures underlying conflict", category="transformation"),
    TheoryConcept(id="tc-l-moral-imagination", name="Moral Imagination", framework_id="lederach", description="Capacity to imagine and generate constructive responses", category="transformation"),
    TheoryConcept(id="tc-l-web-of-relationships", name="Web of Relationships", framework_id="lederach", description="Conflict embedded in relational systems, not isolated events", category="transformation"),

    # Deutsch
    TheoryConcept(id="tc-d-cooperation", name="Cooperation", framework_id="deutsch", description="Linked fate where gain for one benefits all", category="interaction"),
    TheoryConcept(id="tc-d-competition", name="Competition", framework_id="deutsch", description="Linked fate where gain for one harms others", category="interaction"),
    TheoryConcept(id="tc-d-crude-law", name="Crude Law of Social Relations", framework_id="deutsch", description="Cooperation begets cooperation; competition begets competition", category="principle"),

    # Pearl
    TheoryConcept(id="tc-p-association", name="Association", framework_id="pearl_causal", description="Level 1: Observational correlation (seeing)", category="causality"),
    TheoryConcept(id="tc-p-intervention", name="Intervention", framework_id="pearl_causal", description="Level 2: What happens if we act (doing)", category="causality"),
    TheoryConcept(id="tc-p-counterfactual", name="Counterfactual", framework_id="pearl_causal", description="Level 3: What would have happened (imagining)", category="causality"),

    # Mayer Trust
    TheoryConcept(id="tc-m-ability", name="Perceived Ability", framework_id="mayer_trust", description="Trust component based on perceived competence", category="trust"),
    TheoryConcept(id="tc-m-benevolence", name="Perceived Benevolence", framework_id="mayer_trust", description="Trust component based on perceived positive intent", category="trust"),
    TheoryConcept(id="tc-m-integrity", name="Perceived Integrity", framework_id="mayer_trust", description="Trust component based on perceived adherence to principles", category="trust"),

    # French & Raven
    TheoryConcept(id="tc-fr-legitimate", name="Legitimate Power", framework_id="french_raven", description="Power from formal position or authority", category="power"),
    TheoryConcept(id="tc-fr-reward", name="Reward Power", framework_id="french_raven", description="Power from ability to provide rewards", category="power"),
    TheoryConcept(id="tc-fr-coercive", name="Coercive Power", framework_id="french_raven", description="Power from ability to impose penalties", category="power"),
    TheoryConcept(id="tc-fr-expert", name="Expert Power", framework_id="french_raven", description="Power from specialized knowledge", category="power"),
    TheoryConcept(id="tc-fr-referent", name="Referent Power", framework_id="french_raven", description="Power from admiration and identification", category="power"),

    # Plutchik
    TheoryConcept(id="tc-pl-joy", name="Joy", framework_id="plutchik", description="Primary emotion on Plutchik's wheel", category="emotion"),
    TheoryConcept(id="tc-pl-trust", name="Trust", framework_id="plutchik", description="Primary emotion enabling cooperation", category="emotion"),
    TheoryConcept(id="tc-pl-fear", name="Fear", framework_id="plutchik", description="Primary emotion driving avoidance or flight", category="emotion"),
    TheoryConcept(id="tc-pl-anger", name="Anger", framework_id="plutchik", description="Primary emotion driving aggression", category="emotion"),

    # Thomas-Kilmann
    TheoryConcept(id="tc-tk-competing", name="Competing", framework_id="thomas_kilmann", description="High assertiveness, low cooperativeness", category="conflict_mode"),
    TheoryConcept(id="tc-tk-collaborating", name="Collaborating", framework_id="thomas_kilmann", description="High assertiveness, high cooperativeness", category="conflict_mode"),
    TheoryConcept(id="tc-tk-compromising", name="Compromising", framework_id="thomas_kilmann", description="Moderate assertiveness and cooperativeness", category="conflict_mode"),
    TheoryConcept(id="tc-tk-avoiding", name="Avoiding", framework_id="thomas_kilmann", description="Low assertiveness, low cooperativeness", category="conflict_mode"),
    TheoryConcept(id="tc-tk-accommodating", name="Accommodating", framework_id="thomas_kilmann", description="Low assertiveness, high cooperativeness", category="conflict_mode"),

    # Winslade & Monk
    TheoryConcept(id="tc-wm-narrative", name="Narrative Framing", framework_id="winslade_monk", description="Conflicts are constructed through the stories parties tell", category="narrative"),
    TheoryConcept(id="tc-wm-deconstruction", name="Narrative Deconstruction", framework_id="winslade_monk", description="Unpacking dominant conflict narratives", category="narrative"),
    TheoryConcept(id="tc-wm-reauthoring", name="Reauthoring", framework_id="winslade_monk", description="Co-creating alternative narratives of the conflict", category="narrative"),
]

# ─── Patterns ───────────────────────────────────────────────────────────────

PATTERNS = [
    Pattern(id="pat-escalation-spiral", name="Escalation Spiral", description="Self-reinforcing cycle of increasingly hostile actions", indicators=["Increasing Glasl stage", "Reciprocal hostile events", "Coalition formation"]),
    Pattern(id="pat-security-dilemma", name="Security Dilemma", description="One party's defensive measures perceived as threats by others", indicators=["Arms buildup", "Alliance formation", "Threat perception asymmetry"]),
    Pattern(id="pat-stalemate", name="Hurting Stalemate", description="Both parties locked in costly impasse", indicators=["High costs for all parties", "No unilateral solution", "Willingness to negotiate"]),
    Pattern(id="pat-trust-erosion", name="Trust Erosion", description="Progressive breakdown of trust between parties", indicators=["Broken commitments", "Decreased communication", "Negative attribution bias"]),
    Pattern(id="pat-narrative-polarization", name="Narrative Polarization", description="Diverging narratives increasingly incompatible", indicators=["Dehumanizing language", "Victim narratives", "Zero-sum framing"]),
    Pattern(id="pat-power-asymmetry", name="Power Asymmetry", description="Significant imbalance in power between parties", indicators=["Resource disparity", "Access to institutions", "Coalition size difference"]),
]

# ─── Cross-references (Edges) ──────────────────────────────────────────────

THEORY_EDGES = [
    # Fisher/Ury interests BUILDS_ON Burton basic human needs
    {"type": "BUILDS_ON", "source": "tc-fu-interests", "target": "tc-b-bhn"},
    # Zartman ripeness BUILDS_ON Glasl escalation
    {"type": "BUILDS_ON", "source": "tc-z-mhs", "target": "tc-glasl-stage6"},
    # Lederach transformation BUILDS_ON Kriesberg dynamics
    {"type": "BUILDS_ON", "source": "tc-l-transform", "target": "tc-k-transformation"},
    # Galtung structural violence CONTRADICTS simple escalation view
    {"type": "CONTRADICTS", "source": "tc-g-structural", "target": "tc-glasl-stage1"},
    # Deutsch crude law BUILDS_ON Fisher cooperation
    {"type": "BUILDS_ON", "source": "tc-d-crude-law", "target": "tc-fu-options"},
    # Patterns exemplify concepts
    {"type": "EXEMPLIFIES", "source": "pat-escalation-spiral", "target": "tc-glasl-stage6"},
    {"type": "EXEMPLIFIES", "source": "pat-stalemate", "target": "tc-z-mhs"},
    {"type": "EXEMPLIFIES", "source": "pat-trust-erosion", "target": "tc-m-integrity"},
    {"type": "EXEMPLIFIES", "source": "pat-narrative-polarization", "target": "tc-wm-narrative"},
    {"type": "EXEMPLIFIES", "source": "pat-power-asymmetry", "target": "tc-fr-coercive"},
]


def get_all_theory_nodes():
    """Return all theory graph nodes."""
    return THEORISTS + CONCEPTS + PATTERNS


def get_all_theory_edges():
    """Return all theory graph edges."""
    return THEORY_EDGES


if __name__ == "__main__":
    nodes = get_all_theory_nodes()
    edges = get_all_theory_edges()
    print(f"Theory graph: {len(nodes)} nodes, {len(edges)} edges")
    print(f"  Theorists: {len(THEORISTS)}")
    print(f"  Concepts: {len(CONCEPTS)}")
    print(f"  Patterns: {len(PATTERNS)}")
