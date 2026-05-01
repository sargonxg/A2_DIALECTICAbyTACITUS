import { buildDynamicOntologyPlan, type DynamicOntologyPlan } from "@/lib/dynamicOntology";

export type GraphOpsPrimitive = {
  id: string;
  primitive_type: string;
  workspace_id: string;
  case_id: string;
  episode_id?: string;
  ontology_version: string;
  source_id: string;
  extraction_run_id: string;
  evidence_span_id?: string;
  provenance_span?: string;
  confidence: number;
  valid_from?: string | null;
  valid_to?: string | null;
  observed_at: string;
  [key: string]: unknown;
};

export type GraphOpsExtractionResult = {
  workspaceId: string;
  caseId: string;
  objective: string;
  ontologyProfile: string;
  extractionRunId: string;
  graphWrite: {
    requested: boolean;
    enabled: boolean;
    written: number;
    relationships?: number;
    ruleSignalsWritten?: number;
    plan?: Record<string, unknown>;
    warnings?: string[];
    message: string;
  };
  databricks?: Record<string, unknown>;
  localPersistence?: Record<string, unknown>;
  ruleEvaluation?: Record<string, unknown>;
  dynamicOntology: DynamicOntologyPlan;
  preExtraction: {
    originalChars: number;
    cleanedChars: number;
    removedSections: string[];
    segmentCount: number;
    segmentationMode: string;
    segments: Array<{
      id: string;
      label: string;
      start: number;
      end: number;
      charCount: number;
      reason: string;
    }>;
  };
  counts: Record<string, number>;
  quality: {
    status: "ready" | "review" | "blocked";
    score: number;
    evidenceCoverage: number;
    actorCount: number;
    issueCount: number;
    recommendations: string[];
  };
  primitives: GraphOpsPrimitive[];
  graphPreview: {
    nodes: Array<{ id: string; label: string; name: string; node_type: string; confidence: number }>;
    links: Array<{ id: string; source: string; target: string; edge_type: string; confidence: number }>;
  };
  nextQuestions: string[];
};

const ACTOR_PATTERN =
  /\b(?:Alex|Sam|Romeo|Juliet|Capulet|Montague|Tybalt|Mercutio|Nurse|Friar Laurence|Prince|State A|State B|Mayor|Agency|Finance Office|Mediator|Union|Ministry)\b/g;
const CAPITALIZED_ACTOR_PATTERN =
  /\b[A-Z][a-z]+(?:\s+(?:[A-Z][a-z]+|[A-Z]{2,}|&|and)){0,3}\b/g;
const COMMITMENT_PATTERN =
  /\b(agree[ds]?|commit(?:ted)?|promise[ds]?|pledge[ds]?|will|shall|lock it in|vow)\b/i;
const CONSTRAINT_PATTERN =
  /\b(cannot|must|only after|deadline|expires|requires|penalt(?:y|ies)|red line|banished|law|rule|limited)\b/i;
const EVENT_PATTERN =
  /\b(after|then|announced|suspended|postponed|delayed|failed|meeting|fight|death|banished|married|killed|warned)\b/i;
const NARRATIVE_PATTERN =
  /\b(says|claims|argues|warns|citing|you never|this is about|just want|honor|love|hate|feud)\b/i;
const TRUST_PATTERN = /\b(trust|distrust|confidence|safety|betray|secret|guarantee)\b/i;
const LEVERAGE_PATTERN = /\b(power|leverage|capacity|funds|authority|control|banished|penalty)\b/i;

const SAMPLE_TEXTS: Record<string, string> = {
  "romeo-juliet-conflict":
    "Romeo is a Montague and Juliet is a Capulet. Their families are opposed in a public feud. " +
    "After Tybalt kills Mercutio, Romeo kills Tybalt and the Prince banishes Romeo from Verona. " +
    "Juliet secretly commits to Romeo through marriage, while her family pressures her toward another match. " +
    "Friar Laurence proposes a risky plan because the family conflict constrains the lovers and intensifies distrust.",
  "mediation-commitments":
    "Sam says Alex will own the Q4 launch deck content, while Sam handles design. " +
    "Alex agrees and says he will pick it up after the Jenkins pitch. " +
    "Later Alex says he never promised ownership and only agreed to help. " +
    "The team cannot publish after Friday because retail partners impose penalties for late materials.",
  "policy-constraint-map":
    "The Housing Agency says River City must publish new eligibility rules before the July deadline. " +
    "The Finance Office warns that federal grant funds cannot be released until the council approves the implementation plan. " +
    "Tenant advocates claim the proposed rule excludes informal workers, while the Mayor argues the city needs a phased rollout. " +
    "Legal counsel says emergency waivers require public notice and cannot override the state affordability statute.",
  "field-intelligence-brief":
    "Local monitors report that the North Market checkpoint reopened after a meeting between the District Council and the Traders Union. " +
    "The Police Command says the closure was temporary, but shopkeepers claim it was used to pressure vendors into paying new fees. " +
    "A mediator warned that trust remains low because previous access commitments were not honored. " +
    "Observers could verify the reopening but could not confirm who ordered the checkpoint closure.",
};

const ACTOR_STOPWORDS = new Set([
  "After",
  "Later",
  "The",
  "Their",
  "This",
  "That",
  "Before",
  "Observers",
  "Legal",
  "Local",
]);

function id(prefix: string): string {
  return `${prefix}_${crypto.randomUUID().replace(/-/g, "").slice(0, 16)}`;
}

function sentences(text: string): Array<{ text: string; start: number; end: number }> {
  const matches = [...text.matchAll(/[^.!?\n]+[.!?\n]?/g)];
  return matches
    .map((match) => ({
      text: String(match[0] ?? "").trim(),
      start: match.index ?? 0,
      end: (match.index ?? 0) + String(match[0] ?? "").length,
    }))
    .filter((item) => item.text.length > 0);
}

function cleanSourceText(text: string) {
  let cleaned = text.replace(/\r\n/g, "\n");
  const removedSections: string[] = [];
  const startMarker = cleaned.search(/\*\*\*\s*START OF (?:THE|THIS) PROJECT GUTENBERG EBOOK[^\n]*\*\*\*/i);
  if (startMarker >= 0) {
    const afterMarker = cleaned.indexOf("\n", startMarker);
    cleaned = cleaned.slice(Math.max(afterMarker, startMarker));
    removedSections.push("project_gutenberg_header");
  }
  const endMarker = cleaned.search(/\*\*\*\s*END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK[^\n]*\*\*\*/i);
  if (endMarker >= 0) {
    cleaned = cleaned.slice(0, endMarker);
    removedSections.push("project_gutenberg_license_footer");
  }
  cleaned = cleaned
    .replace(/^(?:Produced by|Transcribed from|This eBook is for the use of).*$/gim, "")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
  return { cleanedText: cleaned || text.trim(), removedSections };
}

function headingMatches(text: string) {
  return [...text.matchAll(/^(ACT\s+[IVXLC]+|SCENE\s+[IVXLC]+|CHAPTER\s+\d+|CHAPTER\s+[IVXLC]+|BOOK\s+[A-ZIVXLC]+)\b[^\n]*/gim)];
}

function segmentSource(text: string, mode: string) {
  const headings = headingMatches(text);
  if (headings.length > 0) {
    return headings.slice(0, 12).map((match, index) => {
      const start = match.index ?? 0;
      const next = headings[index + 1]?.index ?? text.length;
      const label = String(match[0]).trim().slice(0, 80);
      return {
        label,
        text: text.slice(start, next).trim(),
        start,
        end: next,
        reason: "explicit_heading",
      };
    });
  }

  const sentenceItems = sentences(text);
  const targetSize = mode.includes("book") ? 5 : 3;
  const segments: Array<{ label: string; text: string; start: number; end: number; reason: string }> = [];
  for (let index = 0; index < sentenceItems.length; index += targetSize) {
    const group = sentenceItems.slice(index, index + targetSize);
    if (group.length === 0) continue;
    segments.push({
      label: `Episode ${segments.length + 1}`,
      text: group.map((item) => item.text).join(" "),
      start: group[0].start,
      end: group[group.length - 1].end,
      reason: mode.includes("book") ? "narrative_turn" : "event_window",
    });
  }
  if (segments.length === 0 && text.trim()) {
    segments.push({
      label: "Episode 1",
      text: text.trim(),
      start: 0,
      end: text.length,
      reason: "single_segment",
    });
  }
  return segments.slice(0, 12);
}

function pushPrimitive(
  primitives: GraphOpsPrimitive[],
  primitive: Omit<GraphOpsPrimitive, "ontology_version" | "observed_at">,
) {
  const complete = {
    ...primitive,
    ontology_version: "tacitus_core_v1",
    observed_at: new Date().toISOString(),
  } as GraphOpsPrimitive;
  primitives.push(complete);
}

export function sampleText(sampleKey: string | null): string | null {
  if (!sampleKey) return null;
  return SAMPLE_TEXTS[sampleKey] ?? null;
}

function extractActors(sentence: string): string[] {
  const fixed = [...sentence.matchAll(ACTOR_PATTERN)].map((match) => match[0]);
  const inferred = [...sentence.matchAll(CAPITALIZED_ACTOR_PATTERN)]
    .map((match) => match[0].trim())
    .filter((value) => value.length > 2 && !ACTOR_STOPWORDS.has(value.split(/\s+/)[0]));
  return [...new Set([...fixed, ...inferred])].slice(0, 8);
}

function buildQuality(primitives: GraphOpsPrimitive[], counts: Record<string, number>) {
  const evidenceLinked = primitives.filter((item) => item.evidence_span_id).length;
  const sourceBacked = primitives.filter((item) =>
    ["ExtractionRun", "SourceDocument", "SourceChunk", "EvidenceSpan"].includes(item.primitive_type),
  ).length;
  const assessable = Math.max(primitives.length - sourceBacked, 1);
  const evidenceCoverage = Math.round((evidenceLinked / assessable) * 100) / 100;
  const actorCount = counts.Actor ?? 0;
  const issueCount =
    (counts.Claim ?? 0) +
    (counts.Constraint ?? 0) +
    (counts.Commitment ?? 0) +
    (counts.Event ?? 0) +
    (counts.Narrative ?? 0);

  const recommendations: string[] = [];
  if (actorCount < 2) recommendations.push("Add more source text naming at least two actors or institutions.");
  if ((counts.Event ?? 0) === 0) recommendations.push("Add chronology or incident text so the timeline can be built.");
  if ((counts.Constraint ?? 0) === 0) recommendations.push("Add rules, deadlines, limits, red lines, or process constraints.");
  if (evidenceCoverage < 0.8) recommendations.push("Review primitives without evidence spans before final answers.");

  const score = Math.min(
    100,
    Math.round(
      (Math.min(actorCount, 4) / 4) * 30 +
        (Math.min(issueCount, 10) / 10) * 35 +
        Math.min(evidenceCoverage, 1) * 35,
    ),
  );

  return {
    status: score >= 70 && recommendations.length <= 1 ? "ready" : score >= 40 ? "review" : "blocked",
    score,
    evidenceCoverage,
    actorCount,
    issueCount,
    recommendations:
      recommendations.length > 0
        ? recommendations
        : ["Enough structure for a first graph-grounded question pass."],
  } as const;
}

export function extractGraphOpsPrimitives(input: {
  text: string;
  workspaceId: string;
  caseId: string;
  objective: string;
  ontologyProfile: string;
  sourceTitle: string;
  sourceType: string;
}): GraphOpsExtractionResult {
  const dynamicOntology = buildDynamicOntologyPlan({
    profileId: input.ontologyProfile,
    objective: input.objective,
    sourceType: input.sourceType,
  });
  const cleaned = cleanSourceText(input.text);
  const preparedSegments = segmentSource(cleaned.cleanedText, dynamicOntology.episodeStrategy.mode);
  const extractionRunId = id("run");
  const sourceId = id("source");
  const documentId = id("doc");
  const primitives: GraphOpsPrimitive[] = [];
  const actorIds = new Map<string, string>();
  const segmentRecords = preparedSegments.map((segment, index) => ({
    ...segment,
    id: id("segment"),
    chunkId: id("chunk"),
    episodeId: id("episode"),
    index,
  }));

  const base = {
    workspace_id: input.workspaceId,
    case_id: input.caseId,
    source_id: sourceId,
    extraction_run_id: extractionRunId,
  };

  pushPrimitive(primitives, {
    id: extractionRunId,
    primitive_type: "ExtractionRun",
    ...base,
    confidence: 1,
    model_name: "graphops-local-deterministic-extractor",
    extraction_method: "rule_based_frontend_api",
    extraction_passes: dynamicOntology.extractionPasses.map((item) => item.id),
    objective: input.objective,
    ontology_profile: input.ontologyProfile,
  });
  pushPrimitive(primitives, {
    id: documentId,
    primitive_type: "SourceDocument",
    ...base,
    confidence: 1,
    title: input.sourceTitle,
    source_type: input.sourceType,
    original_char_count: input.text.length,
    cleaned_char_count: cleaned.cleanedText.length,
    removed_sections: cleaned.removedSections,
  });
  pushPrimitive(primitives, {
    id: id("preplan"),
    primitive_type: "PreExtractionPlan",
    ...base,
    confidence: 1,
    document_id: documentId,
    segmentation_mode: dynamicOntology.episodeStrategy.mode,
    removed_sections: cleaned.removedSections,
    required_nodes: dynamicOntology.requiredNodes,
    required_edges: dynamicOntology.requiredEdges,
    custom_mappings: dynamicOntology.customMappings,
  });

  for (const segment of segmentRecords) {
    pushPrimitive(primitives, {
      id: segment.chunkId,
      primitive_type: "SourceChunk",
      ...base,
      confidence: 1,
      document_id: documentId,
      segment_id: segment.id,
      chunk_index: segment.index,
      text: segment.text.slice(0, 12000),
      start_char: segment.start,
      end_char: segment.end,
      segmentation_reason: segment.reason,
    });
    pushPrimitive(primitives, {
      id: segment.episodeId,
      primitive_type: "Episode",
      ...base,
      confidence: 0.86,
      source_segment_id: segment.id,
      chunk_id: segment.chunkId,
      name: segment.label,
      objective: input.objective,
      segmentation_reason: segment.reason,
    });

    for (const sentence of sentences(segment.text)) {
      const evidenceId = id("span");
      const absoluteStart = segment.start + sentence.start;
      const absoluteEnd = segment.start + sentence.end;
      pushPrimitive(primitives, {
        id: evidenceId,
        primitive_type: "EvidenceSpan",
        ...base,
        episode_id: segment.episodeId,
        confidence: 0.72,
        chunk_id: segment.chunkId,
        provenance_span: sentence.text,
        start_char: absoluteStart,
        end_char: absoluteEnd,
      });

      const actors = extractActors(sentence.text);
      for (const actor of actors) {
        if (!actorIds.has(actor)) {
          const actorId = id("actor");
          actorIds.set(actor, actorId);
          pushPrimitive(primitives, {
            id: actorId,
            primitive_type: "Actor",
            ...base,
            confidence: 0.76,
            evidence_span_id: evidenceId,
            provenance_span: sentence.text,
            name: actor,
            actor_type: /Agency|Office|Union|Ministry|Council|Command|Capulet|Montague/.test(actor)
              ? "organization_or_group"
              : "person_or_collective",
          });
        }
      }

      const primaryActorId = actors.length > 0 ? actorIds.get(actors[0]) : undefined;
      pushPrimitive(primitives, {
        id: id("claim"),
        primitive_type: "Claim",
        ...base,
        episode_id: segment.episodeId,
        confidence: 0.64,
        evidence_span_id: evidenceId,
        provenance_span: sentence.text,
        text: sentence.text,
        assertion_type: "explicit",
        claim_status: "extracted",
        subject_actor_id: primaryActorId,
      });

      if (primaryActorId && COMMITMENT_PATTERN.test(sentence.text)) {
        pushPrimitive(primitives, {
          id: id("commitment"),
          primitive_type: "Commitment",
          ...base,
          episode_id: segment.episodeId,
          confidence: 0.7,
          evidence_span_id: evidenceId,
          provenance_span: sentence.text,
          actor_id: primaryActorId,
          description: sentence.text,
          commitment_status: "candidate",
          constrains_actor_id: primaryActorId,
        });
      }
      if (CONSTRAINT_PATTERN.test(sentence.text)) {
        pushPrimitive(primitives, {
          id: id("constraint"),
          primitive_type: "Constraint",
          ...base,
          episode_id: segment.episodeId,
          confidence: 0.72,
          evidence_span_id: evidenceId,
          provenance_span: sentence.text,
          actor_id: primaryActorId,
          description: sentence.text,
          constraint_type: "temporal_or_normative",
        });
      }
      if (EVENT_PATTERN.test(sentence.text)) {
        pushPrimitive(primitives, {
          id: id("event"),
          primitive_type: "Event",
          ...base,
          episode_id: segment.episodeId,
          confidence: 0.68,
          evidence_span_id: evidenceId,
          provenance_span: sentence.text,
          description: sentence.text,
          event_type: "reported_change",
        });
      }
      if (NARRATIVE_PATTERN.test(sentence.text)) {
        pushPrimitive(primitives, {
          id: id("narrative"),
          primitive_type: "Narrative",
          ...base,
          episode_id: segment.episodeId,
          confidence: 0.66,
          evidence_span_id: evidenceId,
          provenance_span: sentence.text,
          actor_id: primaryActorId,
          content: sentence.text,
          narrative_type: "reported_frame",
        });
      }
      if (primaryActorId && (TRUST_PATTERN.test(sentence.text) || LEVERAGE_PATTERN.test(sentence.text))) {
        pushPrimitive(primitives, {
          id: id("actor_state"),
          primitive_type: "ActorState",
          ...base,
          episode_id: segment.episodeId,
          confidence: 0.62,
          evidence_span_id: evidenceId,
          provenance_span: sentence.text,
          actor_id: primaryActorId,
          trust_level: TRUST_PATTERN.test(sentence.text) ? "mentioned" : null,
          leverage_level: LEVERAGE_PATTERN.test(sentence.text) ? "mentioned" : null,
          source_ids: [sourceId],
        });
      }
    }
  }

  const counts = primitives.reduce<Record<string, number>>((acc, primitive) => {
    acc[primitive.primitive_type] = (acc[primitive.primitive_type] ?? 0) + 1;
    return acc;
  }, {});

  const nodes = primitives
    .filter((item) => !["SourceChunk", "ExtractionRun"].includes(item.primitive_type))
    .slice(0, 80)
    .map((item) => ({
      id: item.id,
      label: item.primitive_type,
      node_type: item.primitive_type.toLowerCase(),
      name: String(item.name ?? item.title ?? item.description ?? item.text ?? item.primitive_type).slice(0, 80),
      confidence: item.confidence,
    }));

  const evidenceLinks = primitives
    .filter((item) => item.evidence_span_id)
    .slice(0, 80)
    .map((item) => ({
      id: id("edge"),
      source: item.id,
      target: String(item.evidence_span_id),
      edge_type: "EVIDENCED_BY",
      confidence: item.confidence,
    }));
  const structuralLinks = primitives
    .flatMap((item) => {
      const links: Array<{ id: string; source: string; target: string; edge_type: string; confidence: number }> = [];
      for (const [key, edgeType] of [
        ["document_id", "FROM_DOCUMENT"],
        ["chunk_id", "FROM_CHUNK"],
        ["episode_id", "IN_EPISODE"],
        ["actor_id", "ABOUT_ACTOR"],
        ["subject_actor_id", "ABOUT_ACTOR"],
        ["constrains_actor_id", "CONSTRAINS"],
      ] as const) {
        const target = item[key];
        if (typeof target === "string" && target && target !== item.id) {
          links.push({
            id: id("edge"),
            source: item.id,
            target,
            edge_type: edgeType,
            confidence: item.confidence,
          });
        }
      }
      return links;
    })
    .slice(0, 120);
  const quality = buildQuality(primitives, counts);

  return {
    workspaceId: input.workspaceId,
    caseId: input.caseId,
    objective: input.objective,
    ontologyProfile: input.ontologyProfile,
    extractionRunId,
    dynamicOntology,
    preExtraction: {
      originalChars: input.text.length,
      cleanedChars: cleaned.cleanedText.length,
      removedSections: cleaned.removedSections,
      segmentCount: segmentRecords.length,
      segmentationMode: dynamicOntology.episodeStrategy.mode,
      segments: segmentRecords.map((segment) => ({
        id: segment.id,
        label: segment.label,
        start: segment.start,
        end: segment.end,
        charCount: segment.text.length,
        reason: segment.reason,
      })),
    },
    graphWrite: {
      requested: false,
      enabled: false,
      written: 0,
      message: "Preview only.",
    },
    counts,
    quality,
    primitives,
    graphPreview: { nodes, links: [...evidenceLinks, ...structuralLinks].slice(0, 160) },
    nextQuestions: [
      "Which commitments constrain each actor?",
      "Which claims are explicit versus inferred?",
      "What changed across episodes?",
      "Which constraints create leverage or block de-escalation?",
      "Which source spans should an analyst verify first?",
    ],
  };
}
