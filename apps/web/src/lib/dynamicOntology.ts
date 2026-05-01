import { ontologyProfileOptions } from "@/data/graphops";

const CORE_TYPES = [
  "Actor",
  "Claim",
  "Interest",
  "Constraint",
  "Leverage",
  "Commitment",
  "Event",
  "Narrative",
  "Episode",
  "ActorState",
  "SourceDocument",
  "SourceChunk",
  "EvidenceSpan",
  "ExtractionRun",
] as const;

export type CorePrimitive = (typeof CORE_TYPES)[number];

export type DynamicOntologyPlan = {
  id: string;
  label: string;
  objective: string;
  requiredNodes: string[];
  requiredEdges: string[];
  customMappings: Array<{
    custom_type: string;
    core_mapping: CorePrimitive;
    purpose: string;
    extraction_hint: string;
  }>;
  extractionPasses: Array<{
    id: string;
    name: string;
    target_primitives: CorePrimitive[];
    instruction: string;
  }>;
  episodeStrategy: {
    mode: string;
    heading_patterns: string[];
    fallback: string;
  };
  validationRules: string[];
  questions: string[];
};

function safeId(value: string) {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "").slice(0, 96);
}

export function coreMappingsForProfile(profileId: string): DynamicOntologyPlan["customMappings"] {
  if (profileId === "literary-conflict") {
    return [
      {
        custom_type: "Character",
        core_mapping: "Actor",
        purpose: "Book-specific person or group participating in the conflict.",
        extraction_hint: "Cluster names, titles, family names, and repeated character mentions.",
      },
      {
        custom_type: "Scene",
        core_mapping: "Episode",
        purpose: "Bounded narrative unit with its own conflict state.",
        extraction_hint: "Prefer ACT/SCENE/CHAPTER headings; otherwise use turning-point paragraphs.",
      },
      {
        custom_type: "FeudFrame",
        core_mapping: "Narrative",
        purpose: "Identity, loyalty, honor, betrayal, love, or legitimacy frame.",
        extraction_hint: "Extract the frame separately from concrete events.",
      },
      {
        custom_type: "BanishmentOrRule",
        core_mapping: "Constraint",
        purpose: "Authority-imposed limit that changes available options.",
        extraction_hint: "Capture who is constrained and the source span.",
      },
      {
        custom_type: "VowOrPromise",
        core_mapping: "Commitment",
        purpose: "Promise, oath, secret bond, agreement, or implied undertaking.",
        extraction_hint: "Preserve ambiguity and actor links.",
      },
    ];
  }
  if (profileId === "policy-analysis") {
    return [
      {
        custom_type: "Institution",
        core_mapping: "Actor",
        purpose: "Agency, office, council, court, or stakeholder group.",
        extraction_hint: "Detect formal organizations and role-bearing public bodies.",
      },
      {
        custom_type: "StatutoryRule",
        core_mapping: "Constraint",
        purpose: "Legal, procedural, temporal, or budgetary limit on options.",
        extraction_hint: "Capture must/cannot/requires/deadline language.",
      },
      {
        custom_type: "VetoPoint",
        core_mapping: "Leverage",
        purpose: "Actor capacity to block, delay, fund, approve, or enforce.",
        extraction_hint: "Link leverage to the actor and affected process.",
      },
      {
        custom_type: "ImplementationRisk",
        core_mapping: "Claim",
        purpose: "Stated risk or uncertainty about policy execution.",
        extraction_hint: "Mark as candidate unless direct evidence supports it.",
      },
      {
        custom_type: "PolicyOption",
        core_mapping: "Narrative",
        purpose: "Framed option, proposal, or public justification.",
        extraction_hint: "Separate option framing from governing constraints.",
      },
    ];
  }
  if (profileId === "mediation-resolution") {
    return [
      {
        custom_type: "Party",
        core_mapping: "Actor",
        purpose: "Direct or indirect participant in the dispute.",
        extraction_hint: "Extract both parties and process actors such as mediator or HR.",
      },
      {
        custom_type: "RedLine",
        core_mapping: "Constraint",
        purpose: "Non-negotiable limit or condition.",
        extraction_hint: "Do not rewrite red lines as interests.",
      },
      {
        custom_type: "RepairOffer",
        core_mapping: "Commitment",
        purpose: "Promised action intended to repair trust or process viability.",
        extraction_hint: "Track actor, scope, and review timing.",
      },
      {
        custom_type: "UnderlyingNeed",
        core_mapping: "Interest",
        purpose: "Need or concern behind a stated position.",
        extraction_hint: "Mark inferred needs separately from explicit statements.",
      },
      {
        custom_type: "TrustRepair",
        core_mapping: "ActorState",
        purpose: "Trust, distrust, safety, or confidence state that shapes process choice.",
        extraction_hint: "Link to evidence and affected actor.",
      },
    ];
  }
  return [
    {
      custom_type: "Participant",
      core_mapping: "Actor",
      purpose: "Person, group, institution, or role-bearing source participant.",
      extraction_hint: "Prefer explicit source mentions.",
    },
    {
      custom_type: "Assertion",
      core_mapping: "Claim",
      purpose: "Source-backed statement that may be true, contested, inferred, or uncertain.",
      extraction_hint: "Keep direct observations separate from claims about causes.",
    },
    {
      custom_type: "FrictionPoint",
      core_mapping: "Constraint",
      purpose: "Limit, blocker, rule, deadline, or conflict pressure.",
      extraction_hint: "Preserve the original span and affected actor when known.",
    },
    {
      custom_type: "PromisedAction",
      core_mapping: "Commitment",
      purpose: "Promise, agreement, plan, undertaking, or obligation.",
      extraction_hint: "Capture scope and later denials as separate claims.",
    },
    {
      custom_type: "StateChange",
      core_mapping: "ActorState",
      purpose: "Trust, leverage, emotion, risk, or readiness state.",
      extraction_hint: "Use only if evidence mentions the state or a strong proxy.",
    },
  ];
}

export function buildDynamicOntologyPlan(input: {
  profileId: string;
  objective: string;
  sourceType?: string;
  templateId?: string;
}): DynamicOntologyPlan {
  const profile =
    ontologyProfileOptions.find((item) => item.id === input.profileId) ?? ontologyProfileOptions[0];
  const isBook = profile.id === "literary-conflict" || input.sourceType?.includes("book");
  return {
    id: `ontology_${safeId(profile.id)}_${safeId(input.objective).slice(0, 24)}`,
    label: profile.label,
    objective: input.objective || profile.objective,
    requiredNodes: profile.requiredNodes,
    requiredEdges: profile.requiredEdges,
    customMappings: coreMappingsForProfile(profile.id),
    extractionPasses: [
      {
        id: "source-cleaning",
        name: "Source Cleaning",
        target_primitives: ["SourceDocument", "SourceChunk", "EvidenceSpan"],
        instruction: isBook
          ? "Remove publisher/license boilerplate, table-of-contents noise, and non-story metadata before extraction."
          : "Preserve source metadata and remove duplicate whitespace or upload noise.",
      },
      {
        id: "episode-prestructure",
        name: "Episode Pre-Structure",
        target_primitives: ["Episode", "Event", "ActorState"],
        instruction: isBook
          ? "Segment by act, scene, chapter, or turning point before extracting character-level conflict facts."
          : "Segment by meeting, incident, date, process step, or source section.",
      },
      {
        id: "primitive-extraction",
        name: "Ontology Primitive Extraction",
        target_primitives: ["Actor", "Claim", "Constraint", "Commitment", "Event", "Narrative"],
        instruction: "Extract only mapped TACITUS primitives and preserve source span IDs for every claim-like item.",
      },
      {
        id: "rule-and-review",
        name: "Rule And Review",
        target_primitives: ["EvidenceSpan", "Claim", "ActorState"],
        instruction: "Apply rule signals for causality, coverage, confidence, commitment scope, and intervention readiness.",
      },
    ],
    episodeStrategy: {
      mode: isBook ? "book_act_scene_chapter_or_turning_point" : "source_section_or_incident",
      heading_patterns: isBook
        ? ["ACT [IVX]+", "SCENE [IVX]+", "CHAPTER \\d+", "Book \\w+"]
        : ["Meeting", "Incident", "Phase", "Section", "Date"],
      fallback: isBook
        ? "Group paragraphs into narrative turns when no heading exists."
        : "Group sentences into small event windows when no explicit section exists.",
    },
    validationRules: [
      "Every custom type must map to one TACITUS core primitive.",
      "Every Claim, Commitment, Constraint, Event, Narrative, and ActorState must carry an EvidenceSpan link.",
      "Chronology and causality must remain separate unless the span contains causal evidence.",
      "Low-confidence claims must remain candidate facts until reviewed or corroborated.",
      "Profile-required nodes and edges must be visible in readiness scoring.",
    ],
    questions: profile.questions,
  };
}
