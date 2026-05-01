import {
  aiCommandExamples,
  benchmarkBlockCatalog,
  dynamicOntologyEngine,
  graphLayerBlueprints,
  neurosymbolicRuleCatalog,
  pipelineBlockCatalog,
  pipelineConfigurationExamples,
  workspaceProjectTemplates,
} from "@/data/graphops";

function scoreText(command: string, values: string[]) {
  const lower = command.toLowerCase();
  return values.reduce((score, value) => score + (lower.includes(value.toLowerCase()) ? 1 : 0), 0);
}

function selectTemplate(command: string) {
  const scores = workspaceProjectTemplates.map((template) => ({
    template,
    score:
      scoreText(command, [template.name, template.description, template.sourceExamples]) +
      (command.toLowerCase().includes("union") || command.toLowerCase().includes("labor") ? (template.id === "labor-union-mediation" ? 5 : 0) : 0) +
      (command.toLowerCase().includes("border") || command.toLowerCase().includes("territorial") ? (template.id === "regional-border-process" ? 5 : 0) : 0) +
      (command.toLowerCase().includes("romeo") || command.toLowerCase().includes("book") ? (template.id === "book-conflict-lab" ? 5 : 0) : 0) +
      (command.toLowerCase().includes("expert") || command.toLowerCase().includes("method") ? (template.id === "expert-method-graph" ? 5 : 0) : 0),
  }));
  return scores.sort((a, b) => b.score - a.score)[0]?.template ?? workspaceProjectTemplates[0];
}

function selectRules(command: string) {
  const lower = command.toLowerCase();
  return neurosymbolicRuleCatalog.filter((rule) => {
    const text = `${rule.name} ${rule.category} ${rule.trigger} ${rule.benchmark}`.toLowerCase();
    return (
      text.split(/\W+/).some((word) => word.length > 5 && lower.includes(word)) ||
      (lower.includes("mediation") && ["Mediation", "Commitment", "Power"].includes(rule.category)) ||
      (lower.includes("policy") && ["Policy", "Provenance", "Temporal"].includes(rule.category)) ||
      (lower.includes("border") && ["Policy", "Narrative", "Temporal"].includes(rule.category)) ||
      (lower.includes("book") && ["Narrative", "Temporal", "Ontology"].includes(rule.category))
    );
  }).slice(0, 5);
}

async function geminiSuggestion(command: string) {
  const key = process.env.GEMINI_API_KEY || process.env.GOOGLE_AI_API_KEY;
  if (!key) return null;

  const prompt = [
    "You are Aletheia, the TACITUS Dynamic Ontology Engine.",
    "Return concise JSON only with keys: rationale, ontology_extensions, episode_plan, benchmark_plan, risks.",
    "Every ontology extension must map to one of: Actor, Claim, Interest, Constraint, Leverage, Commitment, Event, Narrative, Source, Episode, ActorState, ExtractionRun, EvidenceSpan.",
    `User command: ${command}`,
  ].join("\n");
  const response = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${key}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contents: [{ role: "user", parts: [{ text: prompt }] }],
        generationConfig: { responseMimeType: "application/json" },
      }),
    },
  );
  if (!response.ok) return null;
  const payload = await response.json().catch(() => null);
  const text = payload?.candidates?.[0]?.content?.parts?.[0]?.text;
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return { raw: text };
  }
}

export async function buildGraphOpsAiCommandPlan(command: string) {
  const template = selectTemplate(command);
  const rules = selectRules(command);
  const ai = await geminiSuggestion(command);
  const blocks = pipelineBlockCatalog.filter((block) =>
    [
      "source-upload",
      "aletheia-ontology-profile",
      "temporal-episode-splitter",
      "primitive-extraction",
      "neo4j-memory-write",
      "abstract-knowledge-graph",
      "agent-result-terminal",
      "benchmark-evaluation",
    ].includes(block.id),
  );

  return {
    mode: ai ? "gemini_assisted" : "deterministic_planner",
    command,
    selected_template: template,
    dynamic_ontology_engine: dynamicOntologyEngine.name,
    recommended_blocks: blocks,
    graph_layers: graphLayerBlueprints,
    neurosymbolic_rules: rules.length > 0 ? rules : neurosymbolicRuleCatalog.slice(0, 5),
    benchmark_blocks: benchmarkBlockCatalog.slice(0, 6),
    similar_configurations: pipelineConfigurationExamples.slice(0, 4),
    examples: aiCommandExamples,
    ai_suggestion: ai,
    next_action: "Create a pipeline plan, stage it to Databricks, ingest artifacts into Delta, then write accepted graph memory to Neo4j when secrets are bound.",
  };
}
