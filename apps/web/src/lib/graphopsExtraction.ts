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
    message: string;
  };
  counts: Record<string, number>;
  primitives: GraphOpsPrimitive[];
  graphPreview: {
    nodes: Array<{ id: string; label: string; name: string; node_type: string; confidence: number }>;
    links: Array<{ id: string; source: string; target: string; edge_type: string; confidence: number }>;
  };
  nextQuestions: string[];
};

const ACTOR_PATTERN =
  /\b(?:Alex|Sam|Romeo|Juliet|Capulet|Montague|Tybalt|Mercutio|Nurse|Friar Laurence|Prince|State A|State B|Mayor|Agency|Finance Office|Mediator|Union|Ministry)\b/g;
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
};

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

export function extractGraphOpsPrimitives(input: {
  text: string;
  workspaceId: string;
  caseId: string;
  objective: string;
  ontologyProfile: string;
  sourceTitle: string;
  sourceType: string;
}): GraphOpsExtractionResult {
  const extractionRunId = id("run");
  const sourceId = id("source");
  const documentId = id("doc");
  const chunkId = id("chunk");
  const episodeId = id("episode");
  const primitives: GraphOpsPrimitive[] = [];
  const actorIds = new Map<string, string>();

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
  });
  pushPrimitive(primitives, {
    id: chunkId,
    primitive_type: "SourceChunk",
    ...base,
    confidence: 1,
    document_id: documentId,
    chunk_index: 0,
    text: input.text.slice(0, 12000),
    start_char: 0,
    end_char: input.text.length,
  });
  pushPrimitive(primitives, {
    id: episodeId,
    primitive_type: "Episode",
    ...base,
    confidence: 1,
    name: `${input.caseId} initial episode`,
    objective: input.objective,
  });

  for (const sentence of sentences(input.text)) {
    const evidenceId = id("span");
    pushPrimitive(primitives, {
      id: evidenceId,
      primitive_type: "EvidenceSpan",
      ...base,
      confidence: 0.72,
      chunk_id: chunkId,
      provenance_span: sentence.text,
      start_char: sentence.start,
      end_char: sentence.end,
    });

    const actors = [...new Set([...sentence.text.matchAll(ACTOR_PATTERN)].map((m) => m[0]))];
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
          actor_type: /Agency|Office|Union|Ministry|Capulet|Montague/.test(actor)
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
      episode_id: episodeId,
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
        episode_id: episodeId,
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
        episode_id: episodeId,
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
        episode_id: episodeId,
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
        episode_id: episodeId,
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
        episode_id: episodeId,
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

  return {
    workspaceId: input.workspaceId,
    caseId: input.caseId,
    objective: input.objective,
    ontologyProfile: input.ontologyProfile,
    extractionRunId,
    graphWrite: {
      requested: false,
      enabled: false,
      written: 0,
      message: "Preview only.",
    },
    counts,
    primitives,
    graphPreview: { nodes, links: evidenceLinks },
    nextQuestions: [
      "Which commitments constrain each actor?",
      "Which claims are explicit versus inferred?",
      "What changed across episodes?",
      "Which constraints create leverage or block de-escalation?",
      "Which source spans should an analyst verify first?",
    ],
  };
}
