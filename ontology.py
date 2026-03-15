"""
TACITUS CORE ONTOLOGY v2.0
============================
The Universal Knowledge Structure for Human Friction

A graph-native ontology for modeling conflict, disputes, and negotiations
across all scales — from interpersonal workplace disputes to geopolitical
armed conflicts. Designed for neurosymbolic AI: deterministic Cypher
queries + probabilistic GNN inference.

Scientific Rationale:
    A neurosymbolic architecture for conflict data is justified because
    conflict analysis requires both statistical language understanding
    and explicit relational reasoning. Neural models parse unstructured
    evidence; symbolic structures preserve actors, claims, commitments,
    chronology, and causal hypotheses; graph-based retrieval plus
    argumentation improve traceability, consistency, and decision support.

    The architecture does not claim automated resolution — it supports
    better conflict intelligence and more disciplined human-mediated
    resolution workflows. The sharpest defensible claim: "We make
    conflict computable enough for better human judgment."

Theoretical Grounding (30+ frameworks):
    Negotiation: Fisher/Ury/Patton, Malhotra/Bazerman, Voss, Mnookin,
                 Ury/Brett/Goldberg, Lewicki/Barry/Saunders
    Conflict:    Galtung, Glasl, Lederach, Kriesberg, Deutsch, Coleman,
                 Kelman, Thomas-Kilmann, Pruitt/Rubin
    Computational: PLOVER, CAMEO, ACLED, UCDP, GDELT, ConfliBERT
    Legal:       LKIF, CLO, Hohfeld, AAA, ICC, ICSID, UNCITRAL
    Psychology:  Plutchik, Mayer/Davis/Schoorman, Smith & Ellsworth,
                 Tajfel, Ting-Toomey, Edmondson
    Narrative:   Winslade/Monk, Cobb, Dewulf, Lakoff
    Power:       French/Raven, Ury/Brett/Goldberg
    Systems:     Volkan (chosen trauma), ISO 45003 (psychosocial risk)
    Causality:   Pearl (causal framework — association vs. intervention
                 vs. counterfactual reasoning)

Usage:
    from tacitus_ontology.core import NODES, EDGES, ENUMS
    # Access any node spec:  NODES["Actor"]
    # Access any edge spec:  EDGES["PARTY_TO"]
    # Access any enum:       ENUMS["ConflictScale"]

Graph DB Target: Neo4j / FalkorDB (Labeled Property Graph)
Neurosymbolic: Symbolic layer (Cypher rules) + Neural layer (R-GAT embeddings)
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


# ═══════════════════════════════════════════════════════════════════════════
#  ENUMERATIONS — Controlled vocabularies for property values
# ═══════════════════════════════════════════════════════════════════════════

ENUMS = {

    # ─── Actor ──────────────────────────────────────────────────────────
    "ActorType": {
        "values": ["person", "organization", "state", "coalition", "informal_group"],
        "source": "CAMEO/ACLED synthesis",
    },

    # ─── Conflict ───────────────────────────────────────────────────────
    "ConflictScale": {
        "values": ["micro", "meso", "macro", "meta"],
        "source": "Lederach nested paradigm",
        "notes": "micro=interpersonal, meso=organizational/community, macro=national/international, meta=civilizational",
    },
    "ConflictDomain": {
        "values": ["interpersonal", "workplace", "commercial", "legal", "political", "armed"],
        "source": "TACITUS synthesis",
    },
    "ConflictStatus": {
        "values": ["latent", "active", "dormant", "resolved", "transformed"],
        "source": "Kriesberg + Lederach",
    },
    "KriesbergPhase": {
        "values": [
            "latent",           # Structural conditions exist but not articulated
            "emerging",         # Parties become aware of incompatibility
            "escalating",       # Intensification of hostile interactions
            "stalemate",        # Hurting stalemate / mutually enticing opportunity
            "de_escalating",    # Reduction in hostility
            "terminating",      # Active resolution efforts
            "post_conflict",    # Implementation & reconciliation
        ],
        "source": "Kriesberg: Constructive Conflicts",
    },
    "GlaslStage": {
        "values": {
            1: {"name": "hardening", "level": "win_win", "intervention": "moderation"},
            2: {"name": "debate_and_polemics", "level": "win_win", "intervention": "moderation"},
            3: {"name": "actions_not_words", "level": "win_win", "intervention": "facilitation"},
            4: {"name": "images_and_coalitions", "level": "win_lose", "intervention": "process_consultation"},
            5: {"name": "loss_of_face", "level": "win_lose", "intervention": "mediation"},
            6: {"name": "strategies_of_threats", "level": "win_lose", "intervention": "mediation"},
            7: {"name": "limited_destructive_blows", "level": "lose_lose", "intervention": "arbitration"},
            8: {"name": "fragmentation", "level": "lose_lose", "intervention": "power_intervention"},
            9: {"name": "together_into_the_abyss", "level": "lose_lose", "intervention": "power_intervention"},
        },
        "source": "Glasl: Confronting Conflict",
    },
    "GlaslLevel": {
        "values": ["win_win", "win_lose", "lose_lose"],
        "source": "Glasl (derived from stage 1-3, 4-6, 7-9)",
    },
    "Incompatibility": {
        "values": ["government", "territory", "resource", "rights", "relationship", "identity"],
        "source": "UCDP + Galtung extended",
    },
    "ViolenceType": {
        "values": ["direct", "structural", "cultural", "none"],
        "source": "Galtung violence triangle",
    },
    "Intensity": {
        "values": ["low", "moderate", "high", "severe", "extreme"],
        "source": "Synthesis (maps to UCDP minor/war thresholds)",
    },

    # ─── Event ──────────────────────────────────────────────────────────
    "EventType": {
        "values": [
            # Cooperative spectrum (PLOVER)
            "agree", "consult", "support", "cooperate", "aid", "yield",
            # Neutral
            "investigate",
            # Conflict spectrum (PLOVER)
            "demand", "disapprove", "reject", "threaten", "protest",
            "exhibit_force_posture", "reduce_relations", "coerce", "assault",
        ],
        "source": "PLOVER 16-type ontology",
        "notes": "Domain add-ons map specific events to these universal types",
    },
    "EventMode": {
        "values": [
            "verbal", "written", "diplomatic", "legal", "economic",
            "cyber", "conventional_military", "unconventional",
            "administrative", "procedural", "symbolic",
        ],
        "source": "PLOVER mode concept (extended for non-geopolitical domains)",
    },
    "EventContext": {
        "values": [
            "political", "territorial", "economic", "ethnic", "religious",
            "environmental", "labor", "contractual", "regulatory",
            "interpersonal", "organizational", "technological",
        ],
        "source": "PLOVER context concept (extended)",
    },
    "QuadClass": {
        "values": ["verbal_cooperation", "material_cooperation", "verbal_conflict", "material_conflict"],
        "source": "CAMEO/PLOVER QuadClass",
    },

    # ─── Interest ───────────────────────────────────────────────────────
    "InterestType": {
        "values": ["substantive", "procedural", "psychological", "identity"],
        "source": "Fisher/Ury + Rothman identity-based conflict",
    },

    # ─── Norm ───────────────────────────────────────────────────────────
    "NormType": {
        "values": [
            "statute", "regulation", "treaty", "contract", "policy",
            "social_norm", "customary_law", "precedent", "professional_standard",
        ],
        "source": "LKIF + CLO synthesis",
    },
    "Enforceability": {
        "values": ["binding", "advisory", "aspirational"],
        "source": "CLO (Core Legal Ontology)",
    },

    # ─── Process ────────────────────────────────────────────────────────
    "ProcessType": {
        "values": [
            "negotiation", "mediation_facilitative", "mediation_evaluative",
            "mediation_transformative", "mediation_narrative",
            "arbitration", "adjudication", "investigation",
            "grievance_procedure", "ombuds", "conciliation",
            "early_neutral_evaluation", "online_dispute_resolution",
        ],
        "source": "ADR taxonomy synthesis",
    },
    "ResolutionApproach": {
        "values": ["interest_based", "rights_based", "power_based"],
        "source": "Ury/Brett/Goldberg: Getting Disputes Resolved",
        "notes": "THE meta-framework: conflicts most efficiently resolved at interest level; rights/power escalate cost",
    },
    "ProcessStatus": {
        "values": ["pending", "active", "suspended", "completed", "abandoned", "appealed"],
        "source": "ADR lifecycle synthesis",
    },

    # ─── Outcome ────────────────────────────────────────────────────────
    "OutcomeType": {
        "values": [
            "agreement", "settlement", "award", "judgment", "consent_order",
            "withdrawal", "no_resolution", "ceasefire", "peace_agreement",
            "transformation", "acquiescence",
        ],
        "source": "Multi-domain synthesis",
    },
    "Durability": {
        "values": ["temporary", "durable", "permanent"],
        "source": "Peace research (positive vs negative peace)",
    },

    # ─── Emotion ────────────────────────────────────────────────────────
    "PrimaryEmotion": {
        "values": ["joy", "trust", "fear", "surprise", "sadness", "disgust", "anger", "anticipation"],
        "source": "Plutchik wheel of emotions",
        "dyads": {
            "optimism": ("anticipation", "joy"),
            "love": ("joy", "trust"),
            "submission": ("trust", "fear"),
            "awe": ("fear", "surprise"),
            "disapproval": ("surprise", "sadness"),
            "remorse": ("sadness", "disgust"),
            "contempt": ("disgust", "anger"),
            "aggressiveness": ("anger", "anticipation"),
        },
    },
    "EmotionIntensity": {
        "values": ["low", "medium", "high"],
        "source": "Plutchik (e.g., annoyance → anger → rage)",
    },

    # ─── Narrative ──────────────────────────────────────────────────────
    "NarrativeType": {
        "values": ["dominant", "alternative", "counter", "subjugated"],
        "source": "Winslade & Monk: Narrative Mediation",
    },

    # ─── ConflictMode ───────────────────────────────────────────────────
    "ConflictMode": {
        "values": ["competing", "collaborating", "compromising", "avoiding", "accommodating"],
        "source": "Thomas-Kilmann Conflict Mode Instrument",
        "dual_concern_mapping": {
            "competing":      {"assertiveness": "high", "cooperativeness": "low"},
            "collaborating":  {"assertiveness": "high", "cooperativeness": "high"},
            "compromising":   {"assertiveness": "medium", "cooperativeness": "medium"},
            "avoiding":       {"assertiveness": "low", "cooperativeness": "low"},
            "accommodating":  {"assertiveness": "low", "cooperativeness": "high"},
        },
    },

    # ─── Power ──────────────────────────────────────────────────────────
    "PowerDomain": {
        "values": [
            "coercive", "economic", "political", "informational",
            "positional", "referent", "legitimate", "expert",
        ],
        "source": "French & Raven + Ury/Brett/Goldberg",
    },

    # ─── Role ───────────────────────────────────────────────────────────
    "RoleType": {
        "values": [
            "claimant", "respondent", "mediator", "arbitrator", "judge",
            "witness", "advocate", "aggressor", "target", "bystander",
            "facilitator", "perpetrator", "victim", "ally", "neutral",
            "guarantor", "spoiler", "peacemaker",
        ],
        "source": "Multi-domain synthesis",
    },
}


# ═══════════════════════════════════════════════════════════════════════════
#  NODE SPECIFICATIONS — 15 Core Entity Types
# ═══════════════════════════════════════════════════════════════════════════

NODES = {

    # ─── 1. ACTOR ───────────────────────────────────────────────────────
    "Actor": {
        "description": (
            "Any entity capable of agency in a conflict. The polymorphic root type. "
            "Use multi-labels for subtypes: :Actor:Person, :Actor:Organization, :Actor:State, etc."
        ),
        "theoretical_basis": "CAMEO/ACLED actor coding + Fisher/Ury 'negotiator'",
        "properties": {
            "id":               {"type": "String (UUID)", "required": True,  "description": "Unique identifier"},
            "name":             {"type": "String",        "required": True,  "description": "Display name"},
            "actor_type":       {"type": "Enum:ActorType","required": True,  "description": "Primary classification"},
            "description":      {"type": "String",        "required": False, "description": "Contextual description"},
            "influence_score":  {"type": "Float [0,1]",   "required": False, "description": "Estimated overall influence"},
            "embedding":        {"type": "Float[128]",    "required": False, "description": "Neural embedding vector (GNN layer)"},
        },
        "multi_labels": {
            "Person":       {"extra_props": ["role_title", "gender", "age"]},
            "Organization": {"extra_props": ["org_type", "jurisdiction", "size", "sector"]},
            "State":        {"extra_props": ["sovereignty", "regime_type", "iso_code"]},
            "Coalition":    {"extra_props": ["formation_date", "cohesion"]},
            "InformalGroup":{"extra_props": ["estimated_size", "structure"]},
        },
        "indexes": ["name", "actor_type"],
        "domain_notes": {
            "geopolitical": "States, rebel groups, IGOs, NGOs (UCDP/ACLED actor types)",
            "workplace":    "Employees, managers, HR, departments, unions",
            "legal":        "Plaintiffs, defendants, counsel, judges, tribunals",
            "commercial":   "Companies, contractors, subcontractors, project managers",
        },
    },

    # ─── 2. CONFLICT ────────────────────────────────────────────────────
    "Conflict": {
        "description": (
            "A sustained pattern of friction between parties around an incompatibility. "
            "Distinct from a single Event. The central organizing node."
        ),
        "theoretical_basis": "UCDP incompatibility + Galtung ABC + Glasl escalation + Kriesberg lifecycle",
        "properties": {
            "id":                {"type": "String (UUID)",         "required": True,  "description": "Unique identifier"},
            "name":              {"type": "String",                "required": True,  "description": "Conflict name/title"},
            "scale":             {"type": "Enum:ConflictScale",    "required": True,  "description": "Lederach nested level"},
            "domain":            {"type": "Enum:ConflictDomain",   "required": True,  "description": "Primary domain"},
            "incompatibility":   {"type": "Enum:Incompatibility",  "required": False, "description": "Root incompatibility (UCDP extended)"},
            "glasl_stage":       {"type": "Int [1-9]",             "required": False, "description": "Current Glasl escalation stage"},
            "glasl_level":       {"type": "Enum:GlaslLevel",       "required": False, "description": "Derived: win_win/win_lose/lose_lose"},
            "kriesberg_phase":   {"type": "Enum:KriesbergPhase",   "required": False, "description": "Conflict lifecycle phase"},
            "violence_type":     {"type": "Enum:ViolenceType",     "required": False, "description": "Galtung: direct/structural/cultural/none"},
            "intensity":         {"type": "Enum:Intensity",        "required": False, "description": "Current intensity level"},
            "status":            {"type": "Enum:ConflictStatus",   "required": True,  "description": "Current status"},
            "started_at":        {"type": "DateTime",              "required": False, "description": "Onset date"},
            "ended_at":          {"type": "DateTime",              "required": False, "description": "Termination date"},
            "summary":           {"type": "String",                "required": False, "description": "Narrative summary"},
            "embedding":         {"type": "Float[128]",            "required": False, "description": "Neural embedding"},
        },
        "indexes": ["domain", "status", "glasl_stage", "started_at"],
        "symbolic_rules": [
            "IF glasl_stage IN [7,8,9] THEN glasl_level = 'lose_lose'",
            "IF glasl_stage IN [4,5,6] THEN glasl_level = 'win_lose'",
            "IF glasl_stage IN [1,2,3] THEN glasl_level = 'win_win'",
            "IF glasl_stage increases by 2+ in <30 days THEN ALERT:rapid_escalation",
        ],
    },

    # ─── 3. EVENT ───────────────────────────────────────────────────────
    "Event": {
        "description": (
            "A discrete, time-bounded occurrence that alters a conflict's state. "
            "Follows PLOVER's Event-Mode-Context architecture."
        ),
        "theoretical_basis": "PLOVER event-mode-context + ACLED event taxonomy",
        "properties": {
            "id":                {"type": "String (UUID)",      "required": True,  "description": "Unique identifier"},
            "event_type":        {"type": "Enum:EventType",     "required": True,  "description": "PLOVER 16-type (WHAT happened)"},
            "mode":              {"type": "Enum:EventMode",     "required": False, "description": "HOW it happened"},
            "context":           {"type": "Enum:EventContext",  "required": False, "description": "WHY / issue area"},
            "quad_class":        {"type": "Enum:QuadClass",     "required": False, "description": "CAMEO verbal/material × coop/conflict"},
            "severity":          {"type": "Float [0,1]",        "required": True,  "description": "Normalized severity"},
            "description":       {"type": "String",             "required": False, "description": "Narrative description of event"},
            "occurred_at":       {"type": "DateTime",           "required": True,  "description": "Event timestamp"},
            "source_text":       {"type": "String",             "required": False, "description": "Original source passage"},
            "confidence":        {"type": "Float [0,1]",        "required": False, "description": "Epistemic certainty"},
            "embedding":         {"type": "Float[128]",         "required": False, "description": "Neural embedding"},
        },
        "indexes": ["event_type", "occurred_at", "severity"],
        "domain_notes": {
            "geopolitical": "Direct PLOVER mapping. ACLED sub-event types in addon.",
            "workplace":    "complaint=DEMAND, hearing=INVESTIGATE, disciplinary=COERCE, mediation=CONSULT",
            "legal":        "filing=DEMAND, ruling=YIELD/REJECT, settlement=AGREE, appeal=REJECT",
            "commercial":   "variation_order=DEMAND, payment=COOPERATE, adjudication=INVESTIGATE",
        },
    },

    # ─── 4. ISSUE ───────────────────────────────────────────────────────
    "Issue": {
        "description": (
            "The subject matter or incompatibility at stake. What the conflict is ABOUT."
        ),
        "theoretical_basis": "UCDP incompatibility + Fisher/Ury 'the problem'",
        "properties": {
            "id":              {"type": "String (UUID)",         "required": True,  "description": "Unique identifier"},
            "name":            {"type": "String",                "required": True,  "description": "Issue description"},
            "issue_type":      {"type": "Enum:InterestType",     "required": True,  "description": "substantive/procedural/psychological/identity"},
            "domain_category": {"type": "String",                "required": False, "description": "Domain-specific category (from addon)"},
            "salience":        {"type": "Float [0,1]",           "required": False, "description": "How central to the conflict"},
            "divisibility":    {"type": "Float [0,1]",           "required": False, "description": "Can it be split/shared? (0=indivisible, 1=fully divisible)"},
        },
    },

    # ─── 5. INTEREST ────────────────────────────────────────────────────
    "Interest": {
        "description": (
            "An underlying need, desire, concern, or fear. The WHY behind a position. "
            "Fisher/Ury's central concept. Distinguished from Position (what they SAY) "
            "and BATNA (what they'll do if no deal)."
        ),
        "theoretical_basis": "Fisher/Ury 'Getting to Yes' + Rothman identity-based conflict",
        "properties": {
            "id":                 {"type": "String (UUID)",        "required": True,  "description": "Unique identifier"},
            "description":        {"type": "String",               "required": True,  "description": "Interest statement"},
            "interest_type":      {"type": "Enum:InterestType",    "required": True,  "description": "substantive/procedural/psychological/identity"},
            "priority":           {"type": "Int [1-5]",            "required": False, "description": "1=critical, 5=nice-to-have"},
            "stated":             {"type": "Boolean",              "required": False, "description": "Explicitly stated or inferred?"},
            "stated_position":    {"type": "String",               "required": False, "description": "The POSITION that masks this interest (Fisher/Ury)"},
            "satisfaction":       {"type": "Float [0,1]",          "required": False, "description": "Current satisfaction level"},
            "batna_description":  {"type": "String",               "required": False, "description": "Best Alternative to Negotiated Agreement"},
            "batna_strength":     {"type": "Enum: strong/moderate/weak", "required": False, "description": "BATNA quality assessment"},
            "reservation_value":  {"type": "Float",                "required": False, "description": "Walk-away point (Malhotra/Bazerman)"},
        },
        "notes": (
            "Position and BATNA are properties of Interest rather than separate nodes in the sweet-spot version. "
            "This is because Position only makes sense relative to an Interest, and BATNA is the "
            "actor's alternative for satisfying that interest. In Version A (maximal), these become separate nodes."
        ),
    },

    # ─── 6. NORM ────────────────────────────────────────────────────────
    "Norm": {
        "description": (
            "Any rule, standard, or shared expectation governing behavior. "
            "Covers laws, contracts, policies, social norms, professional standards."
        ),
        "theoretical_basis": "LKIF + CLO + Fisher/Ury 'objective criteria'",
        "properties": {
            "id":              {"type": "String (UUID)",        "required": True,  "description": "Unique identifier"},
            "name":            {"type": "String",               "required": True,  "description": "Norm title/citation"},
            "norm_type":       {"type": "Enum:NormType",        "required": True,  "description": "Classification"},
            "jurisdiction":    {"type": "String",               "required": False, "description": "Geographic/organizational scope"},
            "enforceability":  {"type": "Enum:Enforceability",  "required": False, "description": "binding/advisory/aspirational"},
            "text":            {"type": "String",               "required": False, "description": "Norm text or summary"},
            "effective_from":  {"type": "DateTime",             "required": False, "description": "When norm took effect"},
            "effective_to":    {"type": "DateTime",             "required": False, "description": "Expiry/repeal date"},
        },
    },

    # ─── 7. PROCESS ─────────────────────────────────────────────────────
    "Process": {
        "description": (
            "Any procedure or mechanism for addressing conflict. "
            "Classified by Ury/Brett/Goldberg's interest-rights-power hierarchy."
        ),
        "theoretical_basis": "Ury/Brett/Goldberg + ADR taxonomy + Glasl intervention mapping",
        "properties": {
            "id":                   {"type": "String (UUID)",          "required": True,  "description": "Unique identifier"},
            "process_type":         {"type": "Enum:ProcessType",       "required": True,  "description": "Specific mechanism"},
            "resolution_approach":  {"type": "Enum:ResolutionApproach","required": True,  "description": "interest/rights/power (THE meta-framework)"},
            "formality":            {"type": "Enum: informal/semi_formal/formal", "required": False, "description": "Formality level"},
            "binding":              {"type": "Boolean",                "required": False, "description": "Is outcome binding?"},
            "voluntary":            {"type": "Boolean",                "required": False, "description": "Is participation voluntary?"},
            "current_stage":        {"type": "Enum: intake/dialogue/evaluation/resolution/implementation", "required": False, "description": "Current lifecycle stage"},
            "status":               {"type": "Enum:ProcessStatus",     "required": True,  "description": "Current status"},
            "started_at":           {"type": "DateTime",               "required": False, "description": "Process start"},
            "ended_at":             {"type": "DateTime",               "required": False, "description": "Process end"},
            "governing_rules":      {"type": "String",                 "required": False, "description": "Applicable rules (e.g., ICC Rules, AAA Commercial)"},
        },
        "symbolic_rules": [
            "IF Process.resolution_approach='power_based' AND Outcome.outcome_type='no_resolution' THEN recommend Process WHERE resolution_approach='interest_based'",
            "IF Conflict.glasl_stage <= 3 THEN recommend Process.process_type IN ['negotiation','mediation_facilitative']",
            "IF Conflict.glasl_stage IN [4,5,6] THEN recommend Process.process_type IN ['mediation_evaluative','arbitration']",
            "IF Conflict.glasl_stage >= 7 THEN recommend Process.process_type IN ['arbitration','adjudication'] WITH escalation_alert",
        ],
    },

    # ─── 8. OUTCOME ─────────────────────────────────────────────────────
    "Outcome": {
        "description": "The result of a conflict resolution process or the conflict itself.",
        "theoretical_basis": "Mnookin 'Beyond Winning' (value creation) + ADR outcomes",
        "properties": {
            "id":                 {"type": "String (UUID)",       "required": True,  "description": "Unique identifier"},
            "outcome_type":       {"type": "Enum:OutcomeType",    "required": True,  "description": "Classification"},
            "description":        {"type": "String",              "required": False, "description": "Outcome summary"},
            "monetary_value":     {"type": "Float",               "required": False, "description": "Financial component if applicable"},
            "satisfaction_a":     {"type": "Float [0,1]",         "required": False, "description": "Party A satisfaction"},
            "satisfaction_b":     {"type": "Float [0,1]",         "required": False, "description": "Party B satisfaction"},
            "joint_value":        {"type": "Float [0,1]",         "required": False, "description": "Integrative value created (Mnookin)"},
            "durability":         {"type": "Enum:Durability",     "required": False, "description": "Expected permanence"},
            "compliance_rate":    {"type": "Float [0,1]",         "required": False, "description": "Implementation compliance"},
            "decided_at":         {"type": "DateTime",            "required": False, "description": "Decision date"},
        },
    },

    # ─── 9. NARRATIVE ───────────────────────────────────────────────────
    "Narrative": {
        "description": (
            "A dominant story, account, or frame that shapes how a conflict is understood. "
            "Critical for neurosymbolic reasoning — narratives are the primary vehicle "
            "through which conflicts persist or transform."
        ),
        "theoretical_basis": "Winslade & Monk + Sara Cobb + Dewulf framing + Lakoff",
        "properties": {
            "id":              {"type": "String (UUID)",         "required": True,  "description": "Unique identifier"},
            "content":         {"type": "String",                "required": True,  "description": "Narrative summary"},
            "narrative_type":  {"type": "Enum:NarrativeType",    "required": True,  "description": "dominant/alternative/counter/subjugated"},
            "perspective":     {"type": "String",                "required": False, "description": "Whose perspective"},
            "frame_type":      {"type": "Enum: identity/characterization/power/risk/loss_gain/moral", "required": False, "description": "Dewulf frame classification"},
            "coherence":       {"type": "Float [0,1]",           "required": False, "description": "Internal narrative coherence (Cobb)"},
            "reach":           {"type": "Float [0,1]",           "required": False, "description": "How widely adopted"},
            "moral_order":     {"type": "String",                "required": False, "description": "Implied moral framework (Cobb)"},
            "embedding":       {"type": "Float[128]",            "required": False, "description": "Neural embedding for similarity"},
        },
    },

    # ─── 10. EMOTIONAL STATE ────────────────────────────────────────────
    "EmotionalState": {
        "description": (
            "An actor's emotional condition at a point in time. "
            "Emotions DRIVE conflict behavior — they are not epiphenomenal."
        ),
        "theoretical_basis": "Plutchik wheel + Smith & Ellsworth appraisal theory + Intergroup emotion theory",
        "properties": {
            "id":                {"type": "String (UUID)",          "required": True,  "description": "Unique identifier"},
            "primary_emotion":   {"type": "Enum:PrimaryEmotion",    "required": True,  "description": "Plutchik primary (8 types)"},
            "intensity":         {"type": "Enum:EmotionIntensity",  "required": True,  "description": "low/medium/high"},
            "secondary_emotion": {"type": "String",                 "required": False, "description": "Plutchik dyad (e.g., contempt=disgust+anger)"},
            "valence":           {"type": "Float [-1,1]",           "required": False, "description": "Positive-negative"},
            "arousal":           {"type": "Float [0,1]",            "required": False, "description": "Activation level"},
            "is_group_emotion":  {"type": "Boolean",                "required": False, "description": "Individual vs. collective (Smith & Mackie)"},
            "trigger_event_id":  {"type": "String",                 "required": False, "description": "Event that triggered this state"},
            "observed_at":       {"type": "DateTime",               "required": True,  "description": "Timestamp"},
            "confidence":        {"type": "Float [0,1]",            "required": False, "description": "Detection confidence"},
        },
    },

    # ─── 11. TRUST STATE ────────────────────────────────────────────────
    "TrustState": {
        "description": (
            "Trust level between two actors. THE single most predictive relational variable. "
            "Based on Mayer/Davis/Schoorman's integrative model: trust = f(ability, benevolence, integrity)."
        ),
        "theoretical_basis": "Mayer/Davis/Schoorman 1995 + Lewicki & Bunker trust development",
        "properties": {
            "id":                     {"type": "String (UUID)", "required": True,  "description": "Unique identifier"},
            "perceived_ability":      {"type": "Float [0,1]",  "required": True,  "description": "Can they do what they promise?"},
            "perceived_benevolence":  {"type": "Float [0,1]",  "required": True,  "description": "Do they care about my interests?"},
            "perceived_integrity":    {"type": "Float [0,1]",  "required": True,  "description": "Are they honest and principled?"},
            "propensity_to_trust":    {"type": "Float [0,1]",  "required": False, "description": "Trustor's dispositional trait"},
            "overall_trust":          {"type": "Float [0,1]",  "required": True,  "description": "Composite trust score"},
            "trust_basis":            {"type": "Enum: calculus/knowledge/identification", "required": False, "description": "Lewicki & Bunker trust stage"},
            "assessed_at":            {"type": "DateTime",     "required": True,  "description": "When assessed"},
        },
        "symbolic_rules": [
            "overall_trust ≈ propensity_to_trust × (w1×ability + w2×benevolence + w3×integrity)",
            "IF overall_trust < 0.3 THEN flag: trust_deficit — likely escalation risk",
            "IF perceived_integrity drops > 0.3 in single assessment THEN flag: trust_breach_event",
        ],
    },

    # ─── 12. POWER DYNAMIC ──────────────────────────────────────────────
    "PowerDynamic": {
        "description": (
            "A measured power relationship between actors. Kept as a node (not just edge property) "
            "to enable temporal versioning — power shifts are a primary escalation driver."
        ),
        "theoretical_basis": "French & Raven 5 bases of power + Ury/Brett/Goldberg",
        "properties": {
            "id":             {"type": "String (UUID)",       "required": True,  "description": "Unique identifier"},
            "power_domain":   {"type": "Enum:PowerDomain",    "required": True,  "description": "Type of power"},
            "magnitude":      {"type": "Float [0,1]",         "required": True,  "description": "Strength of asymmetry"},
            "direction":      {"type": "Enum: a_over_b/b_over_a/symmetric", "required": True, "description": "Who holds power"},
            "legitimacy":     {"type": "Float [0,1]",         "required": False, "description": "Perceived legitimacy of power"},
            "exercised":      {"type": "Boolean",             "required": False, "description": "Has this power been actively used?"},
            "reversible":     {"type": "Boolean",             "required": False, "description": "Can power balance shift?"},
            "valid_from":     {"type": "DateTime",            "required": False, "description": "Temporal start"},
            "valid_to":       {"type": "DateTime",            "required": False, "description": "Temporal end (null = current)"},
        },
    },

    # ─── 13. LOCATION ───────────────────────────────────────────────────
    "Location": {
        "description": "Geographic entity. Hierarchically structured via WITHIN edges.",
        "theoretical_basis": "ACLED/UCDP spatial coding",
        "properties": {
            "id":             {"type": "String (UUID)",  "required": True,  "description": "Unique identifier"},
            "name":           {"type": "String",         "required": True,  "description": "Place name"},
            "location_type":  {"type": "Enum: point/building/city/district/region/country/global", "required": True, "description": "Hierarchy level"},
            "latitude":       {"type": "Float",          "required": False, "description": "Coordinate"},
            "longitude":      {"type": "Float",          "required": False, "description": "Coordinate"},
            "country_code":   {"type": "String",         "required": False, "description": "ISO 3166-1 alpha-3"},
        },
    },

    # ─── 14. EVIDENCE ───────────────────────────────────────────────────
    "Evidence": {
        "description": "Supporting material for claims, events, or assertions.",
        "theoretical_basis": "Legal evidence law + ACLED source methodology",
        "properties": {
            "id":              {"type": "String (UUID)", "required": True,  "description": "Unique identifier"},
            "evidence_type":   {"type": "Enum: document/testimony/expert_opinion/digital_record/physical/statistical", "required": True, "description": "Classification"},
            "description":     {"type": "String",        "required": True,  "description": "Description"},
            "source_name":     {"type": "String",        "required": False, "description": "Source attribution"},
            "reliability":     {"type": "Float [0,1]",   "required": False, "description": "Assessed reliability"},
            "url":             {"type": "String",        "required": False, "description": "Reference URL"},
            "created_at":      {"type": "DateTime",      "required": False, "description": "When evidence was created/recorded"},
        },
    },

    # ─── 15. ROLE ───────────────────────────────────────────────────────
    "Role": {
        "description": (
            "A contextual role played by an actor in a specific conflict or event. "
            "Reification pattern: the SAME actor can be victim in one context and aggressor in another."
        ),
        "theoretical_basis": "SEM (Simple Event Model) role reification",
        "properties": {
            "id":          {"type": "String (UUID)",    "required": True,  "description": "Unique identifier"},
            "role_type":   {"type": "Enum:RoleType",    "required": True,  "description": "Role classification"},
            "valid_from":  {"type": "DateTime",         "required": False, "description": "Role start"},
            "valid_to":    {"type": "DateTime",         "required": False, "description": "Role end"},
        },
    },
}


# ═══════════════════════════════════════════════════════════════════════════
#  EDGE SPECIFICATIONS — 20 Core Relationship Types
# ═══════════════════════════════════════════════════════════════════════════

EDGES = {

    # ─── Actor-Conflict Relations ───────────────────────────────────────
    "PARTY_TO": {
        "source": "Actor",
        "target": "Conflict",
        "description": "Actor is a party to a conflict",
        "properties": {
            "role":       {"type": "String",    "description": "Role in this conflict"},
            "side":       {"type": "Enum: side_a/side_b/third_party/observer", "description": "Which side (UCDP convention)"},
            "joined_at":  {"type": "DateTime",  "description": "When actor became a party"},
            "left_at":    {"type": "DateTime",  "description": "When actor ceased involvement"},
        },
        "cardinality": "Many:Many",
        "source_theory": "UCDP dyadic structure",
    },

    "PARTICIPATES_IN": {
        "source": "Actor",
        "target": "Event",
        "description": "Actor participates in a specific event (PLOVER Source-Action-Target)",
        "properties": {
            "role_type":  {"type": "Enum:RoleType", "description": "Role in this event (perpetrator, target, witness, etc.)"},
            "influence":  {"type": "Float [0,1]",   "description": "Degree of influence on event"},
        },
        "cardinality": "Many:Many",
        "source_theory": "CAMEO/PLOVER Source-Action-Target triplet",
    },

    # ─── Actor-Interest Relations ───────────────────────────────────────
    "HAS_INTEREST": {
        "source": "Actor",
        "target": "Interest",
        "description": "Actor holds this underlying interest (Fisher/Ury core concept)",
        "properties": {
            "priority":     {"type": "Int [1-5]",  "description": "How important (1=critical)"},
            "in_conflict":  {"type": "String",     "description": "Conflict ID this interest relates to"},
            "stated":       {"type": "Boolean",    "description": "Has actor articulated this interest?"},
        },
        "cardinality": "Many:Many",
        "source_theory": "Fisher/Ury: focus on interests, not positions",
    },

    # ─── Event-Conflict Relations ───────────────────────────────────────
    "PART_OF": {
        "source": "Event",
        "target": "Conflict",
        "description": "Event belongs to this conflict",
        "properties": {},
        "cardinality": "Many:One",
        "source_theory": "ACLED/UCDP event-conflict linking",
    },

    # ─── Event-Event Relations (Causal Chain) ───────────────────────────
    "CAUSED": {
        "source": "Event",
        "target": "Event",
        "description": "One event caused or contributed to another. THE critical edge for escalation analysis.",
        "properties": {
            "mechanism":  {"type": "Enum: escalation/retaliation/contagion/spillover/provocation/precedent", "description": "Causal mechanism"},
            "strength":   {"type": "Float [0,1]",  "description": "Causal strength"},
            "lag":        {"type": "Duration",      "description": "Time between cause and effect"},
            "confidence": {"type": "Float [0,1]",   "description": "Confidence in causal link"},
        },
        "cardinality": "Many:Many",
        "source_theory": "XPEventCore causal chains + Glasl escalation sequences",
    },

    # ─── Spatial Relations ──────────────────────────────────────────────
    "AT_LOCATION": {
        "source": "Event",
        "target": "Location",
        "description": "Event occurred at this location",
        "properties": {
            "precision": {"type": "Int [1-7]", "description": "UCDP geo-precision code"},
        },
        "cardinality": "Many:One",
        "source_theory": "ACLED/UCDP spatial coding",
    },

    "WITHIN": {
        "source": "Location",
        "target": "Location",
        "description": "Hierarchical containment (city WITHIN country)",
        "properties": {},
        "cardinality": "Many:One",
        "source_theory": "Spatial hierarchy",
    },

    # ─── Actor-Actor Relations ──────────────────────────────────────────
    "ALLIED_WITH": {
        "source": "Actor",
        "target": "Actor",
        "description": "Cooperative alignment between actors",
        "properties": {
            "strength":   {"type": "Float [0,1]", "description": "Alliance strength"},
            "formality":  {"type": "Enum: formal/tacit", "description": "Formal treaty or tacit alignment"},
            "since":      {"type": "DateTime",    "description": "Alliance formation"},
            "confidence": {"type": "Float [0,1]", "description": "Assessment confidence"},
        },
        "cardinality": "Many:Many",
        "source_theory": "UCDP alliance coding + Glasl Stage 4 (coalitions)",
    },

    "OPPOSED_TO": {
        "source": "Actor",
        "target": "Actor",
        "description": "Adversarial relationship between actors",
        "properties": {
            "intensity": {"type": "Float [0,1]", "description": "Opposition intensity"},
            "since":     {"type": "DateTime",    "description": "When opposition began"},
        },
        "cardinality": "Many:Many",
        "source_theory": "UCDP dyadic opposition",
    },

    "HAS_POWER_OVER": {
        "source": "Actor",
        "target": "Actor",
        "description": "Power asymmetry between actors",
        "properties": {
            "power_dynamic_id": {"type": "String", "description": "References PowerDynamic node for full detail"},
            "domain":           {"type": "Enum:PowerDomain", "description": "Quick-access power type"},
            "magnitude":        {"type": "Float [0,1]",      "description": "Quick-access magnitude"},
        },
        "cardinality": "Many:Many",
        "source_theory": "French & Raven + Ury/Brett/Goldberg power-based resolution",
    },

    "MEMBER_OF": {
        "source": "Actor",
        "target": "Actor",
        "description": "Organizational/group membership (Person MEMBER_OF Organization)",
        "properties": {
            "role":  {"type": "String",   "description": "Role within organization"},
            "since": {"type": "DateTime", "description": "Membership start"},
            "until": {"type": "DateTime", "description": "Membership end"},
        },
        "cardinality": "Many:Many",
        "source_theory": "Organizational structure",
    },

    # ─── Normative Relations ────────────────────────────────────────────
    "GOVERNED_BY": {
        "source": "Conflict",
        "target": "Norm",
        "description": "Conflict is subject to this norm/law/contract",
        "properties": {
            "applicability": {"type": "Float [0,1]", "description": "How applicable is this norm"},
        },
        "cardinality": "Many:Many",
        "source_theory": "LKIF legal knowledge + Fisher/Ury objective criteria",
    },

    "VIOLATES": {
        "source": "Event",
        "target": "Norm",
        "description": "Event violates this norm (critical for escalation and rights-based claims)",
        "properties": {
            "severity":    {"type": "Float [0,1]", "description": "Violation severity"},
            "intentional": {"type": "Boolean",     "description": "Was violation intentional?"},
        },
        "cardinality": "Many:Many",
        "source_theory": "CLO + Glasl violation escalation",
    },

    # ─── Process Relations ──────────────────────────────────────────────
    "RESOLVED_THROUGH": {
        "source": "Conflict",
        "target": "Process",
        "description": "Conflict addressed through this process",
        "properties": {
            "initiated_at":  {"type": "DateTime", "description": "When process was initiated"},
            "initiated_by":  {"type": "String",   "description": "Actor ID who initiated"},
        },
        "cardinality": "Many:Many",
        "source_theory": "Ury/Brett/Goldberg dispute system design",
    },

    "PRODUCES": {
        "source": "Process",
        "target": "Outcome",
        "description": "Process generates this outcome",
        "properties": {},
        "cardinality": "Many:One",
        "source_theory": "ADR process → outcome",
    },

    # ─── Psychological Relations ────────────────────────────────────────
    "EXPERIENCES": {
        "source": "Actor",
        "target": "EmotionalState",
        "description": "Actor experiences this emotional state",
        "properties": {
            "context_event_id":    {"type": "String", "description": "Triggering event"},
            "context_conflict_id": {"type": "String", "description": "Related conflict"},
        },
        "cardinality": "Many:Many",
        "source_theory": "Plutchik + Smith & Ellsworth appraisal theory",
    },

    "TRUSTS": {
        "source": "Actor",
        "target": "Actor",
        "description": "Trust relationship (links to TrustState node for temporal versioning)",
        "properties": {
            "trust_state_id":  {"type": "String",     "description": "Current TrustState node ID"},
            "overall_trust":   {"type": "Float [0,1]", "description": "Quick-access trust score"},
        },
        "cardinality": "Many:Many",
        "source_theory": "Mayer/Davis/Schoorman integrative trust model",
    },

    # ─── Narrative Relations ────────────────────────────────────────────
    "PROMOTES": {
        "source": "Actor",
        "target": "Narrative",
        "description": "Actor actively promotes/advances this narrative",
        "properties": {
            "strength":   {"type": "Float [0,1]", "description": "How strongly promoted"},
            "since":      {"type": "DateTime",    "description": "Since when"},
        },
        "cardinality": "Many:Many",
        "source_theory": "Winslade & Monk + Cobb narrative theory",
    },

    "ABOUT": {
        "source": "Narrative",
        "target": "Conflict",
        "description": "Narrative is about/frames this conflict",
        "properties": {},
        "cardinality": "Many:Many",
        "source_theory": "Dewulf framing theory",
    },

    # ─── Evidence Relations ─────────────────────────────────────────────
    "EVIDENCED_BY": {
        "source": "Event",
        "target": "Evidence",
        "description": "Event is supported by this evidence",
        "properties": {
            "relevance": {"type": "Float [0,1]", "description": "Relevance of evidence to event"},
        },
        "cardinality": "Many:Many",
        "source_theory": "Legal evidence + ACLED source methodology",
    },
}


# ═══════════════════════════════════════════════════════════════════════════
#  NEUROSYMBOLIC ARCHITECTURE
# ═══════════════════════════════════════════════════════════════════════════

NEUROSYMBOLIC = {
    "architecture_rationale": (
        "A neurosymbolic architecture for conflict data is justified because "
        "conflict analysis requires both statistical language understanding and "
        "explicit relational reasoning. Neural models parse unstructured evidence; "
        "symbolic structures preserve actors, claims, commitments, chronology, "
        "and causal hypotheses; and graph-based retrieval plus argumentation "
        "improve traceability, consistency, and decision support. "
        "This is NOT just GraphRAG — it is a four-layer neurosymbolic system."
    ),
    "four_layers": {
        "1_neural_ingestion": (
            "Extract actors, claims, events, sentiments, commitments, threats, "
            "concessions, timelines, and uncertainty from messy text using the "
            "ontology as an extraction schema. Each extraction carries a confidence score."
        ),
        "2_symbolic_representation": (
            "Encode extracted entities into the conflict ontology graph with typed "
            "relations, controlled vocabularies, and temporal metadata."
        ),
        "3_reasoning_inference": (
            "Contradiction checks, commitment tracking, escalation pattern detection, "
            "argument maps, procedural rules, causal hypotheses. Deterministic rules "
            "fire first; neural GNN predictions fill gaps second."
        ),
        "4_decision_support": (
            "Surface options, risks, missing evidence, and competing interpretations "
            "for human decision-makers. Human validation promotes neural suggestions "
            "to new symbolic rules (learning loop)."
        ),
    },
    "symbolic_layer": {
        "description": "Deterministic reasoning via Cypher queries and rule-based inference",
        "components": [
            "Glasl escalation rules (stage transition triggers and intervention recommendations)",
            "Ury/Brett/Goldberg loop-back rules (failed power → recommend interests)",
            "Trust breach detection (integrity drop > 0.3 triggers alert)",
            "UCDP conflict classification (25-death threshold, incompatibility typing)",
            "Temporal logic via Allen's interval algebra on valid_from/valid_to",
            "Norm violation detection (Event-VIOLATES-Norm chains)",
            "BATNA comparison (reservation values across parties → ZOPA computation)",
            "Causal chain analysis (Event-CAUSED-Event path traversal for escalation patterns)",
            "Cross-case structural similarity (subgraph isomorphism for pattern recognition)",
        ],
        "query_language": "Cypher (Neo4j/FalkorDB) + custom rule engine",
    },
    "neural_layer": {
        "description": "Probabilistic inference via GNN embeddings and link prediction",
        "components": [
            "R-GAT (Relational Graph Attention Network) for heterogeneous graph embedding",
            "RotatE for knowledge graph link prediction (predict future alliances, oppositions)",
            "Temporal attention mechanism for trajectory forecasting",
            "Narrative similarity via embedding cosine distance",
            "Conflict pattern matching via subgraph isomorphism + neural fingerprinting",
            "Escalation prediction: GNN trained on historical (Event, Event, CAUSED) chains",
            "Outcome prediction: predict resolution probability by dispute profile",
        ],
        "embedding_nodes": ["Actor", "Conflict", "Event", "Narrative"],
        "recommended_dim": 128,
        "training_approach": "reason-then-embed (OWL inference → materialize edges → embed enriched graph)",
    },
    "bridge": {
        "description": "How symbolic and neural layers interact (reason-then-embed pipeline)",
        "pattern": (
            "1. Symbolic rules fire first (deterministic, explainable) "
            "2. Neural layer fills gaps (predictions, similarities, anomalies) "
            "3. Human-in-the-loop validates neural suggestions "
            "4. Validated suggestions become new symbolic rules (learning loop)"
        ),
        "key_principle": (
            "Deterministic conclusions are NEVER overridden by probabilistic inference. "
            "The symbolic layer provides the auditability and accountability required "
            "in high-stakes conflict domains."
        ),
    },
    "scientific_risks": {
        "ontology_loss": (
            "If schema is too rigid, it flattens meaningful ambiguity. "
            "Mitigation: controlled vocabularies, confidence scores, preserved source_text."
        ),
        "extraction_error_propagation": (
            "LLM misreads can look authoritative in symbolic layer. "
            "Mitigation: confidence scores, HITL validation, stated/inferred distinction."
        ),
        "normative_overreach": (
            "System may identify strategic efficiency without understanding procedural "
            "fairness or political legitimacy. "
            "Mitigation: TACITUS is decision-support, not autonomous resolution."
        ),
    },
}


# ═══════════════════════════════════════════════════════════════════════════
#  HELPER: Generate Cypher DDL for graph database initialization
# ═══════════════════════════════════════════════════════════════════════════

def generate_cypher_constraints() -> str:
    """Generate Cypher CREATE CONSTRAINT statements for all node types."""
    lines = ["// TACITUS Core Ontology — Graph Database Initialization\n"]
    for node_name in NODES:
        lines.append(f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{node_name}) REQUIRE n.id IS UNIQUE;")
    return "\n".join(lines)


def generate_cypher_indexes() -> str:
    """Generate Cypher CREATE INDEX statements for optimized queries."""
    lines = ["\n// Indexes for query optimization\n"]
    for node_name, spec in NODES.items():
        for idx_prop in spec.get("indexes", []):
            lines.append(f"CREATE INDEX IF NOT EXISTS FOR (n:{node_name}) ON (n.{idx_prop});")
    # Composite indexes for common query patterns
    lines.append("\n// Composite indexes")
    lines.append("CREATE INDEX IF NOT EXISTS FOR (n:Event) ON (n.event_type, n.occurred_at);")
    lines.append("CREATE INDEX IF NOT EXISTS FOR (n:Conflict) ON (n.domain, n.status);")
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════
#  METADATA
# ═══════════════════════════════════════════════════════════════════════════

ONTOLOGY_META = {
    "name": "TACITUS Core Ontology",
    "version": "2.0.1",
    "author": "Giulio Catanzariti — TACITUS (tacitus.me)",
    "license": "CC-BY-SA 4.0",
    "node_count": len(NODES),
    "edge_count": len(EDGES),
    "enum_count": len(ENUMS),
    "theoretical_frameworks": 30,
    "target_graph_db": "Neo4j / FalkorDB (Labeled Property Graph)",
    "architecture": "Neurosymbolic (reason-then-embed pipeline)",
    "description": (
        "The universal knowledge structure for human friction. "
        "15 node types × 20 edge types × 25 controlled vocabularies. "
        "Designed for neurosymbolic reasoning: deterministic Cypher rules + "
        "probabilistic GNN inference. Four-layer architecture: neural ingestion, "
        "symbolic representation, reasoning inference, decision support. "
        "Not just GraphRAG — a structured intelligence layer for conflict."
    ),
    "sharpest_claim": "We make conflict computable enough for better human judgment.",
}


if __name__ == "__main__":
    print(f"TACITUS Core Ontology v{ONTOLOGY_META['version']}")
    print(f"  Nodes: {ONTOLOGY_META['node_count']}")
    print(f"  Edges: {ONTOLOGY_META['edge_count']}")
    print(f"  Enums: {ONTOLOGY_META['enum_count']}")
    print(f"\n{generate_cypher_constraints()}")
    print(f"\n{generate_cypher_indexes()}")
