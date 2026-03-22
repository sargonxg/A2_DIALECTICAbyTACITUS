"use client";

import { useState } from "react";
import Link from "next/link";
import {
  BookOpen,
  ExternalLink,
  ChevronDown,
  ChevronRight,
  ArrowRight,
  Flame,
  Handshake,
  Building2,
  Heart,
} from "lucide-react";

/* ------------------------------------------------------------------ */
/*  Theory data                                                        */
/* ------------------------------------------------------------------ */

interface Theory {
  id: string;
  name: string;
  author: string;
  color: string;
  keyConcepts: string[];
  dialecticaUse: string;
  description: string;
}

interface TheoryGroup {
  category: string;
  subtitle: string;
  icon: React.ElementType;
  color: string;
  theories: Theory[];
}

const THEORY_GROUPS: TheoryGroup[] = [
  {
    category: "Escalation & Dynamics",
    subtitle: "How conflicts grow, shift, and reach turning points",
    icon: Flame,
    color: "#f43f5e",
    theories: [
      {
        id: "glasl",
        name: "Glasl Escalation Model",
        author: "Friedrich Glasl",
        color: "#f43f5e",
        keyConcepts: [
          "9 escalation stages",
          "Win-win (1-3), Win-lose (4-6), Lose-lose (7-9)",
          "Intervention thresholds",
          "Point of no return",
        ],
        dialecticaUse:
          "DIALECTICA tracks Glasl stages via symbolic rules that fire on event sequences. Stage determines which intervention type is appropriate: moderation (1-3), mediation (4-5), or power intervention (7-9). The stage is computed deterministically and cannot be overridden by neural predictions.",
        description:
          "A 9-stage model describing how conflicts escalate from mild tension ('hardening') to mutual destruction ('together into the abyss'). Each stage maps to specific behavioral patterns and appropriate intervention strategies.",
      },
      {
        id: "kriesberg",
        name: "Conflict Lifecycle",
        author: "Louis Kriesberg",
        color: "#06b6d4",
        keyConcepts: [
          "Emergence",
          "Escalation",
          "De-escalation",
          "Termination",
          "Post-conflict recovery",
        ],
        dialecticaUse:
          "Maps the temporal dimension of conflicts. DIALECTICA uses event timestamps and severity tracking to identify which lifecycle phase a conflict is in, enabling phase-appropriate recommendations.",
        description:
          "Models conflicts as dynamic processes that move through predictable phases. Each phase has distinct characteristics and opportunities for intervention.",
      },
      {
        id: "zartman",
        name: "Ripeness Theory",
        author: "I. William Zartman",
        color: "#f59e0b",
        keyConcepts: [
          "Mutually Hurting Stalemate (MHS)",
          "Mutually Enticing Opportunity (MEO)",
          "Way Out",
          "Ripe Moment",
          "Precipice",
        ],
        dialecticaUse:
          "Symbolic rules detect MHS conditions (escalating costs + stalemate indicators) and MEO presence. When both are detected, DIALECTICA flags the conflict as 'ripe for resolution' — a critical signal for mediators and negotiators.",
        description:
          "Conflicts become ready for resolution when parties perceive a Mutually Hurting Stalemate — both sides are suffering and neither can win unilaterally — combined with a perceived Way Out.",
      },
    ],
  },
  {
    category: "Negotiation & Resolution",
    subtitle: "Structured approaches to reaching agreements",
    icon: Handshake,
    color: "#14b8a6",
    theories: [
      {
        id: "fisher_ury",
        name: "Principled Negotiation",
        author: "Roger Fisher & William Ury",
        color: "#14b8a6",
        keyConcepts: [
          "Interests vs. Positions",
          "BATNA (Best Alternative to Negotiated Agreement)",
          "ZOPA (Zone of Possible Agreement)",
          "Objective Criteria",
          "Mutual Gain Options",
        ],
        dialecticaUse:
          "Core to DIALECTICA's interest extraction. The system separates stated positions from underlying interests, identifies BATNA for each party, and maps potential ZOPA. The Interest node type directly implements this framework.",
        description:
          "The foundational interest-based negotiation framework from 'Getting to Yes'. Separates people from problems, focuses on interests not positions, generates options for mutual gain, and insists on objective criteria.",
      },
      {
        id: "thomas_kilmann",
        name: "Conflict Modes",
        author: "Kenneth Thomas & Ralph Kilmann",
        color: "#78716c",
        keyConcepts: [
          "Competing (assertive, uncooperative)",
          "Collaborating (assertive, cooperative)",
          "Compromising (moderate)",
          "Avoiding (unassertive, uncooperative)",
          "Accommodating (unassertive, cooperative)",
        ],
        dialecticaUse:
          "Classifies actor behavior into the five conflict-handling modes based on event analysis. Helps identify whether parties are stuck in competing mode or moving toward collaboration.",
        description:
          "Identifies five distinct approaches to handling conflict based on two dimensions: assertiveness (satisfying own concerns) and cooperativeness (satisfying others' concerns).",
      },
      {
        id: "ury_brett_goldberg",
        name: "Dispute Systems Design",
        author: "William Ury, Jeanne Brett & Stephen Goldberg",
        color: "#64748b",
        keyConcepts: [
          "Interest-based approaches",
          "Rights-based approaches",
          "Power-based approaches",
          "Loop-back mechanisms",
          "System efficiency",
        ],
        dialecticaUse:
          "Evaluates whether a dispute resolution process is using interests, rights, or power approaches. DIALECTICA's Process node tracks the resolution mechanism type and recommends loop-back to interest-based approaches.",
        description:
          "A framework for designing effective dispute resolution systems. Argues that interest-based approaches are most efficient, with rights and power as fallbacks, and systems should include mechanisms to loop back toward interest-based resolution.",
      },
      {
        id: "winslade_monk",
        name: "Narrative Mediation",
        author: "John Winslade & Gerald Monk",
        color: "#ec4899",
        keyConcepts: [
          "Dominant stories",
          "Counter-stories",
          "Externalization",
          "Deconstruction",
          "Re-authoring",
        ],
        dialecticaUse:
          "DIALECTICA's Narrative node type captures the stories and frames parties use. Identifies dominant narratives that sustain conflict and surfaces alternative stories that could enable resolution.",
        description:
          "A social constructionist approach that sees conflicts as embedded in narrative. Mediation involves helping parties deconstruct conflict-saturated stories and co-author new narratives that open space for resolution.",
      },
    ],
  },
  {
    category: "Structural & Cultural",
    subtitle: "Systemic forces and institutions shaping conflict",
    icon: Building2,
    color: "#6366f1",
    theories: [
      {
        id: "galtung",
        name: "Violence Triangle",
        author: "Johan Galtung",
        color: "#6366f1",
        keyConcepts: [
          "Direct violence (behavioral)",
          "Structural violence (systemic inequality)",
          "Cultural violence (legitimizing narratives)",
          "Positive peace vs. negative peace",
        ],
        dialecticaUse:
          "Structures conflict analysis across three violence dimensions. Norm and Narrative nodes capture cultural violence; power asymmetries in Power Dynamic nodes surface structural violence; Event nodes track direct violence.",
        description:
          "Distinguishes three types of violence: direct (physical acts), structural (systemic inequalities built into social structures), and cultural (attitudes and beliefs that legitimize direct and structural violence).",
      },
      {
        id: "lederach",
        name: "Peacebuilding & Transformation",
        author: "John Paul Lederach",
        color: "#ec4899",
        keyConcepts: [
          "Multi-track diplomacy",
          "Nested paradigm (issue, relationship, subsystem, system)",
          "Web of relationships",
          "Moral imagination",
          "20-year vision",
        ],
        dialecticaUse:
          "Frames conflict transformation across multiple levels. DIALECTICA maps the web of actor relationships and identifies intervention points at issue, relationship, and systemic levels simultaneously.",
        description:
          "Focuses on long-term transformation of relationships and social structures. Peacebuilding requires working simultaneously at multiple levels — from grassroots communities to top leadership — across extended timeframes.",
      },
      {
        id: "burton",
        name: "Basic Human Needs",
        author: "John Burton",
        color: "#22c55e",
        keyConcepts: [
          "Identity needs",
          "Security needs",
          "Recognition needs",
          "Participation needs",
          "Non-negotiable needs vs. negotiable interests",
        ],
        dialecticaUse:
          "Links conflicts to unmet fundamental needs. Interest nodes are classified by need type, and symbolic rules detect when core identity or security needs are threatened — indicating deep-rooted conflicts resistant to simple compromise.",
        description:
          "Argues that conflicts arise from unmet basic human needs (identity, security, recognition, participation) that are universal and non-negotiable. Resolution requires satisfying these needs rather than bargaining over positions.",
      },
      {
        id: "deutsch",
        name: "Cooperation & Competition Theory",
        author: "Morton Deutsch",
        color: "#a855f7",
        keyConcepts: [
          "Goal interdependence",
          "Promotive (cooperative) interaction",
          "Contrient (competitive) interaction",
          "Crude law of social relations",
          "Constructive vs. destructive conflict",
        ],
        dialecticaUse:
          "Models whether party dynamics are cooperative or competitive. DIALECTICA's edge analysis (ALLIES_WITH vs. OPPOSES) maps the cooperation-competition spectrum to identify potential for constructive engagement.",
        description:
          "Explores how goal interdependence shapes interaction. Cooperative goal structures lead to constructive processes; competitive structures lead to destructive ones. The 'crude law' states that the characteristics of cooperation/competition tend to be self-reinforcing.",
      },
    ],
  },
  {
    category: "Relational & Emotional",
    subtitle: "Power, trust, emotions, and causal reasoning",
    icon: Heart,
    color: "#f59e0b",
    theories: [
      {
        id: "french_raven",
        name: "Bases of Power",
        author: "John French & Bertram Raven",
        color: "#d946ef",
        keyConcepts: [
          "Legitimate power (authority)",
          "Reward power (incentives)",
          "Coercive power (threats)",
          "Expert power (knowledge)",
          "Referent power (charisma)",
          "Informational power (data)",
        ],
        dialecticaUse:
          "Power Dynamic nodes classify power type using French & Raven taxonomy. Symbolic rules analyze power asymmetries to identify exploitation risk and recommend power-balancing interventions.",
        description:
          "Identifies six bases of social power. Different power sources have different effects on compliance, internalization, and relationship quality. Informational power was added later by Raven as a sixth base.",
      },
      {
        id: "mayer_trust",
        name: "Trust Model",
        author: "Roger Mayer, James Davis & F. David Schoorman",
        color: "#8b5cf6",
        keyConcepts: [
          "Ability (competence)",
          "Benevolence (goodwill)",
          "Integrity (principles)",
          "Propensity to trust",
          "Risk-taking in relationships",
        ],
        dialecticaUse:
          "Trust State nodes track trust across three dimensions (ability, benevolence, integrity). Symbolic rules compute trust trajectories — deteriorating trust triggers early warnings; improving trust signals resolution readiness.",
        description:
          "A three-dimensional model of organizational trust. Trustworthiness = Ability + Benevolence + Integrity, moderated by the trustor's propensity to trust. Trust enables risk-taking in relationships.",
      },
      {
        id: "plutchik",
        name: "Emotion Wheel",
        author: "Robert Plutchik",
        color: "#fb923c",
        keyConcepts: [
          "8 primary emotions (joy, trust, fear, surprise, sadness, disgust, anger, anticipation)",
          "Emotion combinations (e.g., anger + disgust = contempt)",
          "Intensity levels (e.g., annoyance -> anger -> rage)",
          "Emotion dyads",
        ],
        dialecticaUse:
          "Emotional State nodes use Plutchik's taxonomy to classify party emotions. Intensity tracking detects emotional escalation. Combined emotions (like contempt = anger + disgust) surface relationship deterioration.",
        description:
          "A psycho-evolutionary theory proposing 8 primary emotions arranged in opposing pairs. Emotions combine like colors to form complex feelings. Each emotion exists on an intensity continuum.",
      },
      {
        id: "pearl_causal",
        name: "Causal Inference",
        author: "Judea Pearl",
        color: "#3b82f6",
        keyConcepts: [
          "do-calculus",
          "Directed Acyclic Graphs (DAGs)",
          "Counterfactual reasoning",
          "Interventions vs. observations",
          "Structural causal models",
        ],
        dialecticaUse:
          "Applies causal inference to conflict event chains. CAUSED edges form DAGs analyzed for counterfactuals: 'What if event X had not occurred?' This enables scenario planning and root cause analysis beyond correlation.",
        description:
          "A mathematical framework for reasoning about cause and effect. Distinguishes between observation, intervention, and counterfactuals. Enables answering 'what if?' questions about conflict dynamics with formal rigor.",
      },
    ],
  },
];

/* ------------------------------------------------------------------ */
/*  Page                                                               */
/* ------------------------------------------------------------------ */

export default function TheoryPage() {
  const [expandedGroup, setExpandedGroup] = useState<string>(
    THEORY_GROUPS[0].category,
  );
  const [expandedTheory, setExpandedTheory] = useState<string | null>(null);

  const toggleGroup = (category: string) => {
    setExpandedGroup((prev) => (prev === category ? "" : category));
    setExpandedTheory(null);
  };

  const toggleTheory = (id: string) => {
    setExpandedTheory((prev) => (prev === id ? null : id));
  };

  const totalTheories = THEORY_GROUPS.reduce(
    (sum, g) => sum + g.theories.length,
    0,
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-text-primary flex items-center gap-2">
          <BookOpen size={24} className="text-accent" /> Theory Frameworks
        </h1>
        <a
          href="https://tacitus.me"
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs text-text-secondary hover:text-accent transition-colors flex items-center gap-1"
        >
          tacitus.me <ExternalLink size={10} />
        </a>
      </div>

      <p className="text-text-secondary max-w-3xl">
        DIALECTICA integrates{" "}
        <span className="text-accent font-semibold">{totalTheories} conflict resolution theory frameworks</span>{" "}
        spanning four categories. Each framework provides a unique analytical lens — from
        Glasl escalation stages to Pearl causal inference — all operationalized as symbolic
        rules and data structures in the Conflict Grammar ontology.
      </p>

      {/* Category summary cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {THEORY_GROUPS.map((group) => {
          const GroupIcon = group.icon;
          return (
            <button
              key={group.category}
              onClick={() => toggleGroup(group.category)}
              className="card-hover text-left space-y-2"
              style={{
                borderColor:
                  expandedGroup === group.category ? `${group.color}40` : undefined,
              }}
            >
              <GroupIcon size={18} style={{ color: group.color }} />
              <p className="text-sm font-semibold text-text-primary">{group.category}</p>
              <p className="text-xs text-text-secondary">
                {group.theories.length} frameworks
              </p>
            </button>
          );
        })}
      </div>

      {/* Theory groups */}
      <div className="space-y-4">
        {THEORY_GROUPS.map((group) => {
          const GroupIcon = group.icon;
          const isGroupExpanded = expandedGroup === group.category;

          return (
            <div key={group.category} className="card space-y-3">
              <button
                onClick={() => toggleGroup(group.category)}
                className="w-full flex items-center justify-between"
              >
                <div className="flex items-center gap-3">
                  <div
                    className="w-8 h-8 rounded-lg flex items-center justify-center"
                    style={{ backgroundColor: `${group.color}15` }}
                  >
                    <GroupIcon size={16} style={{ color: group.color }} />
                  </div>
                  <div className="text-left">
                    <h3 className="font-semibold text-text-primary">{group.category}</h3>
                    <p className="text-xs text-text-secondary">{group.subtitle}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="badge bg-surface-active text-text-secondary text-[10px]">
                    {group.theories.length}
                  </span>
                  {isGroupExpanded ? (
                    <ChevronDown size={16} className="text-text-secondary" />
                  ) : (
                    <ChevronRight size={16} className="text-text-secondary" />
                  )}
                </div>
              </button>

              {isGroupExpanded && (
                <div className="space-y-3 pt-2">
                  {group.theories.map((theory) => {
                    const isTheoryExpanded = expandedTheory === theory.id;
                    return (
                      <div
                        key={theory.id}
                        className="rounded-lg border border-border bg-background overflow-hidden"
                      >
                        <button
                          onClick={() => toggleTheory(theory.id)}
                          className="w-full p-4 flex items-start gap-3 text-left hover:bg-surface-hover transition-colors"
                        >
                          <div
                            className="w-2 h-2 rounded-full mt-1.5 shrink-0"
                            style={{ backgroundColor: theory.color }}
                          />
                          <div className="flex-1 min-w-0">
                            <h4 className="font-semibold text-text-primary text-sm">
                              {theory.name}
                            </h4>
                            <p className="text-xs text-text-secondary">{theory.author}</p>
                          </div>
                          {isTheoryExpanded ? (
                            <ChevronDown size={14} className="text-text-secondary shrink-0 mt-1" />
                          ) : (
                            <ChevronRight size={14} className="text-text-secondary shrink-0 mt-1" />
                          )}
                        </button>

                        {isTheoryExpanded && (
                          <div className="px-4 pb-4 space-y-4 border-t border-border pt-4 animate-fade-in">
                            {/* Description */}
                            <p className="text-sm text-text-secondary leading-relaxed">
                              {theory.description}
                            </p>

                            {/* Key Concepts */}
                            <div>
                              <p className="text-xs font-semibold text-text-primary mb-2 uppercase tracking-wider">
                                Key Concepts
                              </p>
                              <div className="flex flex-wrap gap-1.5">
                                {theory.keyConcepts.map((concept) => (
                                  <span
                                    key={concept}
                                    className="badge text-[10px]"
                                    style={{
                                      backgroundColor: `${theory.color}15`,
                                      color: theory.color,
                                    }}
                                  >
                                    {concept}
                                  </span>
                                ))}
                              </div>
                            </div>

                            {/* How DIALECTICA uses it */}
                            <div
                              className="rounded-lg border p-3 space-y-1"
                              style={{
                                borderColor: `${theory.color}20`,
                                backgroundColor: `${theory.color}05`,
                              }}
                            >
                              <p className="text-xs font-semibold uppercase tracking-wider" style={{ color: theory.color }}>
                                How DIALECTICA Uses This
                              </p>
                              <p className="text-xs text-text-secondary leading-relaxed">
                                {theory.dialecticaUse}
                              </p>
                            </div>

                            {/* Detail link */}
                            <Link
                              href={`/theory/${theory.id}`}
                              className="inline-flex items-center gap-1 text-xs text-accent hover:text-accent-hover transition-colors"
                            >
                              View detailed framework page
                              <ArrowRight size={10} />
                            </Link>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Footer */}
      <div className="text-center text-xs text-text-secondary/50 pt-4 border-t border-border">
        DIALECTICA by{" "}
        <a
          href="https://tacitus.me"
          target="_blank"
          rel="noopener noreferrer"
          className="text-accent hover:text-accent-hover transition-colors"
        >
          TACITUS
        </a>{" "}
        — {totalTheories} Theories Operationalized as Symbolic Rules
      </div>
    </div>
  );
}
