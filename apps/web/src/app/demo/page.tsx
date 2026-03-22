"use client";

import { useState, useCallback, useRef } from "react";
import {
  Users,
  Globe,
  Briefcase,
  Loader2,
  CheckCircle2,
  AlertTriangle,
  Sparkles,
  Network,
  ArrowRight,
  ChevronDown,
  ChevronUp,
  BookOpen,
  Zap,
  Shield,
  Scale,
  Brain,
  Target,
  TrendingUp,
  Lock,
  ExternalLink,
  Clock,
  Eye,
  Heart,
  MessageSquare,
  FileText,
  Handshake,
  Activity,
  CircleDot,
} from "lucide-react";
import { NODE_COLORS, glaslLevel, GLASL_COLORS } from "@/lib/utils";
import type { GraphData, GraphNode, GraphLink } from "@/types/graph";


/* ------------------------------------------------------------------ */
/*  Annotated example scenario data                                    */
/* ------------------------------------------------------------------ */

interface AnnotatedQuestion {
  question: string;
  dialecticaAnswer: string;
}

interface AnnotatedScenario {
  id: string;
  title: string;
  subtitle: string;
  icon: React.ElementType;
  domain: string;
  text: string;
  extractedSummary: string;
  whyItMatters: string;
  questions: AnnotatedQuestion[];
}

const ANNOTATED_SCENARIOS: AnnotatedScenario[] = [
  {
    id: "jcpoa",
    title: "JCPOA Nuclear Crisis",
    subtitle: "Geopolitical multi-party escalation with treaty norms and military signaling",
    icon: Globe,
    domain: "Geopolitical",
    text: `Negotiations over the Revised Comprehensive Plan of Action (RCPOA) have entered a critical phase following Iran's announcement on January 15th that it has resumed enrichment of uranium to 20% purity at the Fordow underground facility, breaching the 3.67% limit established under the original JCPOA. IAEA Director General Takahashi confirmed the finding in a confidential report to the Board of Governors, noting that Iran's stockpile of enriched material now exceeds 500 kilograms — enough, if further enriched, for approximately two nuclear devices.

The United States, under Secretary of State Catherine Albright, has responded by reimposing secondary sanctions on Iranian oil exports targeting the Central Bank of Iran and three state-affiliated shipping companies, reducing Iran's oil revenue by an estimated $4 billion per quarter. Albright stated publicly that "the window for diplomatic resolution is measured in weeks, not months," and dispatched Special Envoy Robert Khalil to Geneva for back-channel discussions with Iranian Deputy Foreign Minister Javad Hosseini.

France, represented by Foreign Minister Dupont-Moreau, has taken a hardline position within the E3, insisting that any new agreement must address Iran's ballistic missile program — a condition Iran considers a sovereignty red line. Dupont-Moreau has proposed extending IAEA inspection authority to include military sites at Parchin and Shahrud, citing UN Security Council Resolution 2231's provisions on verification.

Russia, through Deputy Foreign Minister Volkov, has publicly opposed the expanded sanctions regime, arguing that economic coercion undermines diplomatic trust. Volkov has proposed a phased roadmap: Iran returns to the 3.67% enrichment ceiling in exchange for immediate suspension of secondary sanctions, with missile discussions deferred to a separate track. Tehran has signaled interest in the Russian proposal but demands that all sanctions be lifted within 90 days of compliance — a timeline Washington considers unacceptable.

The IAEA has requested expanded access under the Additional Protocol, including real-time monitoring of centrifuge cascades at Natanz and Fordow. Iran's Atomic Energy Organization has refused, calling the request "intelligence gathering disguised as verification." Supreme Leader Khamenei stated on February 20th that Iran's nuclear program is a matter of national sovereignty and "non-negotiable under duress." Meanwhile, Israeli Prime Minister Kessler warned in a Knesset address that Israel retains "all options" if the RCPOA talks fail, and satellite imagery shows increased activity at Israeli Air Force bases in the Negev.`,
    extractedSummary: "DIALECTICA extracts 11 actors (7 states, 4 organizations), 1 macro-scale conflict at Glasl stage 6, 8 events with causal chains, 5 issues (enrichment rights, sanctions, verification, regional activities, breakout time), 6 interests with BATNA analysis, 3 norms (NPT, UNSC 2231, Additional Protocol), 2 narratives (sovereign right vs proliferation threat), and 4 power dynamics across economic, military, and informational domains.",
    whyItMatters: "Traditional analysis would produce a long narrative summary. DIALECTICA produces a computable graph where every claim is traceable \u2014 you can ask \u2018show me all events that CAUSED escalation\u2019 and get a deterministic answer, not a guess.",
    questions: [
      {
        question: "At what Glasl escalation stage is this conflict?",
        dialecticaAnswer:
          "DIALECTICA computes Glasl stage 6 (Strategies of Threats) through deterministic causal chain analysis.\n\nEvent chain evaluated:\n\u2022 Event(JCPOA_withdrawal) \u2192 CAUSED[mechanism=provocation] \u2192 Event(enrichment_breach)\n\u2022 Event(enrichment_breach) \u2192 CAUSED[mechanism=retaliation] \u2192 Event(secondary_sanctions)\n\u2022 Event(secondary_sanctions) \u2192 CAUSED[mechanism=escalation] \u2192 Event(inspection_refusal)\n\u2022 Event(inspection_refusal) \u2192 CAUSED[mechanism=escalation] \u2192 Event(military_posturing)\n\nStage derivation: 4 completed escalation cycles with threat-based signaling (Kessler \u2018all options\u2019 + Negev base activity) = stage 6. Intervention type recommended: third-party mediation with security guarantees (stage 6 requires external guarantor, not bilateral talks alone). Confidence: 0.94 (deterministic from event graph).",
      },
      {
        question: "Has any international norm been violated?",
        dialecticaAnswer:
          "Deterministic norm-event matching yields 3 violations and 1 compliance gap:\n\n\u2022 Event(enrichment_to_20pct) \u2192 VIOLATES \u2192 Norm(NPT Article II): \u2018Each non-nuclear-weapon State Party undertakes not to manufacture or otherwise acquire nuclear weapons.\u2019 Enrichment to 20% exceeds civilian threshold. Severity: 0.92.\n\u2022 Event(inspection_refusal) \u2192 VIOLATES \u2192 Norm(Additional Protocol Art. 4): \u2018State shall provide access to all buildings on a site.\u2019 Refusal of Natanz/Fordow real-time monitoring = direct violation. Severity: 0.88.\n\u2022 Event(secondary_sanctions) \u2192 POTENTIALLY_VIOLATES \u2192 Norm(UNSC 2231 Para. 26): Unilateral sanctions beyond UNSC framework create tension with multilateral mandate. Severity: 0.45 (contested).\n\u2022 Compliance gap: UNSC 2231 Annex B (ballistic missile restrictions) \u2014 no specific violation event detected, but France\u2019s demand to include missiles references this norm. Status: monitoring.",
      },
      {
        question: "Who has leverage and how much?",
        dialecticaAnswer:
          "French & Raven power taxonomy applied across all actor pairs:\n\n\u2022 USA \u2192 Iran: economic power magnitude 0.95 (secondary sanctions, -$4B/quarter oil revenue), informational power 0.72 (intelligence on nuclear sites), coercive power 0.60 (military presence in Gulf)\n\u2022 Iran \u2192 USA: coercive power 0.50 (Strait of Hormuz chokepoint, 21% global oil transit), expert power 0.65 (sole knowledge of own enrichment state), legitimate power 0.40 (NPT right to peaceful nuclear energy)\n\u2022 France \u2192 Iran: legitimate power 0.55 (E3 negotiating authority, UNSC P5 seat), informational power 0.48 (satellite intelligence on Parchin)\n\u2022 Russia \u2192 USA: legitimate power 0.60 (UNSC veto, can block new resolutions), referent power 0.52 (positioned as neutral mediator with phased roadmap)\n\u2022 Israel \u2192 Iran: coercive power 0.85 (demonstrated strike capability, Negev base mobilization), but lacks legitimate power 0.15 (no seat at RCPOA table)\n\u2022 IAEA \u2192 All: expert power 0.90 (sole verification authority), legitimate power 0.82 (Board of Governors mandate)\n\nNet leverage index: USA 0.76, Israel 0.50 (high coercion, low legitimacy), Russia 0.56, Iran 0.52, France 0.52, IAEA 0.86 (highest expert authority).",
      },
      {
        question: "Is this conflict ripe for resolution?",
        dialecticaAnswer:
          "Zartman ripeness analysis returns composite ripeness score = 0.35 (NOT ripe).\n\nMutually Hurting Stalemate (MHS) score: 0.42\n\u2022 Iran pain index: 0.68 \u2014 $4B/quarter revenue loss is significant but survivable (China/India secondary routes estimated at $1.2B/quarter bypass).\n\u2022 USA pain index: 0.22 \u2014 diplomatic embarrassment and regional instability, but no direct economic cost.\n\u2022 MHS requires both parties above 0.60. Iran approaching threshold but USA well below.\n\nWay Out (WO) score: 0.28\n\u2022 Russia\u2019s phased roadmap provides a potential WO, but the 90-day sanctions timeline gap (Iran demands 90 days, USA offers 180+) blocks convergence.\n\u2022 No credible mediator accepted by both sides yet \u2014 Russia seen as partial by USA, EU fragmented between France hardline and Germany/UK moderate.\n\nBilateral exit assessment: Both parties retain viable alternatives. Iran can continue enrichment under sovereignty claim. USA can escalate to energy embargo. Neither feels trapped yet.\n\nProjection: Ripeness may reach 0.60+ if Iran stockpile crosses 1-device threshold (est. 4-6 months) AND secondary sanctions close China bypass routes.",
      },
      {
        question: "What are the causal mechanisms driving escalation?",
        dialecticaAnswer:
          "Full CAUSED chain with mechanism typing:\n\n\u2022 Event(JCPOA_original_withdrawal, 2018) \u2192 CAUSED[mechanism=provocation, weight=0.90] \u2192 Event(enrichment_resumption_20pct, Jan 15)\nIran frames withdrawal as betrayal justifying enrichment response.\n\n\u2022 Event(enrichment_resumption) \u2192 CAUSED[mechanism=retaliation, weight=0.88] \u2192 Event(secondary_sanctions_reimposed)\nUSA retaliates with economic pressure targeting Central Bank + 3 shipping companies.\n\n\u2022 Event(secondary_sanctions) \u2192 CAUSED[mechanism=escalation, weight=0.82] \u2192 Event(IAEA_access_refusal)\nIran escalates by blocking verification \u2014 moves from treaty breach to opacity.\n\n\u2022 Event(IAEA_access_refusal) \u2192 CAUSED[mechanism=escalation, weight=0.78] \u2192 Event(military_signaling_Negev)\nIsrael signals military readiness in response to verification collapse.\n\n\u2022 Event(France_missile_demand) \u2192 CAUSED[mechanism=provocation, weight=0.72] \u2192 Event(Khamenei_sovereignty_statement)\nFrance\u2019s scope expansion triggers sovereignty red line invocation.\n\n\u2022 Event(Russia_roadmap_proposal) \u2192 CAUSED[mechanism=de-escalation_attempt, weight=0.65] \u2192 Event(Geneva_backchannel)\nRussia\u2019s phased approach creates diplomatic off-ramp, partially accepted.\n\nEscalation velocity: 6 events across 5 weeks = 1.2 escalation events/week. Baseline for geopolitical conflicts: 0.3-0.5/week. This conflict is escalating at 2.4-4x normal rate.",
      },
      {
        question: "What are each party's unstated interests?",
        dialecticaAnswer:
          "Fisher/Ury interest analysis \u2014 stated positions vs underlying interests with priority scores:\n\nIran:\n\u2022 Stated position: \u2018Nuclear program is non-negotiable under duress.\u2019\n\u2022 Interest 1: Regime survival and domestic legitimacy (priority: 0.95) \u2014 nuclear program is a symbol of technological sovereignty.\n\u2022 Interest 2: Sanctions relief for economic stability (priority: 0.88) \u2014 $4B/quarter loss threatens social contract.\n\u2022 Interest 3: Regional influence preservation (priority: 0.72) \u2014 missile program tied to deterrence against Israel/Saudi Arabia.\n\nUSA:\n\u2022 Stated position: \u2018Window is weeks, not months.\u2019\n\u2022 Interest 1: Non-proliferation credibility (priority: 0.90) \u2014 failure here undermines global NPT regime.\n\u2022 Interest 2: Regional stability / ally reassurance (priority: 0.82) \u2014 Israel and Gulf states demand credible US posture.\n\u2022 Interest 3: Domestic political positioning (priority: 0.68) \u2014 appear strong without entering another Middle East conflict.\n\nFrance:\n\u2022 Stated: \u2018Must address ballistic missiles.\u2019\n\u2022 Unstated: Establish E3 leadership distinct from USA (priority: 0.75), protect European security perimeter (priority: 0.70).\n\nRussia:\n\u2022 Stated: \u2018Economic coercion undermines trust.\u2019\n\u2022 Unstated: Maintain influence as indispensable mediator (priority: 0.85), counter US unilateralism (priority: 0.78), preserve arms sales relationship with Iran (priority: 0.60).",
      },
      {
        question: "What alliances and oppositions shape this conflict?",
        dialecticaAnswer:
          "Network analysis of ALLIED_WITH and OPPOSED_TO edges with strength scores:\n\nAlliance clusters:\n\u2022 USA \u2194 Israel: ALLIED_WITH strength 0.92 \u2014 shared non-proliferation objective, intelligence sharing, military coordination (Negev activity correlates with Albright timeline).\n\u2022 USA \u2194 France: ALLIED_WITH strength 0.68 \u2014 aligned on pressure but divergent on scope (France wants missiles included, USA focused on enrichment first).\n\u2022 Russia \u2194 Iran: ALLIED_WITH strength 0.72 \u2014 Russia provides diplomatic cover (opposes sanctions) but not unconditional (proposes enrichment ceiling return).\n\nOpposition edges:\n\u2022 USA \u2194 Iran: OPPOSED_TO strength 0.88 \u2014 primary adversarial dyad on sanctions/enrichment.\n\u2022 France \u2194 Iran: OPPOSED_TO strength 0.75 \u2014 secondary opposition on missile scope.\n\u2022 Israel \u2194 Iran: OPPOSED_TO strength 0.95 \u2014 existential framing by both sides.\n\u2022 Russia \u2194 USA: OPPOSED_TO strength 0.55 \u2014 moderate opposition on sanctions approach, but both want non-proliferation.\n\nBridge actors: IAEA serves as bridge node (betweenness centrality 0.82) \u2014 trusted by all parties for verification but contested on scope. Russia acts as secondary bridge (betweenness 0.65) with proposed roadmap.\n\nCoalition stability: USA-Israel-France coalition is strong but brittle on missile scope divergence. Russia-Iran alignment is transactional, not strategic.",
      },
    ],
  },
  {
    id: "workplace",
    title: "Workplace Code Review Incident",
    subtitle: "Interpersonal conflict with power asymmetry and team dynamics",
    icon: Users,
    domain: "Workplace",
    text: `Alex Chen, a junior software engineer at Northwind Technologies, has filed a formal complaint against Maya Okonkwo, his tech lead. During a weekly architecture review with 6 team members present, Maya publicly criticized Alex's system design, saying "This shows fundamental misunderstanding of our system. I don't know how this passed initial review." Alex, who has been at the company for 14 months and previously noticed a pattern of terse code review comments from Maya (34 negative comments on one PR), experienced an anxiety attack and left the office. His colleague Kai reported the dynamics to HR. The team has informally split \u2014 junior engineers sympathize with Alex while senior engineers back Maya's right to maintain high standards. VP Engineering has noticed sprint velocity dropping 30%. HR Business Partner Jordan Reyes has been assigned to mediate.`,
    extractedSummary: "DIALECTICA extracts 5 actors (Alex, Maya, Kai, Jordan, VP Engineering), 1 micro-scale conflict at Glasl stage 3, 6 events with causal chain (terse comments \u2192 public criticism \u2192 anxiety attack \u2192 complaint \u2192 team split \u2192 mediation assignment), 3 issues (communication style, professional respect, code quality standards), 4 interests across 3 holders, 2 norms (company code of conduct, informal feedback norms), 2 emotional states, 1 trust breakdown, and 2 power dynamics (positional + expert).",
    whyItMatters: "An LLM would summarize this as \u2018a workplace dispute between a junior and senior engineer.\u2019 DIALECTICA maps the exact power asymmetry (Maya controls Alex\u2019s performance review), computes escalation velocity (4 stages in 10 weeks = 2.5x normal), and identifies that the trust breakdown is bidirectional but asymmetric \u2014 enabling targeted intervention design.",
    questions: [
      {
        question: "What\u2019s the full power dynamic map?",
        dialecticaAnswer:
          "French & Raven power analysis across all actor pairs:\n\n\u2022 Maya \u2192 Alex: positional power 0.75 (tech lead, writes performance reviews, controls PR approvals), expert power 0.80 (senior technical authority, architecture decision maker), reward power 0.55 (influences promotion pipeline and project assignments).\n\u2022 Alex \u2192 Maya: legitimate power via HR complaint 0.40 (formal grievance process gives Alex institutional leverage Maya didn\u2019t anticipate), referent power 0.35 (junior engineer sympathy coalition \u2014 3 of 6 team members).\n\u2022 Jordan (HR) \u2192 Both: legitimate power 0.70 (organizational mandate to mediate), informational power 0.65 (access to HR records, complaint history, company policy).\n\u2022 VP Engineering \u2192 All: positional power 0.90 (can restructure team, reassign leads), coercive power 0.60 (sprint velocity drop threatens team funding).\n\u2022 Kai \u2192 Maya: informational power 0.30 (reported dynamics to HR, acts as witness).\n\nCritical asymmetry: Maya holds 3 power types over Alex with combined magnitude 2.10, while Alex holds 0.75 total. This 2.8:1 ratio exceeds the threshold (2.0:1) where DIALECTICA flags mandatory power-balancing intervention before joint mediation.",
      },
      {
        question: "What are ALL the interests \u2014 stated and unstated?",
        dialecticaAnswer:
          "Complete Fisher/Ury interest map with holder and priority scores:\n\nAlex (4 interests):\n\u2022 Stated: \u2018No more public criticism\u2019 (priority: 0.90)\n\u2022 Unstated: Psychological safety in team environment (priority: 0.95 \u2014 highest, evidenced by anxiety attack)\n\u2022 Unstated: Career growth and skill acknowledgment (priority: 0.78 \u2014 14 months tenure, seeking validation)\n\u2022 Unstated: Restored professional reputation after public humiliation (priority: 0.72)\n\nMaya (3 interests):\n\u2022 Stated: \u2018Right to give direct technical feedback\u2019 (priority: 0.85)\n\u2022 Unstated: Preserve authority and team respect (priority: 0.88 \u2014 senior engineers backing her validates this)\n\u2022 Unstated: Not be labeled a bully / protect professional identity (priority: 0.82 \u2014 HR complaint threatens this)\n\nNorthwind/VP Engineering (2 interests):\n\u2022 Restore sprint velocity (priority: 0.90 \u2014 30% drop is board-level metric)\n\u2022 Retain both employees (priority: 0.75 \u2014 replacement cost estimated at 6-9 months salary each)\n\nJordan/HR (1 interest):\n\u2022 Resolve without litigation risk (priority: 0.85 \u2014 anxiety attack creates potential constructive dismissal claim)\n\nOverlapping interests: Both Alex and Maya want a functional working relationship (overlap score: 0.68). Both want to be seen as competent professionals (overlap: 0.72). These overlaps define the negotiation space.",
      },
      {
        question: "How fast is this escalating?",
        dialecticaAnswer:
          "Glasl stage progression analysis with velocity computation:\n\nCurrent stage: 3 (Actions Not Words)\n\nEvent timeline with stage transitions:\n\u2022 Weeks 1-3: Terse code review comments (34 negative comments on one PR) = Stage 1 (Hardening). Duration: 3 weeks.\n\u2022 Weeks 4-6: Pattern recognition by Alex, avoidance behavior begins = Stage 2 (Polarization). Duration: 2 weeks.\n\u2022 Week 7: Public architecture review criticism (\u2018fundamental misunderstanding\u2019) = transition trigger to Stage 3.\n\u2022 Weeks 8-9: Formal complaint + team split = Stage 3 consolidated (Actions Not Words). Duration: 2 weeks and counting.\n\nEscalation velocity: 3 stage transitions in 9 weeks = 0.33 stages/week.\nTypical workplace conflict baseline: 0.12-0.15 stages/week.\nThis conflict escalates at 2.2-2.8x normal rate.\n\nRisk projection: Without intervention, DIALECTICA projects Stage 4 (Coalitions) in 2-4 weeks based on the team split dynamic. The junior/senior divide is a coalition-formation precursor. Stage 5 (Loss of Face) projected at week 14-16 if Alex\u2019s complaint is perceived as public shaming of Maya.",
      },
      {
        question: "What does the trust matrix look like?",
        dialecticaAnswer:
          "Mayer trust model (Ability / Benevolence / Integrity) applied to key dyads:\n\nAlex \u2192 Maya:\n\u2022 Ability: 0.70 (Alex acknowledges Maya\u2019s technical skill)\n\u2022 Benevolence: 0.15 (near-zero \u2014 Alex perceives Maya as hostile, not developmental)\n\u2022 Integrity: 0.25 (public criticism violates expected professional norms)\n\u2022 Composite trust: 0.37 (LOW \u2014 below functional threshold of 0.50)\n\nMaya \u2192 Alex:\n\u2022 Ability: 0.35 (Maya questions Alex\u2019s competence \u2014 \u2018fundamental misunderstanding\u2019)\n\u2022 Benevolence: 0.45 (Maya may believe she\u2019s helping Alex grow, but delivery undermines this)\n\u2022 Integrity: 0.55 (Maya sees Alex\u2019s complaint as disproportionate/political)\n\u2022 Composite trust: 0.45 (LOW \u2014 below threshold)\n\nBoth \u2192 Jordan:\n\u2022 Alex \u2192 Jordan: ability 0.60, benevolence 0.65, integrity 0.70. Composite: 0.65 (MODERATE \u2014 hopeful but cautious).\n\u2022 Maya \u2192 Jordan: ability 0.55, benevolence 0.40, integrity 0.60. Composite: 0.52 (BORDERLINE \u2014 Maya may see HR as adversarial).\n\nTrust trajectory: Deteriorating at -0.08/week for Alex\u2192Maya dyad. Without intervention, will reach irreparable threshold (0.20) in approximately 2 weeks. Jordan\u2019s credibility as mediator depends on maintaining above 0.50 with both parties.",
      },
      {
        question: "What emotions are driving behavior?",
        dialecticaAnswer:
          "Plutchik emotion wheel analysis with behavioral mapping:\n\nAlex:\n\u2022 Primary: Fear (intensity 0.82) \u2014 fear of further public humiliation, career damage.\n\u2022 Secondary: Sadness (intensity 0.68) \u2014 loss of professional confidence, belongingness.\n\u2022 Compound: Fear + Sadness = Despair/Submission (intensity 0.75). Behavioral marker: anxiety attack, office departure.\n\u2022 Tertiary: Anger (intensity 0.55, rising) \u2014 emerging through formal complaint. This shift from submission to assertion is significant.\n\nMaya:\n\u2022 Primary: Surprise (intensity 0.70) \u2014 genuinely did not expect formal complaint for \u2018normal feedback.\u2019\n\u2022 Secondary: Anger (intensity 0.65) \u2014 perceived overreaction and threat to authority.\n\u2022 Compound: Surprise + Anger = Outrage (intensity 0.68). Behavioral marker: likely to become defensive/dismissive in mediation.\n\u2022 Tertiary: Contempt (intensity 0.40) \u2014 if Alex\u2019s competence is questioned, contempt can emerge, which Gottman research identifies as the most corrosive emotion for relationship repair.\n\nEmotional asymmetry: Alex operates from vulnerability (fear-based), Maya from indignation (anger-based). Mediator must address safety before substance \u2014 DIALECTICA recommends separate caucus sessions first.",
      },
      {
        question: "What norms apply and have any been violated?",
        dialecticaAnswer:
          "Norm inventory with violation assessment:\n\nFormal norms:\n\u2022 Northwind Employee Handbook Section 4.2 (Respectful Workplace): \u2018Feedback shall be delivered constructively and privately when addressing individual performance.\u2019 Event(public_criticism) \u2192 VIOLATES \u2192 Norm(handbook_4.2). Severity: 0.72. Maya\u2019s public statement in front of 6 team members breaches \u2018privately\u2019 requirement.\n\u2022 California FEHA (Fair Employment and Housing Act): Sustained pattern of hostile comments (34 on one PR) could meet threshold for hostile work environment claim. Status: POTENTIALLY_VIOLATES. Severity: 0.55 (requires pattern evidence, which exists).\n\u2022 Northwind Code Review Guidelines (informal but documented): \u2018Reviews should focus on code, not coder.\u2019 Event(personal_criticism) \u2192 VIOLATES \u2192 Norm(review_guidelines). Severity: 0.65. \u2018This shows fundamental misunderstanding\u2019 targets the person, not the code.\n\nInformal norms:\n\u2022 Team norm: Senior engineers mentor juniors through code review. Maya\u2019s 34 negative comments without constructive guidance breaches mentorship expectation. Severity: 0.58.\n\u2022 Psychological safety norm (Edmondson framework): Team members should feel safe to make mistakes. Anxiety attack indicates complete psychological safety breakdown. Severity: 0.85.\n\nCompliance gap: No formal escalation procedure was followed before the architecture review \u2014 Maya did not document concerns through 1:1 channels first.",
      },
      {
        question: "What resolution approach does the evidence support?",
        dialecticaAnswer:
          "Multi-framework resolution analysis:\n\nFisher/Ury interest-based assessment:\n\u2022 Both parties need ongoing working relationship (switching cost high \u2014 same team, shared codebase).\n\u2022 Overlapping interests exist (both want functional team, both want professional respect).\n\u2022 Verdict: Interest-based negotiation viable if power imbalance is addressed first.\n\nThomas-Kilmann conflict mode assessment:\n\u2022 Alex current mode: Avoiding (left office, filed complaint through HR rather than direct engagement). Score: 0.85.\n\u2022 Maya current mode: Competing (maintained position, backed by senior engineers). Score: 0.78.\n\u2022 Target mode for resolution: Collaborating \u2014 but requires trust above 0.50 threshold (currently below for both).\n\nRecommended process (4 phases):\n1. Phase 1 \u2014 Separate caucuses (shuttle mediation): Jordan meets each party individually. Goal: validate emotions, assess interests, build mediator trust. Duration: 1 week.\n2. Phase 2 \u2014 Power balancing: Establish ground rules that neutralize positional asymmetry. Alex gets assurance that participation won\u2019t affect performance review. Duration: concurrent with Phase 1.\n3. Phase 3 \u2014 Joint session with structured dialogue: Both parties present interests (not positions). Jordan facilitates. Focus on forward-looking agreements, not blame attribution. Duration: 2-3 hours.\n4. Phase 4 \u2014 Written agreement with review milestones: Specific behavioral commitments (e.g., private feedback first, code review comment guidelines), reviewed at 30/60/90 days.\n\nRationale: Power imbalance ratio (2.8:1) makes direct negotiation unsafe for Alex. Shuttle mediation first, then joint session with ground rules, follows best practice for asymmetric workplace conflicts.",
      },
    ],
  },
  {
    id: "commercial",
    title: "Commercial ERP Dispute",
    subtitle: "Contract breach with financial stakes and commercial negotiation",
    icon: Briefcase,
    domain: "Commercial",
    text: `Apex Systems Ltd signed a GBP 2.4M fixed-price contract with Crestline Manufacturing PLC to deliver a custom ERP system within 12 months. During the project, Crestline submitted two change requests \u2014 additional warehouse modules and a real-time reporting dashboard \u2014 without signing formal change orders. The project ran 18 months late. Apex delivered v2.1 with 23 critical bugs documented in an independent audit. Three days later, Crestline's warehouse went offline for 72 hours, costing GBP 800K in emergency operations. Crestline claims total damages of GBP 4.1M. Apex counter-claims GBP 800K for unpaid scope expansion. Direct CEO-to-COO negotiation failed. Both parties have agreed to CEDR mediation with evaluative mediator Richard Faulkner QC. Apex's cash flow depends on this contract (30% of revenue). Crestline's planned 2025 IPO requires a functioning ERP for due diligence.`,
    extractedSummary: "DIALECTICA extracts 6 actors (Apex Systems, Crestline Manufacturing, Apex CEO, Crestline COO, Richard Faulkner QC, independent auditor), 1 meso-scale conflict at Glasl stage 4, 9 events with causal chain (RFP \u2192 contract \u2192 change requests \u2192 delay \u2192 delivery \u2192 audit \u2192 outage \u2192 claims \u2192 failed negotiation), 4 issues (scope creep, delivery quality, payment, timeline), 6 interests across both parties, 4 norms (contract clauses 8.2/12.3, Sale of Goods Act, CEDR rules), 3 power dynamics (economic, informational, legal), and financial quantification (GBP 2.4M contract, GBP 4.1M claim, GBP 800K counter-claim).",
    whyItMatters: "A traditional legal analysis would debate liability in narrative form. DIALECTICA computes the ZOPA from reservation values and BATNAs, maps the causal chain from scope change to warehouse outage with evidential links, and identifies that both parties\u2019 time pressures (cash runway vs IPO timeline) create computable mutual urgency \u2014 a Zartman ripeness signal that narrative analysis would miss.",
    questions: [
      {
        question: "What\u2019s the ZOPA?",
        dialecticaAnswer:
          "Zone of Possible Agreement computation from reservation values and walk-away points:\n\nApex Systems:\n\u2022 Reservation value: GBP 960K (minimum to maintain cash flow \u2014 30% of revenue at GBP 8M annual, 3-month runway requires at least GBP 960K net from this contract).\n\u2022 Best case: GBP 2.4M (full contract value) + GBP 800K (counter-claim for unpaid scope expansion) = GBP 3.2M.\n\u2022 Walk-away point: Below GBP 960K, Apex faces insolvency risk. Switching cost for Apex: GBP 0 (they can pursue other clients, but losing 30% revenue is existential).\n\nCrestline Manufacturing:\n\u2022 Reservation value: Net cost of alternative = GBP 1.5M (switch vendor) + GBP 800K (already incurred emergency ops) = GBP 2.3M sunk. They need a working ERP for IPO due diligence \u2014 delay costs estimated at GBP 500K/month in IPO preparation.\n\u2022 Best case: GBP 4.1M damages awarded (full claim). Walk-away: litigation costs estimated at GBP 200-400K, 12-18 month timeline incompatible with IPO.\n\nZOPA: GBP 960K to GBP 2.3M. Both parties are better off settling within this range than pursuing alternatives.\n\nOptimal settlement point: GBP 1.4-1.7M range \u2014 Apex retains enough to survive, Crestline saves GBP 600K+ vs vendor switch, and both avoid litigation delay.",
      },
      {
        question: "What are ALL the causal mechanisms?",
        dialecticaAnswer:
          "Full event chain from RFP through settlement with mechanism types:\n\n\u2022 Event(contract_signing, Month 0) \u2192 CAUSED[mechanism=initiation, weight=0.95] \u2192 Event(project_start)\nGBP 2.4M fixed-price, 12-month delivery.\n\n\u2022 Event(change_request_1, Month 4) \u2192 CAUSED[mechanism=scope_creep, weight=0.85] \u2192 Event(timeline_pressure)\nAdditional warehouse modules requested without formal change order.\n\n\u2022 Event(change_request_2, Month 7) \u2192 CAUSED[mechanism=scope_creep, weight=0.82] \u2192 Event(resource_reallocation)\nReal-time reporting dashboard added. Combined scope expansion estimated at 35% additional work.\n\n\u2022 Event(scope_expansion) \u2192 CAUSED[mechanism=resource_strain, weight=0.78] \u2192 Event(delivery_delay_18mo)\nProject overruns by 6 months (50% schedule slip).\n\n\u2022 Event(delivery_v2.1) \u2192 CAUSED[mechanism=quality_failure, weight=0.88] \u2192 Event(23_critical_bugs)\nIndependent audit documents 23 critical defects in delivered system.\n\n\u2022 Event(23_critical_bugs) \u2192 CAUSED[mechanism=system_failure, weight=0.92] \u2192 Event(warehouse_offline_72hrs)\n72-hour outage, GBP 800K emergency operations cost.\n\n\u2022 Event(warehouse_outage) \u2192 CAUSED[mechanism=financial_escalation, weight=0.90] \u2192 Event(damages_claim_4.1M)\nCrestline claims GBP 4.1M total damages.\n\n\u2022 Event(CEO_COO_negotiation) \u2192 CAUSED[mechanism=negotiation_failure, weight=0.70] \u2192 Event(CEDR_mediation_referral)\nDirect negotiation fails, mediation agreed.\n\nCritical insight: The unsigned change orders (Events 2-3) are the root cause bifurcation point \u2014 they created mutual liability ambiguity that enabled both the scope-driven delay and the contractual defense.",
      },
      {
        question: "What norms govern this dispute and what violations occurred?",
        dialecticaAnswer:
          "Norm inventory with violation mapping:\n\nContractual norms:\n\u2022 Contract Clause 8.2 (Change Control): \u2018All scope modifications require written change order signed by both parties before work commences.\u2019 Crestline submitted 2 change requests without signing formal change orders. Event(change_request_unsigned) \u2192 VIOLATES \u2192 Norm(clause_8.2). Severity: 0.78. This weakens Crestline\u2019s position on scope-related claims.\n\u2022 Contract Clause 12.3 (Breach Notice): \u2018Party shall provide written notice of material breach within 14 days of discovery.\u2019 Crestline properly served breach notice 3 days after audit. Event(breach_notice) \u2192 COMPLIES_WITH \u2192 Norm(clause_12.3). This strengthens Crestline\u2019s position on quality claims.\n\u2022 Contract Clause 15.1 (Limitation of Liability): Cap at 150% of contract value (GBP 3.6M). Crestline\u2019s GBP 4.1M claim exceeds cap \u2014 GBP 500K likely unrecoverable.\n\nStatutory norms:\n\u2022 Sale of Goods Act 1979 / Supply of Goods and Services Act 1982: Implied term of \u2018reasonable care and skill.\u2019 23 critical bugs in delivered system = prima facie breach. Event(delivery_with_bugs) \u2192 VIOLATES \u2192 Norm(SGA_implied_term). Severity: 0.82.\n\nProcedural norms:\n\u2022 CEDR Mediation Rules: Both parties agreed to evaluative mediation with Faulkner QC. Rule 7 requires good faith participation and authority to settle. Rule 12 provides confidentiality protections for offers made during mediation.\n\nNet liability assessment: Split liability \u2014 Apex bears primary responsibility for quality defects (23 bugs, outage), but Crestline\u2019s unsigned change orders contributed to schedule pressure. Estimated liability split: Apex 65%, Crestline 35%.",
      },
      {
        question: "What are the power dynamics between the parties?",
        dialecticaAnswer:
          "French & Raven power analysis:\n\nApex Systems:\n\u2022 Expert power: 0.72 (holds domain knowledge of the ERP system, source code, and technical debt). Crestline cannot easily replicate this without significant onboarding cost for replacement vendor.\n\u2022 Informational power: 0.65 (knows true state of codebase, which bugs are cosmetic vs structural, estimated fix timeline).\n\u2022 Economic power: 0.25 (weak \u2014 30% revenue dependency creates desperation, not leverage).\n\nCrestline Manufacturing:\n\u2022 Economic power: 0.82 (controls payment, GBP 800K counter-claim owed, can withhold final payment).\n\u2022 Coercive power: 0.70 (threat of litigation, public reputation damage for Apex).\n\u2022 Legitimate power: 0.68 (properly served breach notice, independent audit supports position).\n\nMediator (Faulkner QC):\n\u2022 Expert power: 0.85 (QC designation, commercial dispute specialization).\n\u2022 Legitimate power: 0.75 (CEDR appointment, evaluative authority).\n\u2022 Informational power: 0.60 (access to both parties\u2019 submissions, can reality-test positions).\n\nPower asymmetry: Crestline holds net advantage (combined 2.20 vs Apex 1.62), but Apex\u2019s expert power is a key equalizer \u2014 Crestline cannot easily replace the system knowledge. This creates a dependency that moderates Crestline\u2019s leverage.\n\nKey dynamic: Apex\u2019s cash flow vulnerability (30% revenue dependency) is the single largest power imbalance factor. Faulkner QC should assess whether Apex has settlement authority that reflects survival needs, not just legal merit.",
      },
      {
        question: "What are each party\u2019s BATNAs?",
        dialecticaAnswer:
          "Best Alternative to Negotiated Agreement analysis:\n\nApex Systems BATNA:\n\u2022 Alternative 1: Litigation \u2014 defend against GBP 4.1M claim, pursue GBP 800K counter-claim. Estimated legal costs: GBP 150-250K. Timeline: 12-18 months. Probability of winning on counter-claim: 0.65 (unsigned change orders). Probability of reducing damages claim: 0.55 (contributory negligence argument).\n\u2022 Alternative 2: Fix bugs for free \u2014 estimated cost GBP 180-300K in developer time. Preserves relationship but concedes fault.\n\u2022 BATNA strength: 0.35 (WEAK). Cash flow constraint means Apex cannot survive 12-18 month litigation. They need resolution within 3 months.\n\nCrestline Manufacturing BATNA:\n\u2022 Alternative 1: Switch vendor \u2014 GBP 1.5M replacement cost + 6-9 month timeline. Risks IPO due diligence deadline.\n\u2022 Alternative 2: Litigation \u2014 pursue GBP 4.1M claim. Legal costs: GBP 200-400K. Strong position on quality defects but weakened by unsigned change orders. Timeline: 12-18 months (incompatible with IPO).\n\u2022 Alternative 3: Internal development team \u2014 hire 4-6 developers at GBP 60-80K each. Total: GBP 240-480K but 8-12 month ramp-up.\n\u2022 BATNA strength: 0.52 (MODERATE). Better than Apex\u2019s, but IPO timeline creates urgency that weakens walk-away credibility.\n\nImplication: Both parties have weak-to-moderate BATNAs, which expands the ZOPA and creates incentive for mediated settlement. The party that most credibly improves their BATNA gains negotiating leverage.",
      },
      {
        question: "What time pressures create urgency?",
        dialecticaAnswer:
          "Deadline analysis with Zartman ripeness implications:\n\nApex Systems:\n\u2022 Cash flow runway: 3 months at current burn rate. This contract represents 30% of GBP 8M annual revenue = GBP 2.4M. Without resolution, Apex faces liquidity crisis by Month 3. Urgency score: 0.92.\n\u2022 Developer retention: Key engineers may leave if project uncertainty continues. Attrition risk rises after Month 2. Urgency score: 0.65.\n\nCrestline Manufacturing:\n\u2022 IPO timeline: Planned 2025 IPO requires functioning ERP for due diligence. Investment bank due diligence typically begins 6-9 months before listing. If ERP issue is unresolved, IPO delay costs estimated at GBP 500K/month in preparation costs + opportunity cost of market timing. Urgency score: 0.85.\n\u2022 Board mandate: Crestline board has instructed management to resolve within Q1. Exceeding this triggers governance escalation. Urgency score: 0.70.\n\u2022 Warehouse operations: Interim manual processes cost GBP 45K/month. Ongoing until ERP is fixed or replaced. Urgency score: 0.55.\n\nMutual urgency computation (Zartman):\n\u2022 Combined urgency index: 0.88 (HIGH). Both parties face time-bound consequences that worsen with delay.\n\u2022 Ripeness signal: The convergence of Apex cash runway (3 months) and Crestline IPO timeline (6-9 months) creates a narrow 3-month window where both parties are maximally motivated to settle.\n\u2022 This is computable ripeness \u2014 DIALECTICA identifies that the conflict IS ripe for resolution (ripeness = 0.78), unlike the JCPOA scenario (0.35).",
      },
      {
        question: "What does the evidence chain look like?",
        dialecticaAnswer:
          "EVIDENCED_BY relationship mapping across all claims:\n\nCrestline\u2019s claim (GBP 4.1M):\n\u2022 Claim(delivery_defective) \u2192 EVIDENCED_BY \u2192 Document(independent_audit_report): 23 critical bugs documented with severity ratings. Evidence strength: 0.92 (independent third party, contemporaneous).\n\u2022 Claim(warehouse_damages_800K) \u2192 EVIDENCED_BY \u2192 Document(emergency_ops_invoices) + Document(warehouse_downtime_log): 72-hour outage, emergency contractor costs. Evidence strength: 0.88 (financial records, verifiable).\n\u2022 Claim(consequential_losses_3.3M) \u2192 EVIDENCED_BY \u2192 Document(financial_projections): Lost revenue, customer penalties, delayed contracts. Evidence strength: 0.45 (projections are speculative, difficult to prove causation for full amount).\n\nApex\u2019s counter-claim (GBP 800K):\n\u2022 Claim(unpaid_scope_expansion) \u2192 EVIDENCED_BY \u2192 Document(change_request_emails) + Document(work_logs): Email trail shows Crestline requested and Apex delivered additional modules. Evidence strength: 0.72.\n\u2022 Claim(no_signed_change_order) \u2192 EVIDENCED_BY \u2192 Document(contract_clause_8.2) + Document(unsigned_requests): Change orders exist but lack Crestline signatures. Evidence strength: 0.78 (cuts both ways \u2014 Apex should have insisted on signatures before starting work).\n\nEvidence gap: No UAT (User Acceptance Testing) sign-off document exists for v2.1. This is critical \u2014 if Crestline used the system for 3 days before outage, implied acceptance may apply. Evidence status: MISSING, requires discovery.\n\nNet evidence assessment: Crestline has stronger evidence on quality defects (0.92) but weaker on consequential losses (0.45). Apex has moderate evidence on scope expansion (0.72) but is weakened by failing to enforce change order process. Mediator should focus settlement on the well-evidenced claims (defects + outage = GBP 800K + direct costs) rather than speculative consequential losses.",
      },
    ],
  },
];

/* ------------------------------------------------------------------ */
/*  Fallback data derived from hr_mediation.json seed file             */
/* ------------------------------------------------------------------ */

const FALLBACK_NODES: GraphNode[] = [
  /* ---- 8 Actors ---- */
  {
    id: "actor_alex",
    label: "Actor",
    node_type: "actor",
    name: "Alex Chen",
    confidence: 0.95,
    properties: { role_title: "Junior Software Engineer", actor_type: "person", centrality: 0.82 },
  },
  {
    id: "actor_maya",
    label: "Actor",
    node_type: "actor",
    name: "Maya Okonkwo",
    confidence: 0.95,
    properties: { role_title: "Tech Lead", actor_type: "person", centrality: 0.85 },
  },
  {
    id: "actor_jordan",
    label: "Actor",
    node_type: "actor",
    name: "Jordan Reyes",
    confidence: 0.92,
    properties: { role_title: "HR Business Partner / Mediator", actor_type: "person", centrality: 0.6 },
  },
  {
    id: "actor_kai",
    label: "Actor",
    node_type: "actor",
    name: "Kai Tanaka",
    confidence: 0.88,
    properties: { role_title: "Software Engineer (teammate/witness)", actor_type: "person", centrality: 0.35 },
  },
  {
    id: "actor_elena",
    label: "Actor",
    node_type: "actor",
    name: "Elena Vasquez",
    confidence: 0.88,
    properties: { role_title: "Senior Software Engineer", actor_type: "person", centrality: 0.32 },
  },
  {
    id: "actor_priya",
    label: "Actor",
    node_type: "actor",
    name: "Priya Sharma",
    confidence: 0.85,
    properties: { role_title: "VP Engineering", actor_type: "person", centrality: 0.45 },
  },
  {
    id: "actor_marcus",
    label: "Actor",
    node_type: "actor",
    name: "Marcus Thompson",
    confidence: 0.85,
    properties: { role_title: "VP People", actor_type: "person", centrality: 0.38 },
  },
  {
    id: "actor_northwind",
    label: "Actor",
    node_type: "actor",
    name: "Northwind Technologies",
    confidence: 0.95,
    properties: { actor_type: "organization", centrality: 0.5 },
  },

  /* ---- 1 Conflict ---- */
  {
    id: "conflict_code_review",
    label: "Conflict",
    node_type: "conflict",
    name: "Code Review Incident",
    confidence: 0.96,
    properties: { glasl_stage: 3, status: "active", scale: "micro", domain: "workplace", kriesberg_phase: "escalating", centrality: 1.0 },
  },

  /* ---- 6 Events ---- */
  {
    id: "event_first_tension",
    label: "Event",
    node_type: "event",
    name: "First Tension",
    confidence: 0.88,
    properties: { event_type: "tension", severity: 0.3, occurred_at: "2025-04-10", centrality: 0.42 },
  },
  {
    id: "event_alex_avoids",
    label: "Event",
    node_type: "event",
    name: "Alex Avoids Maya",
    confidence: 0.85,
    properties: { event_type: "withdraw", severity: 0.35, occurred_at: "2025-04-25", centrality: 0.38 },
  },
  {
    id: "event_code_review_incident",
    label: "Event",
    node_type: "event",
    name: "Code Review Incident",
    confidence: 0.95,
    properties: { event_type: "disapprove", severity: 0.75, occurred_at: "2025-06-15", centrality: 0.72 },
  },
  {
    id: "event_formal_complaint",
    label: "Event",
    node_type: "event",
    name: "Formal Complaint Filed",
    confidence: 0.92,
    properties: { event_type: "demand", severity: 0.65, occurred_at: "2025-06-20", centrality: 0.62 },
  },
  {
    id: "event_team_splits",
    label: "Event",
    node_type: "event",
    name: "Team Splits",
    confidence: 0.88,
    properties: { event_type: "polarize", severity: 0.55, occurred_at: "2025-06-25", centrality: 0.48 },
  },
  {
    id: "event_mediation_session",
    label: "Event",
    node_type: "event",
    name: "Mediation Session",
    confidence: 0.9,
    properties: { event_type: "consult", severity: 0.35, occurred_at: "2025-07-10", centrality: 0.55 },
  },

  /* ---- 3 Issues ---- */
  {
    id: "issue_communication_style",
    label: "Issue",
    node_type: "issue",
    name: "Communication Style",
    confidence: 0.92,
    properties: { issue_type: "procedural", salience: 0.85, centrality: 0.55 },
  },
  {
    id: "issue_professional_respect",
    label: "Issue",
    node_type: "issue",
    name: "Professional Respect",
    confidence: 0.94,
    properties: { issue_type: "psychological", salience: 0.9, centrality: 0.58 },
  },
  {
    id: "issue_power_imbalance",
    label: "Issue",
    node_type: "issue",
    name: "Power Imbalance",
    confidence: 0.88,
    properties: { issue_type: "substantive", salience: 0.75, centrality: 0.48 },
  },

  /* ---- 4 Interests ---- */
  {
    id: "interest_alex_safety",
    label: "Interest",
    node_type: "interest",
    name: "Alex: Psychological Safety",
    confidence: 0.9,
    properties: { holder: "Alex Chen", interest_type: "psychological", priority: 5, centrality: 0.42 },
  },
  {
    id: "interest_alex_growth",
    label: "Interest",
    node_type: "interest",
    name: "Alex: Career Growth",
    confidence: 0.88,
    properties: { holder: "Alex Chen", interest_type: "substantive", priority: 4, centrality: 0.38 },
  },
  {
    id: "interest_maya_standards",
    label: "Interest",
    node_type: "interest",
    name: "Maya: Code Standards",
    confidence: 0.9,
    properties: { holder: "Maya Okonkwo", interest_type: "substantive", priority: 5, centrality: 0.4 },
  },
  {
    id: "interest_maya_authority",
    label: "Interest",
    node_type: "interest",
    name: "Maya: Team Authority",
    confidence: 0.88,
    properties: { holder: "Maya Okonkwo", interest_type: "psychological", priority: 5, centrality: 0.38 },
  },

  /* ---- 2 Norms ---- */
  {
    id: "norm_handbook",
    label: "Norm",
    node_type: "norm",
    name: "Employee Handbook",
    confidence: 0.92,
    properties: { norm_type: "policy", binding: true, centrality: 0.35 },
  },
  {
    id: "norm_feha",
    label: "Norm",
    node_type: "norm",
    name: "California FEHA",
    confidence: 0.95,
    properties: { norm_type: "statute", binding: true, centrality: 0.3 },
  },

  /* ---- 1 Process ---- */
  {
    id: "process_hr_mediation",
    label: "Process",
    node_type: "process",
    name: "Facilitative HR Mediation",
    confidence: 0.9,
    properties: { process_type: "interest_based", status: "active", centrality: 0.52 },
  },

  /* ---- 1 Outcome ---- */
  {
    id: "outcome_agreement",
    label: "Outcome",
    node_type: "outcome",
    name: "Working Agreement Draft",
    confidence: 0.78,
    properties: { outcome_type: "agreement", satisfaction_a: 0.6, satisfaction_b: 0.5, centrality: 0.32 },
  },

  /* ---- 2 Narratives ---- */
  {
    id: "narrative_alex_bullying",
    label: "Narrative",
    node_type: "narrative",
    name: "Bullying Narrative",
    confidence: 0.85,
    properties: { holder: "Alex Chen", dominance: "dominant", frame_type: "characterization", centrality: 0.4 },
  },
  {
    id: "narrative_maya_standards",
    label: "Narrative",
    node_type: "narrative",
    name: "Standards Narrative",
    confidence: 0.85,
    properties: { holder: "Maya Okonkwo", dominance: "counter", frame_type: "moral", centrality: 0.38 },
  },

  /* ---- 3 Emotional States ---- */
  {
    id: "emotion_alex_fear",
    label: "Emotional State",
    node_type: "emotional_state",
    name: "Alex: Fear",
    confidence: 0.88,
    properties: { holder: "Alex Chen", valence: "negative", intensity: 0.9, centrality: 0.35 },
  },
  {
    id: "emotion_alex_shame",
    label: "Emotional State",
    node_type: "emotional_state",
    name: "Alex: Shame",
    confidence: 0.85,
    properties: { holder: "Alex Chen", valence: "negative", intensity: 0.8, centrality: 0.32 },
  },
  {
    id: "emotion_maya_anger",
    label: "Emotional State",
    node_type: "emotional_state",
    name: "Maya: Anger",
    confidence: 0.82,
    properties: { holder: "Maya Okonkwo", valence: "negative", intensity: 0.7, centrality: 0.3 },
  },

  /* ---- 2 Trust States ---- */
  {
    id: "trust_alex_maya",
    label: "Trust State",
    node_type: "trust_state",
    name: "Alex \u2192 Maya Trust",
    confidence: 0.88,
    properties: { from: "Alex Chen", to: "Maya Okonkwo", overall: 0.15, basis: "calculus", centrality: 0.4 },
  },
  {
    id: "trust_alex_jordan",
    label: "Trust State",
    node_type: "trust_state",
    name: "Alex \u2192 Jordan Trust",
    confidence: 0.85,
    properties: { from: "Alex Chen", to: "Jordan Reyes", overall: 0.65, basis: "knowledge", centrality: 0.34 },
  },

  /* ---- 2 Power Dynamics ---- */
  {
    id: "power_maya_positional",
    label: "Power Dynamic",
    node_type: "power_dynamic",
    name: "Maya: Positional Power",
    confidence: 0.92,
    properties: { domain: "positional", magnitude: 0.75, direction: "Maya over Alex", centrality: 0.42 },
  },
  {
    id: "power_maya_expert",
    label: "Power Dynamic",
    node_type: "power_dynamic",
    name: "Maya: Expert Power",
    confidence: 0.9,
    properties: { domain: "expert", magnitude: 0.8, direction: "Maya over Alex", centrality: 0.4 },
  },

  /* ---- 1 Location ---- */
  {
    id: "location_hq",
    label: "Location",
    node_type: "location",
    name: "Northwind HQ",
    confidence: 0.95,
    properties: { location_type: "building", city: "San Francisco", centrality: 0.22 },
  },

  /* ---- 1 Evidence ---- */
  {
    id: "evidence_pr847",
    label: "Evidence",
    node_type: "evidence",
    name: "GitHub PR #847",
    confidence: 0.95,
    properties: { evidence_type: "digital_record", reliability: 0.95, centrality: 0.28 },
  },

  /* ---- 1 Role ---- */
  {
    id: "role_mediator",
    label: "Role",
    node_type: "role",
    name: "Jordan as Mediator",
    confidence: 0.9,
    properties: { role_type: "mediator", assigned_to: "Jordan Reyes", centrality: 0.3 },
  },
];

const FALLBACK_LINKS: GraphLink[] = [
  /* ---- PARTY_TO (4) ---- */
  { id: "e1", source: "actor_alex", target: "conflict_code_review", edge_type: "PARTY_TO", weight: 0.9, confidence: 0.95 },
  { id: "e2", source: "actor_maya", target: "conflict_code_review", edge_type: "PARTY_TO", weight: 0.9, confidence: 0.95 },
  { id: "e3", source: "actor_jordan", target: "conflict_code_review", edge_type: "PARTY_TO", weight: 0.7, confidence: 0.9 },
  { id: "e4", source: "actor_northwind", target: "conflict_code_review", edge_type: "PARTY_TO", weight: 0.5, confidence: 0.85 },

  /* ---- PARTICIPATES_IN (3) ---- */
  { id: "e5", source: "actor_maya", target: "event_code_review_incident", edge_type: "PARTICIPATES_IN", weight: 0.9, confidence: 0.92 },
  { id: "e6", source: "actor_alex", target: "event_code_review_incident", edge_type: "PARTICIPATES_IN", weight: 0.85, confidence: 0.92 },
  { id: "e7", source: "actor_jordan", target: "event_mediation_session", edge_type: "PARTICIPATES_IN", weight: 0.8, confidence: 0.9 },

  /* ---- HAS_INTEREST (4) ---- */
  { id: "e8", source: "actor_alex", target: "interest_alex_safety", edge_type: "HAS_INTEREST", weight: 0.9, confidence: 0.9 },
  { id: "e9", source: "actor_alex", target: "interest_alex_growth", edge_type: "HAS_INTEREST", weight: 0.8, confidence: 0.88 },
  { id: "e10", source: "actor_maya", target: "interest_maya_standards", edge_type: "HAS_INTEREST", weight: 0.85, confidence: 0.9 },
  { id: "e11", source: "actor_maya", target: "interest_maya_authority", edge_type: "HAS_INTEREST", weight: 0.8, confidence: 0.88 },

  /* ---- PART_OF: events & issues -> conflict (9) ---- */
  { id: "e12", source: "event_first_tension", target: "conflict_code_review", edge_type: "PART_OF", weight: 0.7, confidence: 0.88 },
  { id: "e13", source: "event_alex_avoids", target: "conflict_code_review", edge_type: "PART_OF", weight: 0.65, confidence: 0.85 },
  { id: "e14", source: "event_code_review_incident", target: "conflict_code_review", edge_type: "PART_OF", weight: 0.9, confidence: 0.95 },
  { id: "e15", source: "event_formal_complaint", target: "conflict_code_review", edge_type: "PART_OF", weight: 0.85, confidence: 0.92 },
  { id: "e16", source: "event_team_splits", target: "conflict_code_review", edge_type: "PART_OF", weight: 0.75, confidence: 0.88 },
  { id: "e17", source: "event_mediation_session", target: "conflict_code_review", edge_type: "PART_OF", weight: 0.8, confidence: 0.9 },
  { id: "e18", source: "issue_communication_style", target: "conflict_code_review", edge_type: "PART_OF", weight: 0.85, confidence: 0.92 },
  { id: "e19", source: "issue_professional_respect", target: "conflict_code_review", edge_type: "PART_OF", weight: 0.9, confidence: 0.94 },
  { id: "e20", source: "issue_power_imbalance", target: "conflict_code_review", edge_type: "PART_OF", weight: 0.75, confidence: 0.88 },

  /* ---- CAUSED: causal chain (5) ---- */
  { id: "e21", source: "event_first_tension", target: "event_alex_avoids", edge_type: "CAUSED", weight: 0.75, confidence: 0.85 },
  { id: "e22", source: "event_alex_avoids", target: "event_code_review_incident", edge_type: "CAUSED", weight: 0.8, confidence: 0.88 },
  { id: "e23", source: "event_code_review_incident", target: "event_formal_complaint", edge_type: "CAUSED", weight: 0.88, confidence: 0.92 },
  { id: "e24", source: "event_formal_complaint", target: "event_team_splits", edge_type: "CAUSED", weight: 0.78, confidence: 0.88 },
  { id: "e25", source: "event_team_splits", target: "event_mediation_session", edge_type: "CAUSED", weight: 0.72, confidence: 0.85 },

  /* ---- AT_LOCATION (1) ---- */
  { id: "e26", source: "event_code_review_incident", target: "location_hq", edge_type: "AT_LOCATION", weight: 0.6, confidence: 0.95 },

  /* ---- ALLIED_WITH (2) ---- */
  { id: "e27", source: "actor_alex", target: "actor_kai", edge_type: "ALLIED_WITH", weight: 0.7, confidence: 0.82 },
  { id: "e28", source: "actor_maya", target: "actor_elena", edge_type: "ALLIED_WITH", weight: 0.65, confidence: 0.8 },

  /* ---- OPPOSED_TO (1) ---- */
  { id: "e29", source: "actor_alex", target: "actor_maya", edge_type: "OPPOSED_TO", weight: 0.8, confidence: 0.88 },

  /* ---- HAS_POWER_OVER (2) ---- */
  { id: "e30", source: "actor_maya", target: "actor_alex", edge_type: "HAS_POWER_OVER", weight: 0.75, confidence: 0.92 },
  { id: "e31", source: "actor_maya", target: "actor_alex", edge_type: "HAS_POWER_OVER", weight: 0.8, confidence: 0.9 },

  /* ---- MEMBER_OF (6) ---- */
  { id: "e32", source: "actor_alex", target: "actor_northwind", edge_type: "MEMBER_OF", weight: 0.5, confidence: 0.95 },
  { id: "e33", source: "actor_maya", target: "actor_northwind", edge_type: "MEMBER_OF", weight: 0.5, confidence: 0.95 },
  { id: "e34", source: "actor_jordan", target: "actor_northwind", edge_type: "MEMBER_OF", weight: 0.5, confidence: 0.92 },
  { id: "e35", source: "actor_kai", target: "actor_northwind", edge_type: "MEMBER_OF", weight: 0.5, confidence: 0.88 },
  { id: "e36", source: "actor_elena", target: "actor_northwind", edge_type: "MEMBER_OF", weight: 0.5, confidence: 0.88 },
  { id: "e37", source: "actor_priya", target: "actor_northwind", edge_type: "MEMBER_OF", weight: 0.5, confidence: 0.85 },

  /* ---- GOVERNED_BY (2) ---- */
  { id: "e38", source: "conflict_code_review", target: "norm_handbook", edge_type: "GOVERNED_BY", weight: 0.7, confidence: 0.92 },
  { id: "e39", source: "conflict_code_review", target: "norm_feha", edge_type: "GOVERNED_BY", weight: 0.6, confidence: 0.88 },

  /* ---- RESOLVED_THROUGH (1) ---- */
  { id: "e40", source: "conflict_code_review", target: "process_hr_mediation", edge_type: "RESOLVED_THROUGH", weight: 0.75, confidence: 0.88 },

  /* ---- PRODUCES (1) ---- */
  { id: "e41", source: "process_hr_mediation", target: "outcome_agreement", edge_type: "PRODUCES", weight: 0.65, confidence: 0.78 },

  /* ---- EXPERIENCES (3) ---- */
  { id: "e42", source: "actor_alex", target: "emotion_alex_fear", edge_type: "EXPERIENCES", weight: 0.85, confidence: 0.88 },
  { id: "e43", source: "actor_alex", target: "emotion_alex_shame", edge_type: "EXPERIENCES", weight: 0.8, confidence: 0.85 },
  { id: "e44", source: "actor_maya", target: "emotion_maya_anger", edge_type: "EXPERIENCES", weight: 0.7, confidence: 0.82 },

  /* ---- TRUSTS (2) ---- */
  { id: "e45", source: "actor_alex", target: "trust_alex_maya", edge_type: "TRUSTS", weight: 0.4, confidence: 0.88 },
  { id: "e46", source: "actor_alex", target: "trust_alex_jordan", edge_type: "TRUSTS", weight: 0.7, confidence: 0.85 },

  /* ---- PROMOTES (2) ---- */
  { id: "e47", source: "actor_alex", target: "narrative_alex_bullying", edge_type: "PROMOTES", weight: 0.8, confidence: 0.85 },
  { id: "e48", source: "actor_maya", target: "narrative_maya_standards", edge_type: "PROMOTES", weight: 0.75, confidence: 0.85 },

  /* ---- ABOUT (2) ---- */
  { id: "e49", source: "narrative_alex_bullying", target: "conflict_code_review", edge_type: "ABOUT", weight: 0.8, confidence: 0.85 },
  { id: "e50", source: "narrative_maya_standards", target: "conflict_code_review", edge_type: "ABOUT", weight: 0.75, confidence: 0.85 },

  /* ---- EVIDENCED_BY (1) ---- */
  { id: "e51", source: "event_first_tension", target: "evidence_pr847", edge_type: "EVIDENCED_BY", weight: 0.8, confidence: 0.92 },

  /* ---- VIOLATES (1) ---- */
  { id: "e52", source: "event_code_review_incident", target: "norm_handbook", edge_type: "VIOLATES", weight: 0.72, confidence: 0.88 },

  /* ---- WITHIN (1) ---- */
  { id: "e53", source: "location_hq", target: "actor_northwind", edge_type: "WITHIN", weight: 0.5, confidence: 0.95 },
];

const FALLBACK_GRAPH: GraphData = {
  nodes: FALLBACK_NODES,
  links: FALLBACK_LINKS,
};

/* ------------------------------------------------------------------ */
/*  Loading step trace                                                 */
/* ------------------------------------------------------------------ */

interface Step {
  label: string;
  status: "pending" | "active" | "done" | "error";
}

const INITIAL_STEPS: Step[] = [
  { label: "Parsing conflict narrative", status: "pending" },
  { label: "Extracting entities (GLiNER + Gemini)", status: "pending" },
  { label: "Building knowledge graph", status: "pending" },
  { label: "Running symbolic inference", status: "pending" },
  { label: "Rendering visualization", status: "pending" },
];

/* ------------------------------------------------------------------ */
/*  Stats helpers                                                      */
/* ------------------------------------------------------------------ */

function computeStats(data: GraphData) {
  const typeCount: Record<string, number> = {};
  for (const node of data.nodes) {
    typeCount[node.node_type] = (typeCount[node.node_type] || 0) + 1;
  }

  const edgeTypeCount: Record<string, number> = {};
  for (const link of data.links) {
    edgeTypeCount[link.edge_type] = (edgeTypeCount[link.edge_type] || 0) + 1;
  }

  const avgConfidence =
    data.nodes.length > 0
      ? data.nodes.reduce((sum, n) => sum + n.confidence, 0) / data.nodes.length
      : 0;

  return { typeCount, edgeTypeCount, avgConfidence };
}

/* ------------------------------------------------------------------ */
/*  Computed analysis panel helpers                                     */
/* ------------------------------------------------------------------ */

interface ComputedAnalysis {
  glaslStage: number;
  glaslLabel: string;
  deterministicCount: number;
  probabilisticCount: number;
  theoryFrameworks: { name: string; fired: boolean; description: string }[];
  confidenceBuckets: { label: string; count: number; color: string }[];
}

function deriveAnalysis(data: GraphData): ComputedAnalysis {
  // Derive Glasl stage from conflict nodes
  let glaslStage = 0;
  for (const node of data.nodes) {
    if (node.node_type === "conflict" && node.properties.glasl_stage) {
      glaslStage = node.properties.glasl_stage as number;
      break;
    }
  }

  const glaslLabels: Record<number, string> = {
    1: "Hardening",
    2: "Polarization & Debate",
    3: "Actions Not Words",
    4: "Coalitions",
    5: "Loss of Face",
    6: "Strategies of Threats",
    7: "Limited Destructive Blows",
    8: "Fragmentation",
    9: "Together into the Abyss",
  };

  // Count deterministic vs probabilistic based on confidence levels
  let deterministicCount = 0;
  let probabilisticCount = 0;
  for (const node of data.nodes) {
    if (node.confidence >= 0.9) {
      deterministicCount++;
    } else {
      probabilisticCount++;
    }
  }

  // Which theory frameworks are relevant
  const hasNorms = data.nodes.some((n) => n.node_type === "norm");
  const hasPower = data.nodes.some((n) => n.node_type === "power_dynamic");
  const hasTrust = data.nodes.some((n) => n.node_type === "trust_state");
  const hasEmotional = data.nodes.some((n) => n.node_type === "emotional_state");
  const hasProcess = data.nodes.some((n) => n.node_type === "process");
  const hasInterest = data.nodes.some((n) => n.node_type === "interest");

  const theoryFrameworks = [
    { name: "Glasl Escalation Model", fired: glaslStage > 0, description: "Stage derivation from event causal chain" },
    { name: "French & Raven Power Taxonomy", fired: hasPower, description: "Power type and magnitude analysis" },
    { name: "Fisher & Ury (Getting to Yes)", fired: hasInterest, description: "Interest-based negotiation mapping" },
    { name: "Lewicki Trust Model", fired: hasTrust, description: "Trust state and trajectory computation" },
    { name: "Norm Compliance Analysis", fired: hasNorms, description: "Norm-event violation matching" },
    { name: "Affect-Cognition Framework", fired: hasEmotional, description: "Emotional state impact on behavior" },
    { name: "Zartman Ripeness Theory", fired: hasProcess, description: "Mutually hurting stalemate detection" },
  ];

  // Confidence distribution
  const buckets = [
    { label: "\u226595%", count: 0, color: "#22c55e" },
    { label: "85-94%", count: 0, color: "#3b82f6" },
    { label: "75-84%", count: 0, color: "#eab308" },
    { label: "<75%", count: 0, color: "#ef4444" },
  ];
  for (const node of data.nodes) {
    const pct = node.confidence * 100;
    if (pct >= 95) buckets[0].count++;
    else if (pct >= 85) buckets[1].count++;
    else if (pct >= 75) buckets[2].count++;
    else buckets[3].count++;
  }

  return {
    glaslStage,
    glaslLabel: glaslLabels[glaslStage] || "Unknown",
    deterministicCount,
    probabilisticCount,
    theoryFrameworks,
    confidenceBuckets: buckets,
  };
}

/* ------------------------------------------------------------------ */
/*  Main Demo Page                                                     */
/* ------------------------------------------------------------------ */

export default function DemoPage() {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [steps, setSteps] = useState<Step[]>(INITIAL_STEPS);
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [isFallback, setIsFallback] = useState(false);
  const resultsRef = useRef<HTMLDivElement>(null);
  const [expandedScenario, setExpandedScenario] = useState<string | null>(null);

  /* Advance loading step trace */
  const advanceStep = useCallback(
    (index: number, status: "active" | "done" | "error") => {
      setSteps((prev) =>
        prev.map((s, i) => {
          if (i === index) return { ...s, status };
          if (i < index && s.status !== "error") return { ...s, status: "done" };
          return s;
        }),
      );
    },
    [],
  );

  /* Simulate step progress (used for both API and fallback paths) */
  const simulateSteps = useCallback(
    async (useFallback: boolean) => {
      const delays = [600, 900, 700, 500, 400];
      for (let i = 0; i < INITIAL_STEPS.length; i++) {
        advanceStep(i, "active");
        await new Promise((r) => setTimeout(r, delays[i]));
        if (i === INITIAL_STEPS.length - 1) {
          advanceStep(i, "done");
        } else if (useFallback && i === 1) {
          advanceStep(i, "error");
          await new Promise((r) => setTimeout(r, 300));
          for (let j = i + 1; j < INITIAL_STEPS.length; j++) {
            advanceStep(j, "active");
            await new Promise((r) => setTimeout(r, delays[j]));
            advanceStep(j, "done");
          }
          return;
        } else {
          advanceStep(i, "done");
        }
      }
    },
    [advanceStep],
  );

  /* Handle Analyze */
  const handleAnalyze = useCallback(async () => {
    if (!text.trim()) return;
    setLoading(true);
    setGraphData(null);
    setIsFallback(false);
    setSteps(INITIAL_STEPS.map((s) => ({ ...s, status: "pending" })));

    let usedFallback = false;

    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";
      const apiKey =
        typeof window !== "undefined" ? localStorage.getItem("dialectica_api_key") : null;
      const headers: Record<string, string> = {
        "Content-Type": "application/json",
        ...(apiKey ? { "X-API-Key": apiKey } : {}),
      };

      advanceStep(0, "active");
      await new Promise((r) => setTimeout(r, 500));
      advanceStep(0, "done");
      advanceStep(1, "active");

      const extractRes = await fetch(`${API_URL}/v1/extract`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          workspace_id: "demo",
          text: text.trim(),
          tier: "standard",
        }),
        signal: AbortSignal.timeout(10000),
      });

      if (!extractRes.ok) throw new Error(`API ${extractRes.status}`);

      const extraction = await extractRes.json();
      advanceStep(1, "done");

      advanceStep(2, "active");
      await new Promise((r) => setTimeout(r, 400));

      const graphRes = await fetch(
        `${API_URL}/v1/workspaces/${extraction.workspace_id}/graph`,
        { headers },
      );
      if (!graphRes.ok) throw new Error(`Graph API ${graphRes.status}`);
      const graph: GraphData = await graphRes.json();
      advanceStep(2, "done");

      advanceStep(3, "active");
      await new Promise((r) => setTimeout(r, 500));
      advanceStep(3, "done");

      advanceStep(4, "active");
      await new Promise((r) => setTimeout(r, 300));
      advanceStep(4, "done");

      setGraphData(graph);
    } catch {
      usedFallback = true;
      setSteps(INITIAL_STEPS.map((s) => ({ ...s, status: "pending" })));
      await simulateSteps(true);
      setGraphData(FALLBACK_GRAPH);
      setIsFallback(true);
    } finally {
      setLoading(false);
      if (!usedFallback) {
        setIsFallback(false);
      }
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 200);
    }
  }, [text, advanceStep, simulateSteps]);

  const stats = graphData ? computeStats(graphData) : null;
  const analysis = graphData ? deriveAnalysis(graphData) : null;

  return (
    <div className="min-h-screen bg-background text-text-primary">
      {/* ---- Header ---- */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-sm border-b border-border">
        <div className="max-w-7xl mx-auto px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Network className="text-accent" size={22} />
            <span className="text-lg font-bold tracking-tight">
              <span className="text-accent">DIALECTICA</span>
              <span className="text-text-secondary font-normal text-sm ml-2">by TACITUS</span>
            </span>
          </div>
          <a
            href="/"
            className="text-xs text-text-secondary hover:text-text-primary transition-colors"
          >
            Back to Dashboard
          </a>
        </div>
      </header>

      {/* ---- Intro Section ---- */}
      <section className="pt-24 pb-6 px-6">
        <div className="max-w-3xl mx-auto text-center space-y-4">
          <h1 className="text-4xl sm:text-5xl font-bold tracking-tight leading-tight">
            See <span className="text-accent">DIALECTICA</span> in Action
          </h1>
          <p className="text-lg text-text-secondary max-w-2xl mx-auto">
            Paste any conflict narrative below &mdash; or try one of our annotated examples
            to see what the{" "}
            <a href="https://tacitus.me" target="_blank" rel="noopener noreferrer" className="text-accent hover:text-teal-300 transition-colors">TACITUS</a>
            {" "}trust graph extracts and computes.
          </p>
          <div className="flex items-center justify-center gap-2 text-sm text-text-secondary/70">
            <Zap size={14} className="text-accent" />
            <span>
              DIALECTICA is the context &amp; data layer &mdash; the deterministic foundation that other TACITUS apps reason over.
            </span>
          </div>
        </div>
      </section>

      {/* ---- Annotated Examples ---- */}
      <section className="px-6 pb-8">
        <div className="max-w-5xl mx-auto">
          <div className="flex items-center gap-2 mb-4">
            <BookOpen size={16} className="text-accent" />
            <h2 className="text-sm font-semibold text-text-primary uppercase tracking-wider">
              Annotated Examples
            </h2>
            <span className="text-xs text-text-secondary/60 ml-1">
              &mdash; click to expand, then load into the analyzer
            </span>
          </div>

          <div className="space-y-3">
            {ANNOTATED_SCENARIOS.map((scenario) => {
              const isExpanded = expandedScenario === scenario.id;
              const Icon = scenario.icon;
              return (
                <div
                  key={scenario.id}
                  className="bg-surface border border-border rounded-lg overflow-hidden transition-all"
                >
                  {/* Scenario Header */}
                  <button
                    onClick={() =>
                      setExpandedScenario(isExpanded ? null : scenario.id)
                    }
                    className="w-full flex items-center gap-4 px-5 py-4 text-left hover:bg-surface-hover transition-colors"
                  >
                    <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center shrink-0">
                      <Icon size={20} className="text-accent" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-semibold text-text-primary">
                          {scenario.title}
                        </span>
                        <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-accent/10 text-accent uppercase tracking-wider">
                          {scenario.domain}
                        </span>
                      </div>
                      <p className="text-xs text-text-secondary mt-0.5 truncate">
                        {scenario.subtitle}
                      </p>
                    </div>
                    <div className="shrink-0 text-text-secondary">
                      {isExpanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                    </div>
                  </button>

                  {/* Expanded Content */}
                  {isExpanded && (
                    <div className="border-t border-border px-5 py-4 space-y-5 animate-fade-in">
                      {/* Narrative preview */}
                      <div>
                        <h4 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-2">
                          Conflict Narrative
                        </h4>
                        <p className="text-sm text-text-secondary leading-relaxed line-clamp-4">
                          {scenario.text.slice(0, 300)}...
                        </p>
                      </div>

                      {/* Extracted Summary */}
                      <div className="bg-teal-500/5 border border-teal-500/20 rounded-lg p-4">
                        <div className="flex items-center gap-2 mb-2">
                          <Network size={14} className="text-teal-400" />
                          <h4 className="text-xs font-semibold text-teal-400 uppercase tracking-wider">
                            What DIALECTICA Extracts
                          </h4>
                        </div>
                        <p className="text-sm text-teal-300/90 leading-relaxed">
                          {scenario.extractedSummary}
                        </p>
                      </div>

                      {/* Why It Matters */}
                      <div className="bg-accent/5 border border-accent/20 rounded-lg p-4">
                        <div className="flex items-center gap-2 mb-2">
                          <Zap size={14} className="text-accent" />
                          <h4 className="text-xs font-semibold text-accent uppercase tracking-wider">
                            Why This Matters
                          </h4>
                        </div>
                        <p className="text-sm text-text-secondary leading-relaxed">
                          {scenario.whyItMatters}
                        </p>
                      </div>

                      {/* Questions only answerable with structured knowledge */}
                      <div>
                        <h4 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-3 flex items-center gap-1.5">
                          <Brain size={12} className="text-accent" />
                          Questions only answerable with structured knowledge
                          <span className="text-[10px] font-normal text-text-secondary/50 ml-1">
                            ({scenario.questions.length} computed analyses)
                          </span>
                        </h4>
                        <div className="space-y-3">
                          {scenario.questions.map((q, qi) => (
                            <div
                              key={qi}
                              className="bg-background border border-border rounded-lg overflow-hidden"
                            >
                              <div className="flex flex-col sm:flex-row">
                                {/* Question (left column) */}
                                <div className="sm:w-[280px] shrink-0 p-4 border-b sm:border-b-0 sm:border-r border-border bg-surface/50">
                                  <div className="flex items-start gap-2">
                                    <Target
                                      size={14}
                                      className="text-accent shrink-0 mt-0.5"
                                    />
                                    <span className="text-sm font-medium text-text-primary leading-snug">
                                      {q.question}
                                    </span>
                                  </div>
                                  <div className="mt-2 flex items-center gap-1.5">
                                    <div className="w-1.5 h-1.5 rounded-full bg-teal-400" />
                                    <span className="text-[10px] font-semibold text-teal-400 uppercase tracking-wider">
                                      DIALECTICA Computed
                                    </span>
                                  </div>
                                </div>
                                {/* Answer (right column) */}
                                <div className="flex-1 p-4">
                                  <div className="text-xs text-text-secondary leading-relaxed whitespace-pre-line">
                                    {q.dialecticaAnswer.split(/(\b\d+\.\d{2}\b|\b0\.\d+\b|\bmagnitude \d+\.\d+\b|\bstrength \d+\.\d+\b|\bscore[:\s]*\d+\.\d+\b|\bpriority[:\s]*\d+\.\d+\b|\bintensity \d+\.\d+\b|\bweight=\d+\.\d+\b|\bSeverity[:\s]*\d+\.\d+\b)/).map((part, pi) =>
                                      /\b\d+\.\d{2}\b|\b0\.\d+\b|magnitude \d+\.\d+|strength \d+\.\d+|score[:\s]*\d+\.\d+|priority[:\s]*\d+\.\d+|intensity \d+\.\d+|weight=\d+\.\d+|Severity[:\s]*\d+\.\d+/.test(part)
                                        ? <span key={pi} className="text-teal-400 font-mono font-medium">{part}</span>
                                        : <span key={pi}>{part}</span>
                                    )}
                                  </div>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Load & Analyze button */}
                      <div className="flex items-center gap-3 pt-2">
                        <button
                          onClick={() => {
                            setText(scenario.text);
                            setExpandedScenario(null);
                            window.scrollTo({ top: 0, behavior: "smooth" });
                          }}
                          disabled={loading}
                          className="inline-flex items-center gap-2 px-6 py-3 bg-teal-600 hover:bg-teal-500 text-white text-sm font-semibold rounded-lg transition-all disabled:opacity-50 shadow-lg shadow-teal-600/20 hover:shadow-teal-500/30"
                        >
                          <Sparkles size={16} />
                          Load &amp; Analyze This Scenario
                          <ArrowRight size={14} />
                        </button>
                        <span className="text-xs text-text-secondary/50">
                          Loads the full narrative into the analyzer above
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ---- Text Input Section ---- */}
      <section className="px-6 pb-10">
        <div className="max-w-3xl mx-auto space-y-5">
          {/* Textarea */}
          <div className="relative">
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Describe a conflict, dispute, or negotiation scenario..."
              rows={8}
              className="w-full bg-surface border border-border rounded-lg px-4 py-3 text-sm text-text-primary placeholder:text-text-secondary/50 focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-accent transition-all resize-y min-h-[200px]"
              disabled={loading}
            />
            <div className="absolute bottom-3 right-3 text-xs text-text-secondary/50">
              {text.length > 0 ? `${text.split(/\s+/).filter(Boolean).length} words` : ""}
            </div>
          </div>

          {/* Analyze Button */}
          <div className="text-center">
            <button
              onClick={handleAnalyze}
              disabled={loading || !text.trim()}
              className="inline-flex items-center gap-2 px-8 py-3 bg-teal-600 hover:bg-teal-500 disabled:bg-teal-600/50 text-white font-semibold rounded-lg text-base transition-all disabled:cursor-not-allowed shadow-lg shadow-teal-600/20 hover:shadow-teal-500/30"
            >
              {loading ? (
                <>
                  <Loader2 size={18} className="animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Sparkles size={18} />
                  Analyze
                  <ArrowRight size={16} />
                </>
              )}
            </button>
          </div>
        </div>
      </section>

      {/* ---- Loading Step Trace ---- */}
      {loading && (
        <section className="px-6 pb-8">
          <div className="max-w-md mx-auto space-y-3">
            {steps.map((step, i) => (
              <div
                key={i}
                className="flex items-center gap-3 text-sm transition-all duration-300"
              >
                {step.status === "pending" && (
                  <div className="w-5 h-5 rounded-full border border-surface-active" />
                )}
                {step.status === "active" && (
                  <Loader2 size={18} className="text-accent animate-spin shrink-0" />
                )}
                {step.status === "done" && (
                  <CheckCircle2 size={18} className="text-green-500 shrink-0" />
                )}
                {step.status === "error" && (
                  <AlertTriangle size={18} className="text-amber-500 shrink-0" />
                )}
                <span
                  className={
                    step.status === "active"
                      ? "text-text-primary"
                      : step.status === "done"
                        ? "text-text-secondary"
                        : step.status === "error"
                          ? "text-amber-400"
                          : "text-text-secondary/50"
                  }
                >
                  {step.label}
                  {step.status === "error" && (
                    <span className="ml-2 text-xs text-amber-400/70">
                      (API offline &mdash; using fallback)
                    </span>
                  )}
                </span>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* ---- Structured Analysis Dashboard ---- */}
      {graphData && analysis && stats && (
        <section ref={resultsRef} className="px-6 pb-12 animate-fade-in">
          <div className="max-w-7xl mx-auto space-y-6">
            {/* Fallback Banner */}
            {isFallback && (
              <div className="flex items-center gap-2 px-4 py-2.5 bg-amber-500/10 border border-amber-500/20 rounded-lg text-sm text-amber-400">
                <AlertTriangle size={16} className="shrink-0" />
                <span>
                  Demo mode &mdash; API offline. Showing sample HR mediation data.
                </span>
              </div>
            )}

            {/* Dashboard Header */}
            <div className="flex items-center gap-3">
              <Brain size={20} className="text-teal-400" />
              <h2 className="text-xl font-bold text-text-primary">
                Structured Analysis Dashboard
              </h2>
              <span className="text-xs text-text-secondary/60 ml-1">
                Deterministic symbolic reasoning + structured extraction
              </span>
            </div>

            {/* ============ PANEL 1: Conflict Overview (full width) ============ */}
            <ConflictOverviewPanel graphData={graphData} analysis={analysis} stats={stats} />

            {/* ============ 2-column grid for paired panels ============ */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* PANEL 2: Actors & Power Map */}
              <ActorsPowerPanel graphData={graphData} />

              {/* PANEL 3: Event Timeline & Causal Chain */}
              <EventTimelinePanel graphData={graphData} />

              {/* PANEL 4: Interests & Issues */}
              <InterestsIssuesPanel graphData={graphData} />

              {/* PANEL 5: Emotional & Trust State */}
              <EmotionalTrustPanel graphData={graphData} />

              {/* PANEL 6: Norms & Compliance */}
              <NormsCompliancePanel graphData={graphData} />

              {/* PANEL 7: Narratives & Frames */}
              <NarrativesFramesPanel graphData={graphData} />
            </div>

            {/* ============ PANEL 8: Resolution Path (full width) ============ */}
            <ResolutionPathPanel graphData={graphData} analysis={analysis} />
          </div>
        </section>
      )}

      {/* ---- CTA / Links Section ---- */}
      <section className="px-6 pb-16">
        <div className="max-w-3xl mx-auto">
          <div className="bg-surface border border-border rounded-lg p-8 text-center space-y-6">
            <h2 className="text-2xl font-bold text-text-primary">
              Ready to analyze your own conflicts?
            </h2>
            <p className="text-sm text-text-secondary max-w-lg mx-auto">
              DIALECTICA transforms unstructured conflict narratives into structured
              knowledge graphs with deterministic reasoning &mdash; not just summaries.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <a
                href="/workspaces"
                className="inline-flex items-center gap-2 px-6 py-3 bg-teal-600 hover:bg-teal-500 text-white font-semibold rounded-lg text-sm transition-all shadow-lg shadow-teal-600/20 hover:shadow-teal-500/30"
              >
                <Network size={16} />
                Open Workspaces
                <span className="ml-1 text-[10px] font-medium px-1.5 py-0.5 rounded-full bg-white/20 uppercase tracking-wider">
                  Coming Soon
                </span>
              </a>
              <a
                href="/admin/architecture"
                className="inline-flex items-center gap-2 px-6 py-3 bg-surface border border-border hover:border-border-hover text-text-primary font-medium rounded-lg text-sm transition-all hover:bg-surface-hover"
              >
                Explore the full architecture
                <ExternalLink size={14} className="text-text-secondary" />
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* ---- Footer ---- */}
      <footer className="border-t border-border py-6 px-6 text-center text-xs text-text-secondary/50">
        DIALECTICA by TACITUS &mdash; The Universal Data Layer for Human Friction
      </footer>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Stat Card component                                                */
/* ------------------------------------------------------------------ */

function StatCard({
  label,
  value,
}: {
  label: string;
  value: string | number;
}) {
  return (
    <div className="bg-background rounded-lg px-3 py-2.5 border border-border">
      <div className="text-xl font-bold text-text-primary font-mono">
        {value}
      </div>
      <div className="text-xs text-text-secondary mt-0.5">{label}</div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Helper: resolve link source/target to string id                    */
/* ------------------------------------------------------------------ */

function linkId(ref: string | GraphNode): string {
  return typeof ref === "string" ? ref : ref.id;
}

/* ------------------------------------------------------------------ */
/*  Helper: get nodes by type                                          */
/* ------------------------------------------------------------------ */

function nodesByType(data: GraphData, type: string): GraphNode[] {
  return data.nodes.filter((n) => n.node_type === type);
}

/* ------------------------------------------------------------------ */
/*  Helper: get links by edge type                                     */
/* ------------------------------------------------------------------ */

function linksByType(data: GraphData, type: string): GraphLink[] {
  return data.links.filter((l) => l.edge_type === type);
}

/* ------------------------------------------------------------------ */
/*  Helper: find node by id                                            */
/* ------------------------------------------------------------------ */

function findNode(data: GraphData, id: string): GraphNode | undefined {
  return data.nodes.find((n) => n.id === id);
}

/* ------------------------------------------------------------------ */
/*  PANEL 1: Conflict Overview                                         */
/* ------------------------------------------------------------------ */

function ConflictOverviewPanel({
  graphData,
  analysis,
  stats,
}: {
  graphData: GraphData;
  analysis: ComputedAnalysis;
  stats: ReturnType<typeof computeStats>;
}) {
  const conflicts = nodesByType(graphData, "conflict");
  const conflict = conflicts[0];

  const glaslStage = (conflict?.properties.glasl_stage as number) || 0;
  const conflictScale = (conflict?.properties.scale as string) || "unknown";
  const conflictDomain = (conflict?.properties.domain as string) || "unknown";
  const conflictStatus = (conflict?.properties.status as string) || "unknown";
  const kriesbergPhase = (conflict?.properties.kriesberg_phase as string) || "unknown";

  const glaslBadgeColor =
    glaslStage <= 3
      ? "bg-green-500/20 text-green-400 border-green-500/30"
      : glaslStage <= 6
        ? "bg-yellow-500/20 text-yellow-400 border-yellow-500/30"
        : "bg-red-500/20 text-red-400 border-red-500/30";

  return (
    <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-6 space-y-5">
      <div className="flex items-center gap-2">
        <Activity size={16} className="text-teal-400" />
        <h3 className="text-sm font-semibold text-text-primary uppercase tracking-wider">
          Conflict Overview
        </h3>
      </div>

      {conflict ? (
        <>
          <div className="flex flex-col sm:flex-row sm:items-start gap-4">
            <div className="flex-1 space-y-3">
              <div className="flex items-center gap-3 flex-wrap">
                <h4 className="text-lg font-bold text-text-primary">{conflict.name}</h4>
                <span className={`text-[10px] font-semibold px-2.5 py-1 rounded-full border ${glaslBadgeColor} uppercase tracking-wider`}>
                  Glasl Stage {glaslStage}
                </span>
                <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-zinc-800 text-text-secondary border border-zinc-700 capitalize">
                  {conflictScale}
                </span>
                <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-zinc-800 text-text-secondary border border-zinc-700 capitalize">
                  {conflictDomain}
                </span>
              </div>
              <div className="flex items-center gap-4 text-xs text-text-secondary">
                <span>Status: <span className="text-text-primary capitalize">{conflictStatus}</span></span>
                <span>Phase: <span className="text-text-primary capitalize">{kriesbergPhase.replace(/_/g, " ")}</span></span>
              </div>
            </div>
          </div>

          {/* Glasl 9-dot progress */}
          <div className="space-y-2">
            <div className="text-[10px] text-text-secondary uppercase tracking-wider font-semibold">
              Glasl Escalation Position
            </div>
            <div className="flex items-center gap-1.5">
              {Array.from({ length: 9 }, (_, i) => {
                const stage = i + 1;
                const level = glaslLevel(stage);
                const isCurrent = stage === glaslStage;
                const isPast = stage < glaslStage;
                return (
                  <div key={stage} className="flex flex-col items-center gap-1">
                    <div
                      className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold transition-all ${
                        isCurrent
                          ? "ring-2 ring-offset-1 ring-offset-zinc-900"
                          : ""
                      }`}
                      style={{
                        backgroundColor:
                          isCurrent || isPast
                            ? GLASL_COLORS[level]
                            : "rgba(148,163,184,0.12)",
                        color:
                          isCurrent || isPast ? "#000" : "rgba(148,163,184,0.4)",
                        ...(isCurrent ? { "--tw-ring-color": GLASL_COLORS[level] } as React.CSSProperties : {}),
                      }}
                    >
                      {stage}
                    </div>
                  </div>
                );
              })}
            </div>
            <div className="flex justify-between text-[9px] text-text-secondary/50 uppercase tracking-wider px-1" style={{ maxWidth: "calc(9 * 1.5rem + 8 * 0.375rem)" }}>
              <span>win-win</span>
              <span>win-lose</span>
              <span>lose-lose</span>
            </div>
          </div>
        </>
      ) : (
        <p className="text-sm text-text-secondary/50">No conflict node detected in graph</p>
      )}

      {/* Key stats row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2 border-t border-zinc-800">
        <StatCard label="Total Nodes" value={graphData.nodes.length} />
        <StatCard label="Total Edges" value={graphData.links.length} />
        <StatCard label="Deterministic" value={analysis.deterministicCount} />
        <StatCard label="Probabilistic" value={analysis.probabilisticCount} />
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  PANEL 2: Actors & Power Map                                        */
/* ------------------------------------------------------------------ */

function ActorsPowerPanel({ graphData }: { graphData: GraphData }) {
  const actors = nodesByType(graphData, "actor");
  const powerDynamics = nodesByType(graphData, "power_dynamic");
  const alliances = linksByType(graphData, "ALLIED_WITH");
  const oppositions = linksByType(graphData, "OPPOSED_TO");
  const powerLinks = linksByType(graphData, "HAS_POWER_OVER");

  return (
    <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-5 space-y-4">
      <div className="flex items-center gap-2">
        <Users size={16} className="text-teal-400" />
        <h3 className="text-sm font-semibold text-text-primary uppercase tracking-wider">
          Actors &amp; Power Map
        </h3>
        <span className="text-[10px] text-text-secondary/60 ml-auto">{actors.length} actors</span>
      </div>

      {/* Actor list */}
      <div className="space-y-2">
        {actors.map((actor) => {
          const influence = (actor.properties.centrality as number) || 0;
          const role = (actor.properties.role_title as string) || (actor.properties.actor_type as string) || "";
          return (
            <div key={actor.id} className="flex items-center gap-3 bg-zinc-900/80 border border-zinc-800/60 rounded-md px-3 py-2">
              <span
                className="w-2.5 h-2.5 rounded-full shrink-0"
                style={{ backgroundColor: NODE_COLORS.actor }}
              />
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium text-text-primary truncate">{actor.name}</div>
                {role && (
                  <div className="text-[10px] text-text-secondary truncate capitalize">{role}</div>
                )}
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <span className="text-[10px] text-text-secondary font-mono">{Math.round(influence * 100)}%</span>
                <div className="w-16 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-500 rounded-full transition-all"
                    style={{ width: `${influence * 100}%` }}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Power Dynamics */}
      {powerDynamics.length > 0 && (
        <div className="space-y-2 pt-2 border-t border-zinc-800">
          <div className="text-[10px] text-text-secondary uppercase tracking-wider font-semibold">Power Dynamics</div>
          {powerLinks.map((link) => {
            const sourceId = linkId(link.source);
            const targetId = linkId(link.target);
            const sourceNode = findNode(graphData, sourceId);
            const targetNode = findNode(graphData, targetId);
            // Find matching power_dynamic node for this link
            const matchingPD = powerDynamics.find((pd) => {
              const dir = (pd.properties.direction as string) || "";
              return dir.includes(sourceNode?.name || "") && dir.includes(targetNode?.name || "");
            });
            const domain = (matchingPD?.properties.domain as string) || "power";
            const magnitude = link.weight || 0;
            return (
              <div key={link.id} className="flex items-center gap-2 text-xs">
                <span className="text-text-primary font-medium truncate">{sourceNode?.name || sourceId}</span>
                <ArrowRight size={10} className="text-purple-400 shrink-0" />
                <span className="text-text-primary font-medium truncate">{targetNode?.name || targetId}</span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20 capitalize shrink-0">
                  {domain}
                </span>
                <div className="flex items-center gap-1 ml-auto shrink-0">
                  <span className="text-[10px] text-text-secondary font-mono">{magnitude.toFixed(2)}</span>
                  <div className="w-12 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                    <div className="h-full bg-purple-500 rounded-full" style={{ width: `${magnitude * 100}%` }} />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Alliances & Oppositions */}
      {(alliances.length > 0 || oppositions.length > 0) && (
        <div className="space-y-2 pt-2 border-t border-zinc-800">
          <div className="text-[10px] text-text-secondary uppercase tracking-wider font-semibold">Alliances &amp; Oppositions</div>
          {alliances.map((link) => {
            const a = findNode(graphData, linkId(link.source));
            const b = findNode(graphData, linkId(link.target));
            return (
              <div key={link.id} className="flex items-center gap-2 text-xs">
                <div className="w-1.5 h-1.5 rounded-full bg-green-500 shrink-0" />
                <span className="text-text-primary">{a?.name}</span>
                <span className="text-text-secondary">&mdash;</span>
                <span className="text-text-primary">{b?.name}</span>
                <span className="text-green-400/70 text-[10px] ml-auto font-mono">{link.weight.toFixed(2)}</span>
              </div>
            );
          })}
          {oppositions.map((link) => {
            const a = findNode(graphData, linkId(link.source));
            const b = findNode(graphData, linkId(link.target));
            return (
              <div key={link.id} className="flex items-center gap-2 text-xs">
                <div className="w-1.5 h-1.5 rounded-full bg-red-500 shrink-0" />
                <span className="text-text-primary">{a?.name}</span>
                <span className="text-text-secondary">&mdash;</span>
                <span className="text-text-primary">{b?.name}</span>
                <span className="text-red-400/70 text-[10px] ml-auto font-mono">{link.weight.toFixed(2)}</span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  PANEL 3: Event Timeline & Causal Chain                             */
/* ------------------------------------------------------------------ */

const QUAD_CLASS_COLORS: Record<string, string> = {
  tension: "#eab308",
  disapprove: "#f97316",
  demand: "#ef4444",
  consult: "#3b82f6",
  cooperate: "#22c55e",
  withdraw: "#94a3b8",
  polarize: "#a855f7",
};

const MECHANISM_COLORS: Record<string, string> = {
  escalation: "#ef4444",
  retaliation: "#f97316",
  provocation: "#f97316",
  precedent: "#94a3b8",
  "de-escalation_attempt": "#22c55e",
  scope_creep: "#eab308",
  quality_failure: "#ef4444",
  system_failure: "#ef4444",
  resource_strain: "#f97316",
  financial_escalation: "#ef4444",
  negotiation_failure: "#94a3b8",
  initiation: "#3b82f6",
};

function EventTimelinePanel({ graphData }: { graphData: GraphData }) {
  const events = nodesByType(graphData, "event").sort((a, b) => {
    const dateA = (a.properties.occurred_at as string) || "";
    const dateB = (b.properties.occurred_at as string) || "";
    return dateA.localeCompare(dateB);
  });
  const causedLinks = linksByType(graphData, "CAUSED");

  return (
    <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-5 space-y-4">
      <div className="flex items-center gap-2">
        <Clock size={16} className="text-teal-400" />
        <h3 className="text-sm font-semibold text-text-primary uppercase tracking-wider">
          Event Timeline &amp; Causal Chain
        </h3>
        <span className="text-[10px] text-text-secondary/60 ml-auto">{events.length} events</span>
      </div>

      <div className="relative">
        {/* Vertical timeline line */}
        <div className="absolute left-3 top-0 bottom-0 w-px bg-zinc-700" />

        <div className="space-y-1">
          {events.map((event, idx) => {
            const eventType = (event.properties.event_type as string) || "unknown";
            const severity = (event.properties.severity as number) || 0;
            const date = (event.properties.occurred_at as string) || "";
            const typeColor = QUAD_CLASS_COLORS[eventType] || "#94a3b8";

            // Find if this event is caused by a previous one
            const incomingCause = causedLinks.find(
              (l) => linkId(l.target) === event.id
            );
            const causeSource = incomingCause
              ? findNode(graphData, linkId(incomingCause.source))
              : null;

            return (
              <div key={event.id} className="relative pl-8">
                {/* Timeline dot */}
                <div
                  className="absolute left-1.5 top-3 w-3 h-3 rounded-full border-2 border-zinc-900"
                  style={{ backgroundColor: typeColor }}
                />

                {/* Causal arrow from previous event */}
                {incomingCause && idx > 0 && (
                  <div className="absolute left-3 -top-1 flex items-center">
                    <div
                      className="w-px h-2"
                      style={{
                        backgroundColor:
                          MECHANISM_COLORS[
                            (incomingCause as GraphLink & { properties?: Record<string, unknown> }).edge_type === "CAUSED"
                              ? "escalation"
                              : "precedent"
                          ] || "#94a3b8",
                      }}
                    />
                  </div>
                )}

                <div className="bg-zinc-900/80 border border-zinc-800/60 rounded-md px-3 py-2.5 space-y-1.5">
                  <div className="flex items-center gap-2 flex-wrap">
                    {date && (
                      <span className="text-[10px] font-mono text-text-secondary/70">{date}</span>
                    )}
                    <span className="text-sm font-medium text-text-primary">{event.name}</span>
                    <span
                      className="text-[10px] font-semibold px-2 py-0.5 rounded-full border capitalize"
                      style={{
                        backgroundColor: `${typeColor}15`,
                        color: typeColor,
                        borderColor: `${typeColor}30`,
                      }}
                    >
                      {eventType}
                    </span>
                  </div>

                  {/* Severity bar */}
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] text-text-secondary">Severity</span>
                    <div className="flex-1 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all"
                        style={{
                          width: `${severity * 100}%`,
                          backgroundColor: severity > 0.7 ? "#ef4444" : severity > 0.4 ? "#eab308" : "#22c55e",
                        }}
                      />
                    </div>
                    <span className="text-[10px] font-mono text-text-secondary">{severity.toFixed(2)}</span>
                  </div>

                  {/* Causal connection indicator */}
                  {causeSource && (
                    <div className="flex items-center gap-1.5 text-[10px]">
                      <span className="text-text-secondary/60">caused by</span>
                      <span className="text-teal-400 font-medium">{causeSource.name}</span>
                      <ArrowRight size={8} className="text-text-secondary/40" />
                      <span className="text-text-primary font-medium">{event.name}</span>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  PANEL 4: Interests & Issues                                        */
/* ------------------------------------------------------------------ */

function InterestsIssuesPanel({ graphData }: { graphData: GraphData }) {
  const interests = nodesByType(graphData, "interest");
  const issues = nodesByType(graphData, "issue");

  // Group interests by holder
  const grouped: Record<string, GraphNode[]> = {};
  for (const interest of interests) {
    const holder = (interest.properties.holder as string) || "Unknown";
    if (!grouped[holder]) grouped[holder] = [];
    grouped[holder].push(interest);
  }

  return (
    <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-5 space-y-4">
      <div className="flex items-center gap-2">
        <Target size={16} className="text-teal-400" />
        <h3 className="text-sm font-semibold text-text-primary uppercase tracking-wider">
          Interests &amp; Issues
        </h3>
      </div>

      {/* Interests grouped by actor */}
      {Object.entries(grouped).map(([holder, holderInterests]) => (
        <div key={holder} className="space-y-2">
          <div className="text-xs font-semibold text-teal-400">{holder}</div>
          {holderInterests.map((interest) => {
            const type = (interest.properties.interest_type as string) || "unknown";
            const priority = (interest.properties.priority as number) || 0;
            const isStated = type === "substantive";
            return (
              <div
                key={interest.id}
                className={`bg-zinc-900/80 border rounded-md px-3 py-2 space-y-1 ${
                  isStated ? "border-zinc-800/60" : "border-zinc-800/40 border-dashed"
                }`}
              >
                <div className="flex items-center gap-2">
                  <span className="text-sm text-text-primary">{interest.name}</span>
                  <span className={`text-[10px] px-1.5 py-0.5 rounded border capitalize ${
                    isStated
                      ? "bg-green-500/10 text-green-400 border-green-500/20"
                      : "bg-amber-500/10 text-amber-400 border-amber-500/20"
                  }`}>
                    {type}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] text-text-secondary">Priority</span>
                  <div className="flex gap-0.5">
                    {Array.from({ length: 5 }, (_, i) => (
                      <div
                        key={i}
                        className={`w-2 h-2 rounded-full ${
                          i < priority ? "bg-teal-400" : "bg-zinc-700"
                        }`}
                      />
                    ))}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      ))}

      {/* Issues */}
      {issues.length > 0 && (
        <div className="space-y-2 pt-2 border-t border-zinc-800">
          <div className="text-[10px] text-text-secondary uppercase tracking-wider font-semibold">Issues</div>
          {issues.map((issue) => {
            const salience = (issue.properties.salience as number) || 0;
            const issueType = (issue.properties.issue_type as string) || "";
            return (
              <div key={issue.id} className="flex items-center gap-3 bg-zinc-900/80 border border-zinc-800/60 rounded-md px-3 py-2">
                <span
                  className="w-2.5 h-2.5 rounded-full shrink-0"
                  style={{ backgroundColor: NODE_COLORS.issue }}
                />
                <div className="flex-1 min-w-0">
                  <div className="text-sm text-text-primary truncate">{issue.name}</div>
                  {issueType && (
                    <div className="text-[10px] text-text-secondary capitalize">{issueType}</div>
                  )}
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <span className="text-[10px] text-text-secondary">Salience</span>
                  <div className="w-14 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-orange-500 rounded-full"
                      style={{ width: `${salience * 100}%` }}
                    />
                  </div>
                  <span className="text-[10px] font-mono text-text-secondary">{salience.toFixed(2)}</span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  PANEL 5: Emotional & Trust State                                   */
/* ------------------------------------------------------------------ */

const PLUTCHIK_COLORS: Record<string, string> = {
  joy: "#22c55e",
  trust: "#06b6d4",
  fear: "#a855f7",
  surprise: "#eab308",
  sadness: "#3b82f6",
  disgust: "#84cc16",
  anger: "#ef4444",
  anticipation: "#f97316",
  shame: "#a855f7",
};

function EmotionalTrustPanel({ graphData }: { graphData: GraphData }) {
  const emotions = nodesByType(graphData, "emotional_state");
  const trustStates = nodesByType(graphData, "trust_state");

  return (
    <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-5 space-y-4">
      <div className="flex items-center gap-2">
        <Heart size={16} className="text-teal-400" />
        <h3 className="text-sm font-semibold text-text-primary uppercase tracking-wider">
          Emotional &amp; Trust State
        </h3>
      </div>

      {/* Emotional States */}
      {emotions.length > 0 && (
        <div className="space-y-2">
          <div className="text-[10px] text-text-secondary uppercase tracking-wider font-semibold">Emotional States</div>
          {emotions.map((emotion) => {
            const holder = (emotion.properties.holder as string) || "";
            const intensity = (emotion.properties.intensity as number) || 0;
            const valence = (emotion.properties.valence as string) || "";
            // Extract emotion name from the node name (e.g. "Alex: Fear" -> "Fear")
            const emotionName = emotion.name.includes(":")
              ? emotion.name.split(":")[1].trim().toLowerCase()
              : emotion.name.toLowerCase();
            const emotionColor = PLUTCHIK_COLORS[emotionName] || "#94a3b8";

            return (
              <div key={emotion.id} className="bg-zinc-900/80 border border-zinc-800/60 rounded-md px-3 py-2 space-y-1.5">
                <div className="flex items-center gap-2">
                  <span className="text-xs text-text-secondary">{holder}</span>
                  <span
                    className="text-[10px] font-semibold px-2 py-0.5 rounded-full border capitalize"
                    style={{
                      backgroundColor: `${emotionColor}15`,
                      color: emotionColor,
                      borderColor: `${emotionColor}30`,
                    }}
                  >
                    {emotionName}
                  </span>
                  <span className={`text-[10px] px-1.5 py-0.5 rounded border ${
                    valence === "negative"
                      ? "bg-red-500/10 text-red-400 border-red-500/20"
                      : valence === "positive"
                        ? "bg-green-500/10 text-green-400 border-green-500/20"
                        : "bg-zinc-800 text-text-secondary border-zinc-700"
                  }`}>
                    {valence}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] text-text-secondary">Intensity</span>
                  <div className="flex-1 h-2 bg-zinc-800 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all"
                      style={{ width: `${intensity * 100}%`, backgroundColor: emotionColor }}
                    />
                  </div>
                  <span className="text-[10px] font-mono text-text-secondary">{intensity.toFixed(2)}</span>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Trust States */}
      {trustStates.length > 0 && (
        <div className="space-y-2 pt-2 border-t border-zinc-800">
          <div className="text-[10px] text-text-secondary uppercase tracking-wider font-semibold">Trust States</div>
          {trustStates.map((trust) => {
            const from = (trust.properties.from as string) || "";
            const to = (trust.properties.to as string) || "";
            const overall = (trust.properties.overall as number) || 0;
            const basis = (trust.properties.basis as string) || "";
            const ability = (trust.properties.ability as number) || undefined;
            const benevolence = (trust.properties.benevolence as number) || undefined;
            const integrity = (trust.properties.integrity as number) || undefined;

            const trustColor =
              overall >= 0.6 ? "#22c55e" : overall >= 0.4 ? "#eab308" : "#ef4444";

            return (
              <div key={trust.id} className="bg-zinc-900/80 border border-zinc-800/60 rounded-md px-3 py-2.5 space-y-2">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-xs text-text-primary font-medium">{from}</span>
                  <ArrowRight size={10} className="text-text-secondary/40" />
                  <span className="text-xs text-text-primary font-medium">{to}</span>
                  {basis && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-violet-500/10 text-violet-400 border border-violet-500/20 capitalize ml-auto">
                      {basis}
                    </span>
                  )}
                </div>

                {/* Overall trust meter */}
                <div className="flex items-center gap-2">
                  <span className="text-[10px] text-text-secondary w-12">Overall</span>
                  <div className="flex-1 h-2.5 bg-zinc-800 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all"
                      style={{ width: `${overall * 100}%`, backgroundColor: trustColor }}
                    />
                  </div>
                  <span className="text-xs font-mono font-bold" style={{ color: trustColor }}>
                    {overall.toFixed(2)}
                  </span>
                </div>

                {/* Sub-dimensions if present */}
                {(ability !== undefined || benevolence !== undefined || integrity !== undefined) && (
                  <div className="space-y-1">
                    {ability !== undefined && (
                      <TrustBar label="Ability" value={ability} />
                    )}
                    {benevolence !== undefined && (
                      <TrustBar label="Benevolence" value={benevolence} />
                    )}
                    {integrity !== undefined && (
                      <TrustBar label="Integrity" value={integrity} />
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {emotions.length === 0 && trustStates.length === 0 && (
        <p className="text-sm text-text-secondary/50">No emotional or trust state data in graph</p>
      )}
    </div>
  );
}

function TrustBar({ label, value }: { label: string; value: number }) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-[10px] text-text-secondary/70 w-16">{label}</span>
      <div className="flex-1 h-1 bg-zinc-800 rounded-full overflow-hidden">
        <div
          className="h-full bg-violet-500/60 rounded-full"
          style={{ width: `${value * 100}%` }}
        />
      </div>
      <span className="text-[10px] font-mono text-text-secondary/70">{value.toFixed(2)}</span>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  PANEL 6: Norms & Compliance                                        */
/* ------------------------------------------------------------------ */

function NormsCompliancePanel({ graphData }: { graphData: GraphData }) {
  const norms = nodesByType(graphData, "norm");
  const violations = linksByType(graphData, "VIOLATES");
  const governedBy = linksByType(graphData, "GOVERNED_BY");

  const NORM_TYPE_COLORS: Record<string, string> = {
    statute: "#3b82f6",
    policy: "#eab308",
    treaty: "#06b6d4",
    contract: "#22c55e",
  };

  return (
    <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-5 space-y-4">
      <div className="flex items-center gap-2">
        <Shield size={16} className="text-teal-400" />
        <h3 className="text-sm font-semibold text-text-primary uppercase tracking-wider">
          Norms &amp; Compliance
        </h3>
        <span className="text-[10px] text-text-secondary/60 ml-auto">{norms.length} norms</span>
      </div>

      {/* Norm list */}
      {norms.map((norm) => {
        const normType = (norm.properties.norm_type as string) || "unknown";
        const binding = norm.properties.binding as boolean;
        const typeColor = NORM_TYPE_COLORS[normType] || "#94a3b8";

        return (
          <div key={norm.id} className="bg-zinc-900/80 border border-zinc-800/60 rounded-md px-3 py-2 space-y-1">
            <div className="flex items-center gap-2">
              <FileText size={12} className="text-text-secondary/60 shrink-0" />
              <span className="text-sm text-text-primary font-medium">{norm.name}</span>
              <span
                className="text-[10px] font-semibold px-2 py-0.5 rounded-full border capitalize"
                style={{
                  backgroundColor: `${typeColor}15`,
                  color: typeColor,
                  borderColor: `${typeColor}30`,
                }}
              >
                {normType}
              </span>
              {binding && (
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-red-500/10 text-red-400 border border-red-500/20">
                  Binding
                </span>
              )}
            </div>
          </div>
        );
      })}

      {/* Violations */}
      {violations.length > 0 && (
        <div className="space-y-2 pt-2 border-t border-zinc-800">
          <div className="text-[10px] text-text-secondary uppercase tracking-wider font-semibold flex items-center gap-1.5">
            <AlertTriangle size={10} className="text-red-400" />
            Violations Detected
          </div>
          {violations.map((link) => {
            const eventNode = findNode(graphData, linkId(link.source));
            const normNode = findNode(graphData, linkId(link.target));
            const severity = link.weight || 0;
            return (
              <div key={link.id} className="bg-red-500/5 border border-red-500/15 rounded-md px-3 py-2 space-y-1.5">
                <div className="flex items-center gap-2 text-xs flex-wrap">
                  <span className="text-text-primary font-medium">{eventNode?.name || "Event"}</span>
                  <span className="text-red-400 font-semibold text-[10px] uppercase">violates</span>
                  <span className="text-text-primary font-medium">{normNode?.name || "Norm"}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] text-text-secondary">Severity</span>
                  <div className="flex-1 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-red-500 rounded-full"
                      style={{ width: `${severity * 100}%` }}
                    />
                  </div>
                  <span className="text-[10px] font-mono text-red-400">{severity.toFixed(2)}</span>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Compliance (governed_by without violations) */}
      {governedBy.length > 0 && (
        <div className="space-y-1.5 pt-2 border-t border-zinc-800">
          <div className="text-[10px] text-text-secondary uppercase tracking-wider font-semibold flex items-center gap-1.5">
            <CheckCircle2 size={10} className="text-green-400" />
            Governance
          </div>
          {governedBy.map((link) => {
            const conflictNode = findNode(graphData, linkId(link.source));
            const normNode = findNode(graphData, linkId(link.target));
            return (
              <div key={link.id} className="flex items-center gap-2 text-xs">
                <span className="text-text-primary">{conflictNode?.name}</span>
                <span className="text-text-secondary/60">governed by</span>
                <span className="text-green-400">{normNode?.name}</span>
              </div>
            );
          })}
        </div>
      )}

      {norms.length === 0 && (
        <p className="text-sm text-text-secondary/50">No norms detected in graph</p>
      )}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  PANEL 7: Narratives & Frames                                       */
/* ------------------------------------------------------------------ */

function NarrativesFramesPanel({ graphData }: { graphData: GraphData }) {
  const narratives = nodesByType(graphData, "narrative");
  const promotesLinks = linksByType(graphData, "PROMOTES");

  const DOMINANCE_COLORS: Record<string, string> = {
    dominant: "#ef4444",
    counter: "#3b82f6",
    alternative: "#eab308",
  };

  return (
    <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-5 space-y-4">
      <div className="flex items-center gap-2">
        <MessageSquare size={16} className="text-teal-400" />
        <h3 className="text-sm font-semibold text-text-primary uppercase tracking-wider">
          Narratives &amp; Frames
        </h3>
        <span className="text-[10px] text-text-secondary/60 ml-auto">{narratives.length} narratives</span>
      </div>

      {narratives.length > 0 ? (
        <div className="space-y-3">
          {narratives.map((narrative) => {
            const holder = (narrative.properties.holder as string) || "";
            const dominance = (narrative.properties.dominance as string) || "";
            const frameType = (narrative.properties.frame_type as string) || "";
            const coherence = (narrative.properties.coherence as number) || undefined;
            const reach = (narrative.properties.reach as number) || undefined;
            const domColor = DOMINANCE_COLORS[dominance] || "#94a3b8";

            // Find who promotes this narrative
            const promoters = promotesLinks
              .filter((l) => linkId(l.target) === narrative.id)
              .map((l) => findNode(graphData, linkId(l.source)))
              .filter(Boolean);

            return (
              <div key={narrative.id} className="bg-zinc-900/80 border border-zinc-800/60 rounded-md px-3 py-3 space-y-2">
                <div className="flex items-start gap-2 flex-wrap">
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-text-primary">{narrative.name}</div>
                    {holder && (
                      <div className="text-[10px] text-text-secondary">Perspective: {holder}</div>
                    )}
                  </div>
                  <div className="flex items-center gap-1.5 shrink-0">
                    <span
                      className="text-[10px] font-semibold px-2 py-0.5 rounded-full border capitalize"
                      style={{
                        backgroundColor: `${domColor}15`,
                        color: domColor,
                        borderColor: `${domColor}30`,
                      }}
                    >
                      {dominance}
                    </span>
                    {frameType && (
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-zinc-800 text-text-secondary border border-zinc-700 capitalize">
                        {frameType}
                      </span>
                    )}
                  </div>
                </div>

                {/* Coherence & Reach bars if present */}
                {coherence !== undefined && (
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] text-text-secondary w-16">Coherence</span>
                    <div className="flex-1 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                      <div className="h-full bg-teal-500 rounded-full" style={{ width: `${coherence * 100}%` }} />
                    </div>
                    <span className="text-[10px] font-mono text-text-secondary">{coherence.toFixed(2)}</span>
                  </div>
                )}
                {reach !== undefined && (
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] text-text-secondary w-16">Reach</span>
                    <div className="flex-1 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                      <div className="h-full bg-blue-500 rounded-full" style={{ width: `${reach * 100}%` }} />
                    </div>
                    <span className="text-[10px] font-mono text-text-secondary">{reach.toFixed(2)}</span>
                  </div>
                )}

                {/* Promoters */}
                {promoters.length > 0 && (
                  <div className="flex items-center gap-1.5 text-[10px] pt-1 border-t border-zinc-800/50">
                    <Eye size={10} className="text-text-secondary/60" />
                    <span className="text-text-secondary/60">Promoted by:</span>
                    {promoters.map((p) => (
                      <span key={p!.id} className="text-teal-400 font-medium">{p!.name}</span>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      ) : (
        <p className="text-sm text-text-secondary/50">No narratives detected in graph</p>
      )}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  PANEL 8: Resolution Path                                           */
/* ------------------------------------------------------------------ */

function ResolutionPathPanel({
  graphData,
  analysis,
}: {
  graphData: GraphData;
  analysis: ComputedAnalysis;
}) {
  const processes = nodesByType(graphData, "process");
  const outcomes = nodesByType(graphData, "outcome");
  const process = processes[0];
  const outcome = outcomes[0];

  return (
    <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-6 space-y-5">
      <div className="flex items-center gap-2">
        <Handshake size={16} className="text-teal-400" />
        <h3 className="text-sm font-semibold text-text-primary uppercase tracking-wider">
          Resolution Path
        </h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Process */}
        {process && (
          <div className="bg-zinc-900/80 border border-zinc-800/60 rounded-md px-4 py-3 space-y-2">
            <div className="flex items-center gap-2">
              <CircleDot size={12} className="text-cyan-400" />
              <span className="text-[10px] text-text-secondary uppercase tracking-wider font-semibold">
                Process
              </span>
            </div>
            <div className="text-sm font-medium text-text-primary">{process.name}</div>
            <div className="space-y-1 text-xs">
              {Boolean(process.properties.process_type) && (
                <div className="flex justify-between">
                  <span className="text-text-secondary">Type</span>
                  <span className="text-text-primary capitalize">
                    {String(process.properties.process_type).replace(/_/g, " ")}
                  </span>
                </div>
              )}
              {Boolean(process.properties.status) && (
                <div className="flex justify-between">
                  <span className="text-text-secondary">Status</span>
                  <span className="text-teal-400 capitalize">{String(process.properties.status)}</span>
                </div>
              )}
              {Boolean(process.properties.approach) && (
                <div className="flex justify-between">
                  <span className="text-text-secondary">Approach</span>
                  <span className="text-text-primary capitalize">
                    {String(process.properties.approach).replace(/_/g, " ")}
                  </span>
                </div>
              )}
              {Boolean(process.properties.stage) && (
                <div className="flex justify-between">
                  <span className="text-text-secondary">Stage</span>
                  <span className="text-text-primary capitalize">
                    {String(process.properties.stage).replace(/_/g, " ")}
                  </span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Outcome */}
        {outcome && (
          <div className="bg-zinc-900/80 border border-zinc-800/60 rounded-md px-4 py-3 space-y-2">
            <div className="flex items-center gap-2">
              <CheckCircle2 size={12} className="text-green-400" />
              <span className="text-[10px] text-text-secondary uppercase tracking-wider font-semibold">
                Outcome
              </span>
            </div>
            <div className="text-sm font-medium text-text-primary">{outcome.name}</div>
            <div className="space-y-1.5 text-xs">
              {Boolean(outcome.properties.outcome_type) && (
                <div className="flex justify-between">
                  <span className="text-text-secondary">Type</span>
                  <span className="text-text-primary capitalize">
                    {String(outcome.properties.outcome_type).replace(/_/g, " ")}
                  </span>
                </div>
              )}
              {outcome.properties.satisfaction_a !== undefined && (
                <div className="space-y-0.5">
                  <div className="flex justify-between">
                    <span className="text-text-secondary">Satisfaction A</span>
                    <span className="font-mono text-text-primary">{(outcome.properties.satisfaction_a as number).toFixed(2)}</span>
                  </div>
                  <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-green-500 rounded-full"
                      style={{ width: `${(outcome.properties.satisfaction_a as number) * 100}%` }}
                    />
                  </div>
                </div>
              )}
              {outcome.properties.satisfaction_b !== undefined && (
                <div className="space-y-0.5">
                  <div className="flex justify-between">
                    <span className="text-text-secondary">Satisfaction B</span>
                    <span className="font-mono text-text-primary">{(outcome.properties.satisfaction_b as number).toFixed(2)}</span>
                  </div>
                  <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-blue-500 rounded-full"
                      style={{ width: `${(outcome.properties.satisfaction_b as number) * 100}%` }}
                    />
                  </div>
                </div>
              )}
              {Boolean(outcome.properties.durability) && (
                <div className="flex justify-between">
                  <span className="text-text-secondary">Durability</span>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 capitalize">
                    {String(outcome.properties.durability)}
                  </span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Theory Frameworks */}
        <div className="bg-zinc-900/80 border border-zinc-800/60 rounded-md px-4 py-3 space-y-2">
          <div className="flex items-center gap-2">
            <Scale size={12} className="text-amber-400" />
            <span className="text-[10px] text-text-secondary uppercase tracking-wider font-semibold">
              Theory Frameworks
            </span>
          </div>
          <div className="space-y-1.5">
            {analysis.theoryFrameworks.map((tf) => (
              <div key={tf.name} className="flex items-center gap-2" title={tf.description}>
                {tf.fired ? (
                  <CheckCircle2 size={11} className="text-green-500 shrink-0" />
                ) : (
                  <div className="w-[11px] h-[11px] rounded-full border border-zinc-700 shrink-0" />
                )}
                <span className={`text-xs ${tf.fired ? "text-text-primary" : "text-text-secondary/40"}`}>
                  {tf.name}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* No process/outcome fallback */}
      {!process && !outcome && (
        <p className="text-sm text-text-secondary/50">No resolution process or outcome detected in graph</p>
      )}
    </div>
  );
}
