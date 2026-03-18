# DIALECTICA Theory Frameworks

DIALECTICA implements 15 conflict resolution theory frameworks as executable
Python modules. Each framework inherits from `TheoryFramework` (defined in
`packages/ontology/src/dialectica_ontology/theory/base.py`) and implements
three core methods: `describe()`, `assess()`, and `score()`.

Source directory: `packages/ontology/src/dialectica_ontology/theory/`

---

## Base Architecture

All 15 frameworks share a common abstract base class:

```
TheoryFramework(ABC)
  .name: str
  .author: str
  .key_concepts: list[str]
  .describe() -> str            # Human-readable description
  .assess(graph_context) -> dict # Structured assessment from graph data
  .score(graph_context) -> float # Relevance score 0.0-1.0
  .get_concepts() -> list[TheoryConcept]
  .get_diagnostic_questions() -> list[DiagnosticQuestion]
```

Supporting data classes: `TheoryConcept`, `ConflictSnapshot`, `TheoryAssessment`,
`Intervention`, `DiagnosticQuestion`.

---

## 1. Galtung Violence Triangle and Peace Theory

**File:** `galtung.py` | **Class:** `GaltungFramework`

**Author:** Johan Galtung

**Source:** Galtung, J. (1969). "Violence, Peace, and Peace Research."
*Journal of Peace Research*, 6(3), 167-191. Galtung, J. (1990). "Cultural
Violence." *Journal of Peace Research*, 27(3), 291-305.

**Key concepts:** direct_violence, structural_violence, cultural_violence,
negative_peace, positive_peace, violence_triangle, conflict_transformation

**What `assess()` computes:**
- Severity rating (0.0-1.0) for each violence type (direct, structural, cultural) using keyword matching against type-specific indicator sets and explicit severity scores
- Peace type classification: positive (all violence low), negative (direct violence low but structural/cultural persist), or none (active violence)
- Dominant violence type identification
- Targeted recommendations based on which violence types exceed thresholds (direct > 0.5, structural > 0.3, cultural > 0.3)

**What `score()` returns:** Proportion of available violence-related signals present in context (explicit violence scores, keywords/indicators, issues). Range 0.0-1.0.

**Diagnostic questions:**
1. Is there physical violence or threat of physical harm? (boolean)
2. Are there institutional or systemic inequalities affecting the parties? (open)
3. Are there cultural beliefs, narratives, or ideologies that justify the conflict? (open)

---

## 2. Glasl Escalation Model

**File:** `glasl.py` | **Class:** `GlaslFramework`

**Author:** Friedrich Glasl

**Source:** Glasl, F. (1982). *The Process of Conflict Escalation and Roles
of Third Parties.* In Bomers, G.B.J. and Peterson, R.B. (eds.), *Conflict
Management and Industrial Relations*. Kluwer-Nijhoff. Glasl, F. (1999).
*Confronting Conflict.* Hawthorn Press.

**Key concepts:** escalation_stages, win_win, win_lose, lose_lose,
de_escalation, intervention_threshold

**9-stage model:**

| Stage | Name | Level | Intervention |
|---|---|---|---|
| 1 | Hardening | win-win | Moderation |
| 2 | Debate and Polemics | win-win | Process consultation |
| 3 | Actions Not Words | win-win | Process consultation |
| 4 | Images and Coalitions | win-lose | Socio-therapeutic process |
| 5 | Loss of Face | win-lose | Mediation |
| 6 | Strategies of Threats | win-lose | Mediation |
| 7 | Limited Destructive Blows | lose-lose | Arbitration |
| 8 | Fragmentation of the Enemy | lose-lose | Power intervention |
| 9 | Together into the Abyss | lose-lose | Power intervention |

**What `assess()` computes:**
- Stage detection via keyword overlap against per-stage indicator sets, adjusted by behavioural flags (violence_present, dehumanisation, threats) and intensity-based floor
- Level classification (win-win, win-lose, lose-lose)
- Intervention recommendation calibrated to detected stage
- Prognosis based on level

**What `score()` returns:** Proportion of escalation-related signals present (keywords, intensity, violence, threats, parties >= 2). Range 0.0-1.0.

**Diagnostic questions:**
1. How would you describe the current intensity of the conflict on a scale of 1-10? (scale)
2. Are parties still willing to talk directly to each other? (boolean)
3. Have there been any threats, ultimatums, or acts of coercion? (boolean)

---

## 3. Lederach Conflict Transformation

**File:** `lederach.py` | **Class:** `LederachFramework`

**Author:** John Paul Lederach

**Source:** Lederach, J.P. (1997). *Building Peace: Sustainable Reconciliation
in Divided Societies.* United States Institute of Peace Press. Lederach, J.P.
(2005). *The Moral Imagination: The Art and Soul of Building Peace.* Oxford
University Press.

**Key concepts:** nested_paradigm, micro_level, meso_level, macro_level,
moral_imagination, conflict_transformation, web_of_relationships

**Three nested levels:**

| Level | Name | Actors | Intervention |
|---|---|---|---|
| Micro | Personal/Individual | Individuals, families | Counselling, dialogue |
| Meso | Relational/Community | Community leaders, groups | Community dialogue, mediation |
| Macro | Structural/Systemic | Governments, institutions | Policy reform, peace agreements |

**What `assess()` computes:**
- Primary conflict level via keyword matching, explicit scope, and party count heuristics (> 10 parties elevates to macro, > 3 to meso)
- Moral imagination assessment: high/moderate/low based on presence of creativity, vision, empathy, reconciliation keywords
- Multi-level analysis showing relevance at all three levels simultaneously

**What `score()` returns:** Proportion of level-related signals (keywords, scope/num_parties, actors/parties, history). Range 0.0-1.0.

**Diagnostic questions:**
1. Is this conflict primarily personal, community-level, or systemic? (choice)
2. Can the parties envision a future where they coexist constructively? (open)

---

## 4. Zartman Ripeness Theory

**File:** `zartman.py` | **Class:** `ZartmanFramework`

**Author:** I. William Zartman

**Source:** Zartman, I.W. (1989). "Ripe for Resolution: Conflict and
Intervention in Africa." Oxford University Press. Zartman, I.W. (2000).
"Ripeness: The Hurting Stalemate and Beyond." In Stern, P. and Druckman, D.
(eds.), *International Conflict Resolution After the Cold War.* National
Academies Press.

**Key concepts:** ripeness, mutually_hurting_stalemate, mutually_enticing_opportunity,
way_out, ripe_moment, negotiation_readiness

**What `assess()` computes:**
- MHS detection: stalemate + mutual_costs flags, bilateral pain levels > 0.6, exhaustion flag, or keyword overlap (stalemate, impasse, deadlock, etc.)
- MEO detection: opportunity + mutual_benefit flags, external_incentive, or keyword overlap (opportunity, mutual_gain, incentive, etc.)
- Way-out perception: proposed_solution flag or keywords (proposal, mediator, etc.)
- Ripeness determination: ripe = (MHS or MEO) and way_out
- Qualitative assessment string covering all combinations

**What `score()` returns:** Proportion of ripeness-related data fields present. Range 0.0-1.0.

**Diagnostic questions:**
1. Do both parties feel that continuing the conflict is too costly? (boolean)
2. Is there a potential outcome that both parties would find attractive? (open)
3. Do the parties see a viable path to resolution? (boolean)

---

## 5. Fisher-Ury Principled Negotiation

**File:** `fisher_ury.py` | **Class:** `FisherUryFramework`

**Author:** Roger Fisher and William Ury

**Source:** Fisher, R. and Ury, W. (1981). *Getting to Yes: Negotiating
Agreement Without Giving In.* Houghton Mifflin. Fisher, R., Ury, W. and
Patton, B. (2011). *Getting to Yes* (3rd edition). Penguin.

**Key concepts:** positions_vs_interests, batna, zopa, objective_criteria,
mutual_gain, separate_people_problem

**What `assess()` computes:**
- Positions vs. interests detection: classifies stance as interest_focused, position_locked, mixed, or unclear
- ZOPA computation: party_b_reservation - party_a_reservation; positive = agreement possible
- BATNA strength assessment: keyword heuristic classifying each party's alternative as strong, moderate, or weak
- Objective criteria presence check

**What `score()` returns:** Proportion of negotiation-related data fields (positions/interests, reservation values, BATNAs, criteria, parties >= 2). Range 0.0-1.0.

**Diagnostic questions:**
1. What does each party really want, beyond what they are asking for? (open)
2. What is each party's best alternative if no agreement is reached? (open)
3. Are there objective standards both parties would accept as fair? (open)

---

## 6. French-Raven Bases of Social Power

**File:** `french_raven.py` | **Class:** `FrenchRavenFramework`

**Author:** John French and Bertram Raven

**Source:** French, J.R.P. and Raven, B.H. (1959). "The Bases of Social
Power." In Cartwright, D. (ed.), *Studies in Social Power.* Institute for
Social Research. Raven, B.H. (1965). "Social Influence and Power." In
Steiner, I.D. and Fishbein, M. (eds.), *Current Studies in Social Psychology.*

**Key concepts:** coercive_power, reward_power, legitimate_power, expert_power,
referent_power, informational_power, power_asymmetry

**Six power bases:**

| Base | Source | Effect |
|---|---|---|
| Coercive | Ability to punish | Compliance through fear |
| Reward | Ability to provide rewards | Compliance through incentive |
| Legitimate | Formal authority/position | Compliance based on accepted authority |
| Expert | Knowledge/skills | Influence through credibility |
| Referent | Charisma/identification | Influence through admiration |
| Informational | Control of information | Influence through selective sharing |

**What `assess()` computes:**
- Per-base detection via keyword matching and explicit party power assignments
- Power asymmetry classification: party_a_dominant, party_b_dominant, relatively_balanced, or unclear
- Targeted recommendations for asymmetry and coercive power situations

**What `score()` returns:** Proportion of power-related data present. Range 0.0-1.0.

**Diagnostic questions:**
1. What sources of power does each party hold? (open)
2. Is there a significant power imbalance between the parties? (boolean)

---

## 7. Thomas-Kilmann Conflict Mode Instrument

**File:** `thomas_kilmann.py` | **Class:** `ThomasKilmannFramework`

**Author:** Kenneth Thomas and Ralph Kilmann

**Source:** Thomas, K.W. and Kilmann, R.H. (1974). *Thomas-Kilmann Conflict
Mode Instrument.* Xicom. Thomas, K.W. (1992). "Conflict and Conflict
Management." In Dunnette, M.D. (ed.), *Handbook of Industrial and
Organizational Psychology.* Rand McNally.

**Key concepts:** competing, collaborating, compromising, avoiding,
accommodating, assertiveness, cooperativeness

**Five modes mapped to two dimensions:**

| Mode | Assertiveness | Cooperativeness |
|---|---|---|
| Competing | High | Low |
| Collaborating | High | High |
| Compromising | Medium | Medium |
| Avoiding | Low | Low |
| Accommodating | Low | High |

**What `assess()` computes:**
- Mode recommendation based on issue_importance, relationship_importance, time_pressure, and power_balance
- Decision logic: high issue + high relationship = collaborating; high issue + low relationship = competing; etc.
- Full mode comparison table with assertiveness/cooperativeness ratings

**What `score()` returns:** Proportion of mode-selection inputs present. Range 0.0-1.0.

**Diagnostic questions:**
1. How important is the issue at stake to you (1-10)? (scale)
2. How important is maintaining the relationship with the other party (1-10)? (scale)
3. Is there significant time pressure to resolve this conflict? (boolean)

---

## 8. Burton Basic Human Needs

**File:** `burton.py` | **Class:** `BurtonFramework`

**Author:** John Burton

**Source:** Burton, J. (1990). *Conflict: Resolution and Provention.* Macmillan.
Burton, J. (1997). *Violence Explained.* Manchester University Press.

**Key concepts:** basic_human_needs, security, identity, recognition,
participation, deep_rooted_conflict, needs_vs_interests, problem_solving_workshop

**Four basic needs:**

| Need | Description | Denial indicators |
|---|---|---|
| Security | Physical safety and predictability | Threat, violence, instability, persecution |
| Identity | Sense of self and group belonging | Assimilation pressure, cultural suppression |
| Recognition | Acknowledgment of worth and status | Marginalisation, exclusion, humiliation |
| Participation | Ability to influence decisions | Disenfranchisement, autocracy, silencing |

**What `assess()` computes:**
- Per-need satisfaction rating and denial detection via explicit status values and keyword matching against denial indicators
- Conflict depth classification: deep_rooted (if any needs denied) vs. surface
- Need-specific recommendations (e.g., address safety before substantive negotiation)

**What `score()` returns:** Proportion of the 4 needs that are detected as denied (0-4 mapped to 0.0-1.0).

---

## 9. Kriesberg Conflict Lifecycle

**File:** `kriesberg.py` | **Class:** `KriesbergFramework`

**Author:** Louis Kriesberg

**Source:** Kriesberg, L. (1998). *Constructive Conflicts: From Escalation
to Resolution.* Rowman and Littlefield. Kriesberg, L. and Dayton, B.W. (2012).
*Constructive Conflicts* (4th edition).

**Key concepts:** conflict_lifecycle, latent_conflict, emergence, escalation,
stalemate, de_escalation, settlement, post_conflict_transformation

**Seven lifecycle phases:**

| Phase | Description | Intervention |
|---|---|---|
| Latent | Underlying conditions exist | Early prevention |
| Emergence | Awareness of incompatible goals | Dialogue before positions harden |
| Escalation | Intensifying hostility | De-escalation, mediation |
| Stalemate | Neither party can prevail | Ripeness assessment |
| De-escalation | Reducing hostilities | Support negotiation, build trust |
| Settlement | Agreement reached | Ensure root causes addressed |
| Post-conflict | Rebuilding after settlement | Transitional justice, reconciliation |

**What `assess()` computes:**
- Phase detection via explicit flags (post_conflict, agreement_reached, negotiation_active), keyword matching, and violence level heuristics
- Phase index (0-6) and trajectory classification: escalating (phases 0-2), stalled (phase 3), de-escalating (phases 4-6)
- Phase-appropriate intervention recommendation

**What `score()` returns:** Proportion of lifecycle-related signals present. Range 0.0-1.0.

**Diagnostic questions:**
1. How long has this conflict been ongoing, and how has it changed over time? (open)
2. Are the parties currently engaged in any form of negotiation or dialogue? (boolean)

---

## 10. Deutsch Cooperation-Competition Theory

**File:** `deutsch.py` | **Class:** `DeutschFramework`

**Author:** Morton Deutsch

**Source:** Deutsch, M. (1949). "A Theory of Co-operation and Competition."
*Human Relations*, 2(2), 129-152. Deutsch, M. (1973). *The Resolution of
Conflict.* Yale University Press.

**Key concepts:** cooperation, competition, goal_interdependence, crude_law,
constructive_controversy, trust, promotive_interaction

**Four interaction types:** cooperative, competitive, mixed_motive, individualistic

**What `assess()` computes:**
- Interaction type classification via cooperation_signals, competition_signals, trust_level, communication_quality, and keyword matching
- Application of Deutsch's Crude Law: cooperative processes breed cooperation; competitive processes breed competition
- Type-specific dynamics and predicted outcomes
- Tailored recommendations (e.g., reframe zero-sum, build trust via small cooperative gestures)

**What `score()` returns:** Proportion of cooperation/competition data present. Range 0.0-1.0.

**Diagnostic questions:**
1. Do the parties see their goals as linked? (open)
2. How would you characterise the communication: open, guarded, or hostile? (choice)

---

## 11. Mayer-Davis-Schoorman Trust Model

**File:** `mayer_trust.py` | **Class:** `MayerTrustFramework`

**Author:** Roger Mayer, James Davis, and F. David Schoorman

**Source:** Mayer, R.C., Davis, J.H. and Schoorman, F.D. (1995). "An
Integrative Model of Organizational Trust." *Academy of Management Review*,
20(3), 709-734.

**Key concepts:** ability, benevolence, integrity, propensity_to_trust,
trustworthiness, vulnerability, risk_taking_in_relationships

**What `assess()` computes:**
- Trust score = ((ability + benevolence + integrity) / 3) * (0.5 + 0.5 * propensity), clamped to [0, 1]
- Qualitative level: very_low (< 0.2), low (< 0.4), moderate (< 0.6), high (< 0.8), very_high (>= 0.8)
- Component-level analysis identifying the weakest factor
- Targeted recommendations for rebuilding trust via the weakest component

**What `score()` returns:** Proportion of the 4 trust inputs (ability, benevolence, integrity, propensity) present. Range 0.0-1.0.

**Diagnostic questions:**
1. How competent do you believe the other party is in the relevant area (1-10)? (scale)
2. Do you believe the other party genuinely cares about your interests? (boolean)
3. Does the other party consistently follow through on their commitments? (boolean)

---

## 12. Pearl Causal Hierarchy

**File:** `pearl_causal.py` | **Class:** `PearlCausalFramework`

**Author:** Judea Pearl

**Source:** Pearl, J. (2009). *Causality: Models, Reasoning, and Inference.*
Cambridge University Press. Pearl, J. and Mackenzie, D. (2018). *The Book of
Why.* Basic Books.

**Key concepts:** association, intervention, counterfactual, causal_model,
do_calculus, confounding, ladder_of_causation

**Three causal levels (Ladder of Causation):**

| Level | Name | Operator | Question |
|---|---|---|---|
| 1 | Association | P(Y\|X) | What if I observe X? |
| 2 | Intervention | P(Y\|do(X)) | What if I do X? |
| 3 | Counterfactual | P(Y_X\|X',Y') | What if X had been different? |

**What `assess()` computes:**
- Classification of each query and causal claim into one of three levels via keyword matching (counterfactual checked first as most specific)
- Dominant reasoning level identification
- Level-specific conflict application guidance
- Recommendations to deepen reasoning (association -> intervention -> counterfactual)

**What `score()` returns:** Proportion of causal reasoning inputs (queries, causal_claims, reasoning_type) present. Range 0.0-1.0.

**Diagnostic questions:**
1. What causal claims are being made about this conflict (X causes Y)? (open)
2. What would have happened if the conflict had been handled differently at an earlier stage? (open)

---

## 13. Plutchik Wheel of Emotions

**File:** `plutchik.py` | **Class:** `PlutchikFramework`

**Author:** Robert Plutchik

**Source:** Plutchik, R. (1980). *Emotion: A Psychoevolutionary Synthesis.*
Harper and Row. Plutchik, R. (2001). "The Nature of Emotions." *American
Scientist*, 89(4), 344-350.

**Key concepts:** primary_emotions, emotion_opposites, primary_dyads,
secondary_dyads, tertiary_dyads, emotion_intensity, emotion_wheel

**8 primary emotions** (in wheel order): joy, trust, fear, surprise, sadness,
disgust, anger, anticipation

**Opposite pairs:** joy-sadness, trust-disgust, fear-anger, surprise-anticipation

**Primary dyads:** joy+trust=love, trust+fear=submission, fear+surprise=awe,
surprise+sadness=disapproval, sadness+disgust=remorse, disgust+anger=contempt,
anger+anticipation=aggressiveness, anticipation+joy=optimism

**What `assess()` computes:**
- Emotional landscape analysis: which primary emotions are present/absent
- Dyad detection among present emotions (primary, secondary, and tertiary)
- Opposite tension detection (e.g., anger and fear both present)
- Conflict-specific warnings (contempt as relationship breakdown predictor, despair as hopelessness indicator)

**What `score()` returns:** Proportion of primary emotions present (count / 4, capped at 1.0).

**Diagnostic questions:**
1. What primary emotions are each party experiencing? (open)
2. Are there conflicting emotions present within either party? (open)

---

## 14. Ury-Brett-Goldberg Dispute Resolution

**File:** `ury_brett_goldberg.py` | **Class:** `UryBrettGoldbergFramework`

**Author:** William Ury, Jeanne Brett, and Stephen Goldberg

**Source:** Ury, W., Brett, J. and Goldberg, S. (1988). *Getting Disputes
Resolved: Designing Systems to Cut the Costs of Conflict.* Jossey-Bass.

**Key concepts:** interests_based, rights_based, power_based,
dispute_system_design, loop_back, motivation

**Three dispute resolution approaches:**

| Approach | Methods | Cost |
|---|---|---|
| Interests | Negotiation, mediation | Low -- preserves relationships |
| Rights | Arbitration, adjudication | Medium -- may strain relationships |
| Power | Strikes, sanctions, warfare | High -- damages relationships |

**What `assess()` computes:**
- Current approach identification
- Recommended approach: interests first unless negotiation_failed, then rights if clear_rules exist, then power as last resort
- Dispute system health: good (interest-based), moderate (escalated from interests), poor (power without trying interests)
- Loop-back recommendations when power/rights approaches are in use

**What `score()` returns:** Proportion of dispute resolution data present. Range 0.0-1.0.

**Diagnostic questions:**
1. How is this dispute currently being addressed -- through negotiation, rules/law, or force? (choice)
2. Have interest-based negotiation approaches been tried? (boolean)

---

## 15. Winslade-Monk Narrative Mediation

**File:** `winslade_monk.py` | **Class:** `WinsladeMonkFramework`

**Author:** John Winslade and Gerald Monk

**Source:** Winslade, J. and Monk, G. (2000). *Narrative Mediation: A New
Approach to Conflict Resolution.* Jossey-Bass. Winslade, J. and Monk, G.
(2008). *Practicing Narrative Mediation.* Jossey-Bass.

**Key concepts:** dominant_narrative, alternative_narrative, counter_narrative,
subjugated_narrative, externalisation, deconstruction, re_authoring,
double_listening

**Four narrative types:**

| Type | Description |
|---|---|
| Dominant | The prevailing story shaping conflict understanding |
| Alternative | Different perspective that challenges without directly opposing |
| Counter | Directly opposes and seeks to replace dominant narrative |
| Subjugated | Marginalised, silenced, or rendered invisible stories |

**What `assess()` computes:**
- Narrative landscape mapping: classifies each narrative via keyword heuristics or explicit typing
- Gap detection: missing dominant narrative, no alternative/counter narratives, no subjugated narratives
- Recommendations: use double listening, create safe space for subjugated voices, externalise the problem

**What `score()` returns:** Proportion of narrative-related data present. Range 0.0-1.0.

**Diagnostic questions:**
1. What is the dominant story each party tells about this conflict? (open)
2. Are there voices or perspectives that have been silenced or marginalised? (open)
3. Can you think of a different way to tell the story of this conflict? (open)

---

## Framework Registry

All 15 frameworks are exported from `packages/ontology/src/dialectica_ontology/theory/__init__.py`:

| Class | Framework | Author |
|---|---|---|
| `GaltungFramework` | Violence Triangle and Peace Theory | Johan Galtung |
| `GlaslFramework` | Escalation Model | Friedrich Glasl |
| `LederachFramework` | Conflict Transformation | John Paul Lederach |
| `ZartmanFramework` | Ripeness Theory | I. William Zartman |
| `FisherUryFramework` | Principled Negotiation | Roger Fisher and William Ury |
| `FrenchRavenFramework` | Bases of Social Power | John French and Bertram Raven |
| `ThomasKilmannFramework` | Conflict Mode Instrument | Kenneth Thomas and Ralph Kilmann |
| `BurtonFramework` | Basic Human Needs | John Burton |
| `KriesbergFramework` | Conflict Lifecycle | Louis Kriesberg |
| `DeutschFramework` | Cooperation-Competition Theory | Morton Deutsch |
| `MayerTrustFramework` | Trust Model | Roger Mayer, James Davis, F. David Schoorman |
| `PearlCausalFramework` | Causal Hierarchy | Judea Pearl |
| `PlutchikFramework` | Wheel of Emotions | Robert Plutchik |
| `UryBrettGoldbergFramework` | Dispute Resolution | William Ury, Jeanne Brett, Stephen Goldberg |
| `WinsladeMonkFramework` | Narrative Mediation | John Winslade and Gerald Monk |

---

## Using Frameworks in Code

```python
from dialectica_ontology.theory import GlaslFramework, ZartmanFramework

glasl = GlaslFramework()
context = {
    "indicators": {
        "keywords": ["threat", "ultimatum", "polarisation"],
        "intensity": 0.6,
        "violence_present": False,
        "threats": True,
    },
    "parties": ["Government", "Opposition"],
}

assessment = glasl.assess(context)
# {'stage': 6, 'stage_name': 'Strategies of Threats', 'level': 'win-lose', ...}

relevance = glasl.score(context)
# 0.8

questions = glasl.get_diagnostic_questions()
# [DiagnosticQuestion(question='How would you describe...', ...)]
```

The `TheoristAgent` (in `packages/reasoning/`) applies all 15 frameworks to a
workspace graph context and ranks them by applicability score, producing a
cross-framework synthesis accessible via `GET /v1/workspaces/{id}/theory`.
