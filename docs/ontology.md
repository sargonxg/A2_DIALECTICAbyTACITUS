# TACITUS Agentic Conflict Ontology (ACO) v2.0

Complete reference for the DIALECTICA conflict ontology -- 15 node types, 20 edge
types, 30+ controlled vocabularies, 15 theory frameworks, 4 compatibility mappers,
and 5 schema generators.

**Source package:** `packages/ontology/src/dialectica_ontology/`

---

## Design Principles

| Principle | Description |
|---|---|
| **Graph-native** | Every primitive is a node or edge with ULID identifiers, first-class temporal fields, and embedding slots for vector search. |
| **Neurosymbolic** | Discrete symbolic types (enums, schemas) coexist with continuous features (confidence scores, 128/768-dim embeddings, float magnitudes). Theory frameworks bridge the two via `assess()` and `score()` methods. |
| **Scale-agnostic** | The same schema models interpersonal workplace disputes and international armed conflicts. The `ConflictScale` enum (micro/meso/macro/meta) and Lederach's nested paradigm ensure structural consistency across levels. |
| **Theory-grounded** | Every node and edge traces to a published conflict resolution framework: Glasl, Kriesberg, Fisher/Ury, Galtung, PLOVER, CAMEO, ACLED, UCDP, and others. Theoretical provenance is documented in class docstrings. |
| **Tiered** | Three progressive tiers (Essential, Standard, Full) control which node/edge types are exposed, enabling simple mapping at low tiers and complete neurosymbolic intelligence at the Full tier. |

### Base Class: `ConflictNode`

All 15 node types inherit from `ConflictNode`, which provides:

| Field | Type | Default | Description |
|---|---|---|---|
| `id` | `str` | ULID auto-gen | Unique identifier |
| `label` | `str` | `""` | Node type label (set by subclass) |
| `workspace_id` | `str` | `""` | Workspace scope |
| `tenant_id` | `str` | `""` | Tenant isolation |
| `created_at` | `datetime` | now | Creation timestamp |
| `updated_at` | `datetime` | now | Last update timestamp |
| `source_text` | `str \| None` | `None` | Original text this node was extracted from |
| `confidence` | `float` | `1.0` | Extraction confidence `[0.0, 1.0]` |
| `extraction_method` | `str \| None` | `None` | How this node was created (e.g. `"llm"`, `"rule"`) |
| `embedding` | `list[float] \| None` | `None` | 128-dim or 768-dim vector embedding |
| `metadata` | `dict[str, Any]` | `{}` | Arbitrary key-value metadata |

---

## Node Types (15)

### Group 1: Core

#### 1. Actor

Any entity capable of agency in a conflict.

- **Theoretical basis:** CAMEO/ACLED actor coding + Fisher/Ury "negotiator"
- **Tier:** Essential

| Property | Type | Required | Description |
|---|---|---|---|
| `name` | `str` | Yes | Display name |
| `actor_type` | `ActorType` | Yes | person, organization, state, coalition, informal_group |
| `description` | `str \| None` | No | Free-text description |
| `influence_score` | `float \| None` | No | `[0.0, 1.0]` |
| `role_title` | `str \| None` | No | Person subtype |
| `gender` | `str \| None` | No | Person subtype |
| `age` | `int \| None` | No | Person subtype |
| `org_type` | `str \| None` | No | Organization subtype |
| `jurisdiction` | `str \| None` | No | Organization/State subtype |
| `size` | `int \| None` | No | Organization subtype |
| `sector` | `str \| None` | No | Organization subtype |
| `sovereignty` | `str \| None` | No | State subtype |
| `regime_type` | `str \| None` | No | State subtype |
| `iso_code` | `str \| None` | No | State subtype (ISO 3166-1) |
| `formation_date` | `datetime \| None` | No | Coalition subtype |
| `cohesion` | `float \| None` | No | Coalition subtype `[0.0, 1.0]` |
| `estimated_size` | `int \| None` | No | InformalGroup subtype |
| `structure` | `str \| None` | No | InformalGroup subtype |
| `aliases` | `list[str]` | No | Alternative names for entity matching |
| `capabilities` | `list[str]` | No | Known capabilities |

#### 2. Conflict

A sustained pattern of friction between parties around an incompatibility.

- **Theoretical basis:** UCDP incompatibility + Galtung ABC + Glasl escalation + Kriesberg lifecycle
- **Tier:** Essential

| Property | Type | Required | Description |
|---|---|---|---|
| `name` | `str` | Yes | Conflict name |
| `scale` | `ConflictScale` | Yes | micro, meso, macro, meta |
| `domain` | `ConflictDomain` | Yes | interpersonal, workplace, commercial, legal, political, armed |
| `status` | `ConflictStatus` | Yes | latent, active, dormant, resolved, transformed |
| `incompatibility` | `Incompatibility \| None` | No | government, territory, resource, rights, relationship, identity |
| `glasl_stage` | `int \| None` | No | `[1, 9]` -- auto-derives `glasl_level` |
| `glasl_level` | `GlaslLevel \| None` | No | win_win (1-3), win_lose (4-6), lose_lose (7-9) |
| `kriesberg_phase` | `KriesbergPhase \| None` | No | latent, emerging, escalating, stalemate, de_escalating, terminating, post_conflict |
| `violence_type` | `ViolenceType \| None` | No | direct, structural, cultural, none |
| `intensity` | `Intensity \| None` | No | low, moderate, high, severe, extreme |
| `started_at` | `datetime \| None` | No | Conflict start |
| `ended_at` | `datetime \| None` | No | Conflict end |
| `summary` | `str \| None` | No | Free-text summary |

**Auto-derivation:** When `glasl_stage` is set and `glasl_level` is not, the model validator
automatically derives the level: stages 1-3 = win_win, 4-6 = win_lose, 7-9 = lose_lose.

#### 3. Event

A discrete, time-bounded occurrence that alters a conflict's state.

- **Theoretical basis:** PLOVER event-mode-context + ACLED event taxonomy
- **Tier:** Essential

| Property | Type | Required | Description |
|---|---|---|---|
| `event_type` | `EventType` | Yes | 16 PLOVER types (see Enumerations) |
| `mode` | `EventMode \| None` | No | verbal, written, diplomatic, legal, economic, cyber, ... |
| `context` | `EventContext \| None` | No | political, territorial, economic, ethnic, ... |
| `quad_class` | `QuadClass \| None` | No | verbal_cooperation, material_cooperation, verbal_conflict, material_conflict |
| `severity` | `float` | Yes | `[0.0, 1.0]` |
| `description` | `str \| None` | No | Free-text description |
| `occurred_at` | `datetime` | Yes | When the event occurred |
| `source_count` | `int \| None` | No | Number of corroborating sources |
| `fatalities` | `int \| None` | No | Fatality count (armed conflict) |
| `location_text` | `str \| None` | No | Raw location string |

### Group 2: Structure

#### 4. Issue

The subject matter or incompatibility at stake.

- **Theoretical basis:** UCDP incompatibility + Fisher/Ury "the problem"
- **Tier:** Essential

| Property | Type | Required | Description |
|---|---|---|---|
| `name` | `str` | Yes | Issue name |
| `issue_type` | `InterestType` | Yes | substantive, procedural, psychological, identity |
| `domain_category` | `str \| None` | No | Domain-specific category |
| `salience` | `float \| None` | No | `[0.0, 1.0]` -- how important to parties |
| `divisibility` | `float \| None` | No | `[0.0, 1.0]` -- how easily split |

#### 5. Interest

An underlying need, desire, concern, or fear -- the WHY behind a position.

- **Theoretical basis:** Fisher/Ury "Getting to Yes" + Rothman identity-based conflict
- **Tier:** Standard

| Property | Type | Required | Description |
|---|---|---|---|
| `description` | `str` | Yes | What the interest is |
| `interest_type` | `InterestType` | Yes | substantive, procedural, psychological, identity |
| `priority` | `int \| None` | No | `[1, 5]` |
| `stated` | `bool \| None` | No | Whether explicitly stated |
| `stated_position` | `str \| None` | No | The position masking this interest |
| `satisfaction` | `float \| None` | No | `[0.0, 1.0]` -- current satisfaction level |
| `batna_description` | `str \| None` | No | Best Alternative To Negotiated Agreement |
| `batna_strength` | `BatnaStrength \| None` | No | strong, moderate, weak |
| `reservation_value` | `float \| None` | No | Walk-away threshold |

#### 6. Norm

Any rule, standard, or shared expectation governing behavior.

- **Theoretical basis:** LKIF + CLO + Fisher/Ury "objective criteria"
- **Tier:** Standard

| Property | Type | Required | Description |
|---|---|---|---|
| `name` | `str` | Yes | Norm name |
| `norm_type` | `NormType` | Yes | statute, regulation, treaty, contract, policy, social_norm, customary_law, precedent, professional_standard |
| `jurisdiction` | `str \| None` | No | Applicable jurisdiction |
| `enforceability` | `Enforceability \| None` | No | binding, advisory, aspirational |
| `text` | `str \| None` | No | Norm text |
| `effective_from` | `datetime \| None` | No | Start of applicability |
| `effective_to` | `datetime \| None` | No | End of applicability |

### Group 3: Process

#### 7. Process

Any procedure or mechanism for addressing conflict.

- **Theoretical basis:** Ury/Brett/Goldberg + ADR taxonomy + Glasl intervention mapping
- **Tier:** Essential

| Property | Type | Required | Description |
|---|---|---|---|
| `process_type` | `ProcessType` | Yes | negotiation, mediation_facilitative, mediation_evaluative, mediation_transformative, mediation_narrative, arbitration, adjudication, investigation, grievance_procedure, ombuds, conciliation, early_neutral_evaluation, online_dispute_resolution |
| `resolution_approach` | `ResolutionApproach` | Yes | interest_based, rights_based, power_based |
| `status` | `ProcessStatus` | Yes | pending, active, suspended, completed, abandoned, appealed |
| `formality` | `Formality \| None` | No | informal, semi_formal, formal |
| `binding` | `bool \| None` | No | Whether outcome is binding |
| `voluntary` | `bool \| None` | No | Whether participation is voluntary |
| `current_stage` | `ProcessStage \| None` | No | intake, dialogue, evaluation, resolution, implementation |
| `started_at` | `datetime \| None` | No | Process start |
| `ended_at` | `datetime \| None` | No | Process end |
| `governing_rules` | `str \| None` | No | Applicable rules/procedures |

#### 8. Outcome

The result of a conflict resolution process or the conflict itself.

- **Theoretical basis:** Mnookin "Beyond Winning" (value creation) + ADR outcomes
- **Tier:** Essential

| Property | Type | Required | Description |
|---|---|---|---|
| `outcome_type` | `OutcomeType` | Yes | agreement, settlement, award, judgment, consent_order, withdrawal, no_resolution, ceasefire, peace_agreement, transformation, acquiescence |
| `description` | `str \| None` | No | Outcome description |
| `monetary_value` | `float \| None` | No | Dollar value if applicable |
| `satisfaction_a` | `float \| None` | No | `[0.0, 1.0]` -- party A satisfaction |
| `satisfaction_b` | `float \| None` | No | `[0.0, 1.0]` -- party B satisfaction |
| `joint_value` | `float \| None` | No | `[0.0, 1.0]` -- value creation metric |
| `durability` | `Durability \| None` | No | temporary, durable, permanent |
| `compliance_rate` | `float \| None` | No | `[0.0, 1.0]` |
| `decided_at` | `datetime \| None` | No | Decision timestamp |
| `terms` | `list[str]` | No | Settlement/agreement terms |

### Group 4: Context

#### 9. Narrative

A dominant story, account, or frame that shapes how a conflict is understood.

- **Theoretical basis:** Winslade & Monk + Sara Cobb + Dewulf framing + Lakoff
- **Tier:** Standard

| Property | Type | Required | Description |
|---|---|---|---|
| `content` | `str` | Yes | Narrative content |
| `narrative_type` | `NarrativeType` | Yes | dominant, alternative, counter, subjugated |
| `perspective` | `str \| None` | No | Whose perspective |
| `frame_type` | `FrameType \| None` | No | identity, characterization, power, risk, loss_gain, moral |
| `coherence` | `float \| None` | No | `[0.0, 1.0]` -- internal consistency |
| `reach` | `float \| None` | No | `[0.0, 1.0]` -- audience penetration |
| `moral_order` | `str \| None` | No | Underlying moral logic |
| `dominant_frame` | `str \| None` | No | Primary framing device |
| `counter_frame` | `str \| None` | No | Opposing framing device |
| `media_prevalence` | `float \| None` | No | `[0.0, 1.0]` -- media presence |

#### 10. Location

Geographic entity, hierarchically structured via WITHIN edges.

- **Theoretical basis:** ACLED/UCDP spatial coding
- **Tier:** Essential

| Property | Type | Required | Description |
|---|---|---|---|
| `name` | `str` | Yes | Place name |
| `location_type` | `LocationType` | Yes | point, building, city, district, region, country, global |
| `latitude` | `float \| None` | No | `[-90.0, 90.0]` |
| `longitude` | `float \| None` | No | `[-180.0, 180.0]` |
| `country_code` | `str \| None` | No | ISO 3166-1 alpha-3 (validated to 3 chars) |
| `admin_level` | `int \| None` | No | Administrative level |

#### 11. Evidence

Supporting material for claims, events, or assertions.

- **Theoretical basis:** Legal evidence law + ACLED source methodology
- **Tier:** Standard

| Property | Type | Required | Description |
|---|---|---|---|
| `evidence_type` | `EvidenceType` | Yes | document, testimony, expert_opinion, digital_record, physical, statistical |
| `description` | `str` | Yes | Evidence description |
| `source_name` | `str \| None` | No | Source attribution |
| `reliability` | `float \| None` | No | `[0.0, 1.0]` |
| `url` | `str \| None` | No | URL to source |
| `collected_at` | `datetime \| None` | No | Collection timestamp |

#### 12. Role

A contextual role played by an actor in a specific conflict or event.

- **Theoretical basis:** SEM (Simple Event Model) role reification
- **Tier:** Standard

| Property | Type | Required | Description |
|---|---|---|---|
| `role_type` | `RoleType` | Yes | claimant, respondent, mediator, arbitrator, judge, witness, advocate, aggressor, target, bystander, facilitator, perpetrator, victim, ally, neutral, guarantor, spoiler, peacemaker |
| `valid_from` | `datetime \| None` | No | Role start |
| `valid_to` | `datetime \| None` | No | Role end |
| `actor_id` | `str \| None` | No | Reference to Actor node |
| `context_id` | `str \| None` | No | Reference to Conflict/Event node |

### Group 5: State

#### 13. EmotionalState

An actor's emotional condition at a point in time.

- **Theoretical basis:** Plutchik wheel of emotions + Smith & Ellsworth appraisal theory
- **Tier:** Full

| Property | Type | Required | Description |
|---|---|---|---|
| `primary_emotion` | `PrimaryEmotion` | Yes | joy, trust, fear, surprise, sadness, disgust, anger, anticipation |
| `intensity` | `EmotionIntensity` | Yes | low, medium, high |
| `secondary_emotion` | `str \| None` | No | Free-text secondary emotion |
| `valence` | `float \| None` | No | `[-1.0, 1.0]` -- positive/negative |
| `arousal` | `float \| None` | No | `[0.0, 1.0]` |
| `is_group_emotion` | `bool \| None` | No | Individual vs. collective emotion |
| `trigger_event_id` | `str \| None` | No | Event that triggered this state |
| `observed_at` | `datetime` | No | Observation timestamp (auto-set) |

#### 14. TrustState

Trust level between two actors.

- **Theoretical basis:** Mayer/Davis/Schoorman integrative model: trust = f(ability, benevolence, integrity)
- **Tier:** Full

| Property | Type | Required | Description |
|---|---|---|---|
| `perceived_ability` | `float` | Yes | `[0.0, 1.0]` |
| `perceived_benevolence` | `float` | Yes | `[0.0, 1.0]` |
| `perceived_integrity` | `float` | Yes | `[0.0, 1.0]` |
| `propensity_to_trust` | `float \| None` | No | `[0.0, 1.0]` -- dispositional trust |
| `overall_trust` | `float` | Yes | `[0.0, 1.0]` |
| `trust_basis` | `TrustBasis \| None` | No | calculus, knowledge, identification |
| `assessed_at` | `datetime` | No | Assessment timestamp (auto-set) |

#### 15. PowerDynamic

A measured power relationship between actors.

- **Theoretical basis:** French & Raven 5 bases of power + Ury/Brett/Goldberg
- **Tier:** Full

| Property | Type | Required | Description |
|---|---|---|---|
| `power_domain` | `PowerDomain` | Yes | coercive, economic, political, informational, positional, referent, legitimate, expert |
| `magnitude` | `float` | Yes | `[0.0, 1.0]` |
| `direction` | `PowerDirection` | Yes | a_over_b, b_over_a, symmetric |
| `legitimacy` | `float \| None` | No | `[0.0, 1.0]` |
| `exercised` | `bool \| None` | No | Whether actively exercised |
| `reversible` | `bool \| None` | No | Whether power balance can shift |
| `valid_from` | `datetime \| None` | No | Start of validity |
| `valid_to` | `datetime \| None` | No | End of validity |

---

## Edge Types (20)

### Base Class: `ConflictRelationship`

| Field | Type | Default | Description |
|---|---|---|---|
| `id` | `str` | ULID auto-gen | Unique identifier |
| `type` | `EdgeType` | -- | One of the 20 edge types |
| `source_id` | `str` | -- | Source node ID |
| `target_id` | `str` | -- | Target node ID |
| `source_label` | `str` | `""` | Source node type label |
| `target_label` | `str` | `""` | Target node type label |
| `workspace_id` | `str` | `""` | Workspace scope |
| `tenant_id` | `str` | `""` | Tenant isolation |
| `properties` | `dict[str, Any]` | `{}` | Edge-specific properties |
| `weight` | `float` | `1.0` | Edge weight `[0.0, +inf)` |
| `confidence` | `float` | `1.0` | `[0.0, 1.0]` |
| `temporal_start` | `datetime \| None` | `None` | Temporal validity start |
| `temporal_end` | `datetime \| None` | `None` | Temporal validity end |
| `source_text` | `str \| None` | `None` | Source text evidence |

### Edge Schema (EDGE_SCHEMA)

Each edge type is constrained to valid source and target node labels via `EDGE_SCHEMA`.
The `validate_relationship()` function enforces these constraints.

| # | Edge Type | Source | Target | Optional Properties | Tier |
|---|---|---|---|---|---|
| 1 | `PARTY_TO` | Actor | Conflict | role, side, joined_at, left_at | Essential |
| 2 | `PARTICIPATES_IN` | Actor | Event | role_type, influence | Essential |
| 3 | `HAS_INTEREST` | Actor | Interest | priority, in_conflict, stated | Standard |
| 4 | `PART_OF` | Event | Conflict | -- | Essential |
| 5 | `CAUSED` | Event | Event | mechanism, strength, lag, confidence | Full |
| 6 | `AT_LOCATION` | Event | Location | precision | Essential |
| 7 | `WITHIN` | Location | Location | -- | Standard |
| 8 | `ALLIED_WITH` | Actor | Actor | strength, formality, since, confidence | Full |
| 9 | `OPPOSED_TO` | Actor | Actor | intensity, since | Full |
| 10 | `HAS_POWER_OVER` | Actor | Actor | power_dynamic_id, domain, magnitude | Full |
| 11 | `MEMBER_OF` | Actor | Actor | role, since, until | Standard |
| 12 | `GOVERNED_BY` | Conflict | Norm | applicability | Standard |
| 13 | `VIOLATES` | Event | Norm | severity, intentional | Standard |
| 14 | `RESOLVED_THROUGH` | Conflict | Process | initiated_at, initiated_by | Essential |
| 15 | `PRODUCES` | Process | Outcome | -- | Essential |
| 16 | `EXPERIENCES` | Actor | EmotionalState | context_event_id, context_conflict_id | Full |
| 17 | `TRUSTS` | Actor | Actor | trust_state_id, overall_trust | Full |
| 18 | `PROMOTES` | Actor | Narrative | strength, since | Full |
| 19 | `ABOUT` | Narrative | Conflict | -- | Standard |
| 20 | `EVIDENCED_BY` | Event | Evidence | relevance | Standard |

---

## Enumerations

All enumerations are `StrEnum` subclasses defined in `enums.py`. String values are
lowercase with underscores for consistent serialisation.

### Actor Enums

| Enum | Values | Source |
|---|---|---|
| `ActorType` | person, organization, state, coalition, informal_group | CAMEO/ACLED synthesis |

### Conflict Enums

| Enum | Values | Source |
|---|---|---|
| `ConflictScale` | micro, meso, macro, meta | Lederach nested paradigm |
| `ConflictDomain` | interpersonal, workplace, commercial, legal, political, armed | TACITUS synthesis |
| `ConflictStatus` | latent, active, dormant, resolved, transformed | Kriesberg + Lederach |
| `KriesbergPhase` | latent, emerging, escalating, stalemate, de_escalating, terminating, post_conflict | Kriesberg: Constructive Conflicts |
| `Incompatibility` | government, territory, resource, rights, relationship, identity | UCDP + Galtung extended |
| `ViolenceType` | direct, structural, cultural, none | Galtung violence triangle |
| `Intensity` | low, moderate, high, severe, extreme | UCDP thresholds synthesis |

### Glasl Escalation Enums

| Enum | Values | Source |
|---|---|---|
| `GlaslStage` | hardening, debate_and_polemics, actions_not_words, images_and_coalitions, loss_of_face, strategies_of_threats, limited_destructive_blows, fragmentation, together_into_the_abyss | Glasl: Confronting Conflict |
| `GlaslLevel` | win_win, win_lose, lose_lose | Glasl (derived from stage ranges) |

**`GlaslStage` properties:**

- `stage_number` -- positional index 1-9
- `level` -- derived level string: stages 1-3 = "win_win", 4-6 = "win_lose", 7-9 = "lose_lose"
- `intervention_type` -- recommended intervention: 1-2 = moderation, 3 = facilitation, 4 = process_consultation, 5-6 = mediation, 7 = arbitration, 8-9 = power_intervention

### Event Enums

| Enum | Values | Source |
|---|---|---|
| `EventType` | **Cooperative:** agree, consult, support, cooperate, aid, yield; **Neutral:** investigate; **Conflict:** demand, disapprove, reject, threaten, protest, exhibit_force_posture, reduce_relations, coerce, assault | PLOVER 16-type ontology |
| `EventMode` | verbal, written, diplomatic, legal, economic, cyber, conventional_military, unconventional, administrative, procedural, symbolic | PLOVER mode concept (extended) |
| `EventContext` | political, territorial, economic, ethnic, religious, environmental, labor, contractual, regulatory, interpersonal, organizational, technological | PLOVER context concept (extended) |
| `QuadClass` | verbal_cooperation, material_cooperation, verbal_conflict, material_conflict | CAMEO/PLOVER QuadClass |

**EventType to QuadClass mapping:** The cooperative EventTypes (agree, consult, support, cooperate,
aid, yield) map to verbal_cooperation or material_cooperation. The conflict EventTypes (demand,
disapprove, reject, threaten, protest, exhibit_force_posture, reduce_relations, coerce, assault) map
to verbal_conflict or material_conflict. The `event_type_quadclass()` function in the PLOVER
compatibility mapper computes this mapping.

### Interest / Issue Enums

| Enum | Values | Source |
|---|---|---|
| `InterestType` | substantive, procedural, psychological, identity | Fisher/Ury + Rothman |
| `BatnaStrength` | strong, moderate, weak | Fisher/Ury BATNA assessment |

### Norm Enums

| Enum | Values | Source |
|---|---|---|
| `NormType` | statute, regulation, treaty, contract, policy, social_norm, customary_law, precedent, professional_standard | LKIF + CLO synthesis |
| `Enforceability` | binding, advisory, aspirational | CLO (Core Legal Ontology) |

### Process Enums

| Enum | Values | Source |
|---|---|---|
| `ProcessType` | negotiation, mediation_facilitative, mediation_evaluative, mediation_transformative, mediation_narrative, arbitration, adjudication, investigation, grievance_procedure, ombuds, conciliation, early_neutral_evaluation, online_dispute_resolution | ADR taxonomy synthesis |
| `ResolutionApproach` | interest_based, rights_based, power_based | Ury/Brett/Goldberg: Getting Disputes Resolved |
| `ProcessStatus` | pending, active, suspended, completed, abandoned, appealed | ADR lifecycle synthesis |
| `ProcessStage` | intake, dialogue, evaluation, resolution, implementation | Process lifecycle |
| `Formality` | informal, semi_formal, formal | Process formality level |

### Outcome Enums

| Enum | Values | Source |
|---|---|---|
| `OutcomeType` | agreement, settlement, award, judgment, consent_order, withdrawal, no_resolution, ceasefire, peace_agreement, transformation, acquiescence | Multi-domain synthesis |
| `Durability` | temporary, durable, permanent | Peace research (positive vs negative peace) |

### Emotion Enums

| Enum | Values | Source |
|---|---|---|
| `PrimaryEmotion` | joy, trust, fear, surprise, sadness, disgust, anger, anticipation | Plutchik wheel of emotions |
| `EmotionIntensity` | low, medium, high | Plutchik intensity gradient |

**`PrimaryEmotion` properties:**

- `opposite` -- returns the Plutchik opposite: joy/sadness, trust/disgust, fear/anger, surprise/anticipation
- `dyads()` -- class method returning 8 primary dyads: optimism (anticipation+joy), love (joy+trust), submission (trust+fear), awe (fear+surprise), disapproval (surprise+sadness), remorse (sadness+disgust), contempt (disgust+anger), aggressiveness (anger+anticipation)

### Narrative Enums

| Enum | Values | Source |
|---|---|---|
| `NarrativeType` | dominant, alternative, counter, subjugated | Winslade & Monk: Narrative Mediation |
| `FrameType` | identity, characterization, power, risk, loss_gain, moral | Dewulf frame classification |

### Conflict Mode Enum

| Enum | Values | Source |
|---|---|---|
| `ConflictMode` | competing, collaborating, compromising, avoiding, accommodating | Thomas-Kilmann Conflict Mode Instrument |

**`ConflictMode` properties:**

- `assertiveness` -- high (competing, collaborating), medium (compromising), low (avoiding, accommodating)
- `cooperativeness` -- high (collaborating, accommodating), medium (compromising), low (competing, avoiding)

### Power Enums

| Enum | Values | Source |
|---|---|---|
| `PowerDomain` | coercive, economic, political, informational, positional, referent, legitimate, expert | French & Raven + Ury/Brett/Goldberg |
| `PowerDirection` | a_over_b, b_over_a, symmetric | Power asymmetry direction |

### Role / Location / Evidence Enums

| Enum | Values | Source |
|---|---|---|
| `RoleType` | claimant, respondent, mediator, arbitrator, judge, witness, advocate, aggressor, target, bystander, facilitator, perpetrator, victim, ally, neutral, guarantor, spoiler, peacemaker | Multi-domain synthesis |
| `LocationType` | point, building, city, district, region, country, global | Geographic hierarchy |
| `EvidenceType` | document, testimony, expert_opinion, digital_record, physical, statistical | Evidence classification |
| `TrustBasis` | calculus, knowledge, identification | Lewicki & Bunker trust stages |

### Edge-Specific Enums

| Enum | Values | Source |
|---|---|---|
| `Side` | side_a, side_b, third_party, observer | UCDP convention |
| `CausalMechanism` | escalation, retaliation, contagion, spillover, provocation, precedent | Causal mechanism for CAUSED edges |
| `AllianceFormality` | formal, tacit | Alliance formality for ALLIED_WITH edges |

---

## Tier System

Three progressive tiers control ontology exposure. Each tier is cumulative -- Standard
includes everything in Essential, and Full includes everything in Standard.

| Tier | Nodes | Edges | Use Case |
|---|---|---|---|
| **Essential** (7 nodes, 6 edges) | Actor, Conflict, Event, Issue, Process, Outcome, Location | PARTY_TO, PARTICIPATES_IN, PART_OF, AT_LOCATION, RESOLVED_THROUGH, PRODUCES | Quick conflict mapping: actors, events, locations, resolution processes |
| **Standard** (12 nodes, 13 edges) | + Interest, Norm, Narrative, Evidence, Role | + HAS_INTEREST, GOVERNED_BY, VIOLATES, ABOUT, EVIDENCED_BY, WITHIN, MEMBER_OF | Structured analysis: interests, norms, narratives, evidence, roles, Glasl/Kriesberg staging |
| **Full** (15 nodes, 20 edges) | + EmotionalState, TrustState, PowerDynamic | + EXPERIENCES, TRUSTS, PROMOTES, HAS_POWER_OVER, ALLIED_WITH, OPPOSED_TO, CAUSED | Complete neurosymbolic intelligence: emotion tracking, trust assessment, power analysis, causal reasoning |

### Feature Flags by Tier

- **Essential:** conflict_mapping, event_timeline, actor_identification, spatial_mapping, process_tracking, outcome_recording
- **Standard:** + interest_analysis, norm_compliance, narrative_analysis, evidence_linking, role_assignment, glasl_escalation, kriesberg_lifecycle
- **Full:** + emotion_tracking, trust_assessment, power_analysis, alliance_detection, causal_reasoning, neurosymbolic_inference, plutchik_wheel, french_raven_power, mayer_trust_model

Helper functions: `get_available_nodes(tier)`, `get_available_edges(tier)`, `get_available_features(tier)`.

---

## Theory Frameworks (15)

All 15 frameworks inherit from `TheoryFramework` (ABC) and implement three core methods:

- `describe()` -- returns a human-readable description
- `assess(graph_context)` -- analyzes a conflict context dict and returns structured findings
- `score(graph_context)` -- returns a `[0.0, 1.0]` relevance/applicability score

Supporting dataclasses: `TheoryConcept`, `ConflictSnapshot`, `TheoryAssessment`, `Intervention`, `DiagnosticQuestion`.

| # | Framework | Author | Key Concepts | `assess()` Computes |
|---|---|---|---|---|
| 1 | **Glasl Escalation Model** | Friedrich Glasl | escalation_stages, win_win, win_lose, lose_lose, de_escalation, intervention_threshold | Current escalation stage (1-9), level classification, recommended intervention type, de-escalation potential |
| 2 | **Fisher-Ury Principled Negotiation** | Roger Fisher & William Ury | positions_vs_interests, batna, zopa, objective_criteria, mutual_gain, separate_people_problem | Position/interest gap analysis, ZOPA computation from BATNA/reservation values, objective criteria presence, recommendations |
| 3 | **Kriesberg Conflict Lifecycle** | Louis Kriesberg | conflict_lifecycle, latent_conflict, emergence, escalation, stalemate, de_escalation, settlement, post_conflict_transformation | Phase classification across 7 lifecycle stages, phase transition readiness, transformation indicators |
| 4 | **Galtung Violence Triangle & Peace Theory** | Johan Galtung | direct_violence, structural_violence, cultural_violence, negative_peace, positive_peace, violence_triangle, conflict_transformation | Violence type decomposition (direct/structural/cultural), peace quality assessment (negative vs positive), transformation pathways |
| 5 | **Lederach Conflict Transformation** | John Paul Lederach | nested_paradigm, micro_level, meso_level, macro_level, moral_imagination, conflict_transformation, web_of_relationships | Scale-level analysis across micro/meso/macro, relationship web mapping, transformation readiness, moral imagination indicators |
| 6 | **Zartman Ripeness Theory** | I. William Zartman | ripeness, mutually_hurting_stalemate, mutually_enticing_opportunity, way_out, ripe_moment, negotiation_readiness | Stalemate pain assessment, mutually hurting stalemate detection, way-out perception, ripeness scoring |
| 7 | **Deutsch Cooperation-Competition Theory** | Morton Deutsch | cooperation, competition, goal_interdependence, crude_law, constructive_controversy, trust, promotive_interaction | Goal interdependence classification (cooperative/competitive/mixed), crude law of social relations application, trust trajectory |
| 8 | **Thomas-Kilmann Conflict Mode Instrument** | Kenneth Thomas & Ralph Kilmann | competing, collaborating, compromising, avoiding, accommodating, assertiveness, cooperativeness | Dominant conflict mode classification on the assertiveness x cooperativeness grid, mode appropriateness assessment |
| 9 | **French-Raven Bases of Social Power** | John French & Bertram Raven | coercive_power, reward_power, legitimate_power, expert_power, referent_power, informational_power, power_asymmetry | Power base identification across 6 types, asymmetry measurement, power balance assessment, legitimacy scoring |
| 10 | **Mayer-Davis-Schoorman Trust Model** | Roger Mayer, James Davis & F. David Schoorman | ability, benevolence, integrity, propensity_to_trust, trustworthiness, vulnerability, risk_taking_in_relationships | Trust decomposition into ability/benevolence/integrity components, overall trust computation, trust trajectory |
| 11 | **Plutchik Wheel of Emotions** | Robert Plutchik | primary_emotions, emotion_opposites, primary_dyads, secondary_dyads, tertiary_dyads, emotion_intensity, emotion_wheel | Emotion classification across 8 primaries, opposite detection, dyad identification, intensity scaling, emotional trajectory |
| 12 | **Pearl Causal Hierarchy** | Judea Pearl | association, intervention, counterfactual, causal_model, do_calculus, confounding, ladder_of_causation | Causal chain analysis across 3 hierarchy levels (association/intervention/counterfactual), confounder identification, do-calculus applicability |
| 13 | **Winslade-Monk Narrative Mediation** | John Winslade & Gerald Monk | dominant_narrative, alternative_narrative, counter_narrative, subjugated_narrative, externalisation, deconstruction, re_authoring, double_listening | Narrative landscape mapping (dominant/alternative/counter/subjugated), externalisation opportunities, re-authoring potential |
| 14 | **Ury-Brett-Goldberg Dispute Resolution** | William Ury, Jeanne Brett & Stephen Goldberg | interests_based, rights_based, power_based, dispute_system_design, loop_back, motivation | Dispute approach classification (interests/rights/power), loop-back opportunity detection, system design recommendations |
| 15 | **Burton Basic Human Needs** | John Burton | basic_human_needs, security, identity, recognition, participation, deep_rooted_conflict, needs_vs_interests, problem_solving_workshop | Unmet needs identification (security, identity, recognition, participation), deep-rootedness assessment, problem-solving workshop suitability |

---

## Compatibility Mappers

Four bidirectional mappers enable data exchange with established conflict datasets.
All live in `dialectica_ontology.compatibility`.

### PLOVER Mapper

Maps DIALECTICA `EventType` to/from PLOVER event codes. Provides `QuadClass` computation.

| Function | Direction | Description |
|---|---|---|
| `plover_to_dialectica(code)` | PLOVER -> ACO | Convert PLOVER event code to `EventType` |
| `dialectica_to_plover(event_type)` | ACO -> PLOVER | Convert `EventType` to PLOVER code |
| `plover_quadclass(code)` | PLOVER -> QuadClass | Get `QuadClass` for a PLOVER code |
| `event_type_quadclass(event_type)` | ACO -> QuadClass | Get `QuadClass` for an `EventType` |

### ACLED Mapper

Maps DIALECTICA events and actors to/from ACLED coding.

| Function | Direction | Description |
|---|---|---|
| `acled_to_dialectica(acled_event)` | ACLED -> ACO | Convert ACLED event dict to DIALECTICA model |
| `dialectica_to_acled(event)` | ACO -> ACLED | Convert DIALECTICA Event to ACLED format |
| `acled_actor_to_dialectica(acled_actor)` | ACLED -> ACO | Convert ACLED actor to `ActorType` |
| `dialectica_actor_to_acled(actor)` | ACO -> ACLED | Convert `ActorType` to ACLED actor class |

### CAMEO Mapper

Maps DIALECTICA events to/from CAMEO (Conflict and Mediation Event Observations).

| Function | Direction | Description |
|---|---|---|
| `cameo_to_dialectica(cameo_code)` | CAMEO -> ACO | Convert CAMEO code to DIALECTICA mapping |
| `dialectica_to_cameo(event_type)` | ACO -> CAMEO | Convert `EventType` to CAMEO code range |
| `cameo_event_to_dialectica(cameo_event)` | CAMEO -> ACO | Convert full CAMEO event record |
| `dialectica_to_cameo_event(event)` | ACO -> CAMEO | Convert DIALECTICA Event to CAMEO record |

### UCDP Mapper

Maps DIALECTICA conflict attributes to/from UCDP (Uppsala Conflict Data Program).

| Function | Direction | Description |
|---|---|---|
| `ucdp_to_dialectica_incompatibility(ucdp_type)` | UCDP -> ACO | Convert UCDP incompatibility code to `Incompatibility` |
| `dialectica_to_ucdp_incompatibility(incomp)` | ACO -> UCDP | Convert `Incompatibility` to UCDP code |
| `ucdp_to_dialectica_intensity(ucdp_intensity)` | UCDP -> ACO | Convert UCDP intensity level to `Intensity` |
| `ucdp_conflict_type_to_domain(ucdp_type)` | UCDP -> ACO | Convert UCDP conflict type to `ConflictDomain` |
| `ucdp_conflict_type_to_violence(ucdp_type)` | UCDP -> ACO | Convert UCDP conflict type to `ViolenceType` |
| `ucdp_conflict_type_label(ucdp_type)` | UCDP -> label | Human-readable label for UCDP conflict type |

---

## Validation

Four validation functions in `validators.py` enforce structural constraints:

| Function | Input | What It Checks |
|---|---|---|
| `validate_relationship_types(rel)` | `ConflictRelationship` | Source/target label constraints from `EDGE_SCHEMA`. Verifies source_label is in allowed source set and target_label is in allowed target set for the given edge type. Checks required properties exist. |
| `validate_subgraph(nodes, rels)` | `list[ConflictNode]`, `list[ConflictRelationship]` | Full structural validation: (1) every relationship's source_id and target_id reference nodes in the graph, (2) every relationship passes schema validation. |
| `validate_temporal_consistency(rels, timestamps)` | `list[ConflictRelationship]`, `dict[str, datetime]` | For `CAUSED` edges only: verifies that the source event timestamp precedes the target event timestamp (cause must precede effect). |
| `validate_tier_compliance(nodes, rels, tier)` | `list[ConflictNode]`, `list[ConflictRelationship]`, `OntologyTier` | Verifies that all node labels and edge types used in the graph are permitted at the specified tier. |

All validators return `list[str]` -- an empty list means the input is valid; each string
is a human-readable error message.

---

## Schema Generation

Five generators in `schemas.py` produce database schemas and serialisation formats from
the canonical Pydantic models:

| Generator | Output | Target System |
|---|---|---|
| `generate_cypher_ddl()` | Cypher `CREATE CONSTRAINT` + `CREATE INDEX` | Neo4j / FalkorDB |
| `generate_spanner_ddl()` | `CREATE TABLE` statements | Google Cloud Spanner |
| `generate_gql_schema()` | GQL `CREATE OR REPLACE PROPERTY GRAPH` | Spanner Graph |
| `generate_json_schema()` | JSON Schema with `$defs` for all 15 node types | API validation |
| `generate_turtle()` | OWL/Turtle with classes, datatype properties, object properties | RDF interoperability |

**Cypher DDL details:**
- Uniqueness constraint on `id` for all 15 node labels
- Indexed properties: Actor (name, actor_type), Conflict (domain, status, glasl_stage, started_at, domain+status), Event (event_type, occurred_at, severity, event_type+occurred_at)

**Spanner DDL details:**
- One table per node type with columns derived from Pydantic field annotations
- A `Relationship` table for all edges with columns: id, type, source_id, target_id, source_label, target_label, workspace_id, tenant_id, properties (JSON), weight, confidence, temporal_start, temporal_end, source_text
- Python-to-Spanner type mapping: `str` -> STRING(MAX), `float` -> FLOAT64, `int` -> INT64, `bool` -> BOOL, `datetime` -> TIMESTAMP, `list[X]` -> ARRAY, `dict` -> JSON

**Turtle details:**
- Namespace: `https://dialectica.ai/ontology#` (prefix: `dia`)
- OWL classes for each node type
- Datatype properties for all fields (shared base + type-specific)
- Object properties for all 20 edge types with domain/range constraints

---

## Quick Start

```python
from datetime import datetime
from dialectica_ontology.primitives import Actor, Conflict, Event
from dialectica_ontology.relationships import ConflictRelationship, EdgeType
from dialectica_ontology.enums import (
    ActorType, ConflictScale, ConflictDomain, ConflictStatus, EventType, QuadClass,
)
from dialectica_ontology.validators import validate_subgraph

# Create actors
party_a = Actor(
    name="Acme Corp",
    actor_type=ActorType.ORGANIZATION,
    org_type="corporation",
    sector="technology",
)
party_b = Actor(
    name="Workers Union Local 42",
    actor_type=ActorType.ORGANIZATION,
    org_type="union",
)

# Create a conflict
dispute = Conflict(
    name="Acme-Union Contract Dispute 2026",
    scale=ConflictScale.MESO,
    domain=ConflictDomain.WORKPLACE,
    status=ConflictStatus.ACTIVE,
    glasl_stage=4,  # auto-derives glasl_level = "win_lose"
)

# Create an event
strike = Event(
    event_type=EventType.PROTEST,
    quad_class=QuadClass.MATERIAL_CONFLICT,
    severity=0.6,
    occurred_at=datetime(2026, 3, 15),
    description="Workers begin 48-hour strike over contract terms",
)

# Wire the graph with relationships
edges = [
    ConflictRelationship(
        type=EdgeType.PARTY_TO,
        source_id=party_a.id, source_label="Actor",
        target_id=dispute.id, target_label="Conflict",
        properties={"side": "side_a"},
    ),
    ConflictRelationship(
        type=EdgeType.PARTY_TO,
        source_id=party_b.id, source_label="Actor",
        target_id=dispute.id, target_label="Conflict",
        properties={"side": "side_b"},
    ),
    ConflictRelationship(
        type=EdgeType.PART_OF,
        source_id=strike.id, source_label="Event",
        target_id=dispute.id, target_label="Conflict",
    ),
    ConflictRelationship(
        type=EdgeType.PARTICIPATES_IN,
        source_id=party_b.id, source_label="Actor",
        target_id=strike.id, target_label="Event",
        properties={"role_type": "organizer"},
    ),
]

# Validate the subgraph
nodes = [party_a, party_b, dispute, strike]
errors = validate_subgraph(nodes, edges)
assert errors == [], f"Validation errors: {errors}"

# Access auto-derived properties
assert dispute.glasl_level == "win_lose"
print(f"Conflict '{dispute.name}' at Glasl stage {dispute.glasl_stage} ({dispute.glasl_level})")
```

---

## File Index

| File | Description |
|---|---|
| `primitives.py` | 15 node types + `ConflictNode` base + `NODE_TYPES` registry |
| `relationships.py` | `ConflictRelationship` base + `EdgeType` enum + `EDGE_SCHEMA` + `validate_relationship()` |
| `enums.py` | 30+ `StrEnum` classes with computed properties |
| `tiers.py` | `OntologyTier` enum + tier node/edge/feature mappings + helpers |
| `theory/__init__.py` | 15 framework imports |
| `theory/base.py` | `TheoryFramework` ABC + supporting dataclasses |
| `theory/*.py` | Individual framework implementations |
| `compatibility/__init__.py` | 4 mapper imports |
| `compatibility/plover.py` | PLOVER event code mapping |
| `compatibility/acled.py` | ACLED event/actor mapping |
| `compatibility/cameo.py` | CAMEO event code mapping |
| `compatibility/ucdp.py` | UCDP conflict type/intensity mapping |
| `validators.py` | 4 validation functions |
| `schemas.py` | 5 DDL/schema generators |
