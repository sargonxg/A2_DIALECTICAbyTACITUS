import type { GraphData } from "@/types/graph";
import type { NodeType } from "@/types/ontology";

export interface OntologyNodeSpec {
  type: NodeType;
  label: string;
  tier: "Essential" | "Standard" | "Full";
  description: string;
  conflictUse: string;
}

export interface OntologyEdgeSpec {
  type: string;
  source: string;
  target: string;
  description: string;
}

export const ontologyNodes: OntologyNodeSpec[] = [
  {
    type: "actor",
    label: "Actor",
    tier: "Essential",
    description: "Person, organization, state, coalition, or informal group with agency.",
    conflictUse: "Who can act, block, escalate, mediate, or comply.",
  },
  {
    type: "conflict",
    label: "Conflict",
    tier: "Essential",
    description: "Sustained friction pattern with domain, scale, status, and escalation state.",
    conflictUse: "The root object that anchors every situation graph.",
  },
  {
    type: "event",
    label: "Event",
    tier: "Essential",
    description: "Discrete occurrence with time, severity, source evidence, and causal links.",
    conflictUse: "What happened, when, and what it changed.",
  },
  {
    type: "issue",
    label: "Issue",
    tier: "Essential",
    description: "Matter in dispute, including material, procedural, relational, and symbolic issues.",
    conflictUse: "What parties are fighting about on the surface.",
  },
  {
    type: "process",
    label: "Process",
    tier: "Essential",
    description: "Negotiation, mediation, litigation, arbitration, dialogue, or internal review process.",
    conflictUse: "How the situation is being managed or resolved.",
  },
  {
    type: "outcome",
    label: "Outcome",
    tier: "Essential",
    description: "Agreement, settlement, breakdown, ceasefire, ruling, sanction, apology, or new status.",
    conflictUse: "What a process produced and whether it held.",
  },
  {
    type: "location",
    label: "Location",
    tier: "Essential",
    description: "Hierarchical place context for events, institutions, and territorial claims.",
    conflictUse: "Where conflict dynamics are concentrated.",
  },
  {
    type: "interest",
    label: "Interest",
    tier: "Standard",
    description: "Underlying need, fear, priority, value, incentive, or constraint.",
    conflictUse: "Why positions matter to each party.",
  },
  {
    type: "norm",
    label: "Norm",
    tier: "Standard",
    description: "Law, treaty, contract, policy, social norm, or operational rule.",
    conflictUse: "What governs conduct and what may be violated.",
  },
  {
    type: "narrative",
    label: "Narrative",
    tier: "Standard",
    description: "Dominant frame, counter-frame, public story, or identity claim.",
    conflictUse: "How parties justify action and mobilize support.",
  },
  {
    type: "evidence",
    label: "Evidence",
    tier: "Standard",
    description: "Document, quote, testimony, report, transcript, artifact, or data excerpt.",
    conflictUse: "Grounding for every extracted claim.",
  },
  {
    type: "role",
    label: "Role",
    tier: "Standard",
    description: "Mediator, decision maker, advocate, witness, commander, negotiator, or affected party.",
    conflictUse: "What function an actor plays in a specific situation.",
  },
  {
    type: "emotional_state",
    label: "EmotionalState",
    tier: "Full",
    description: "Emotion profile grounded in Plutchik-style categories and intensity.",
    conflictUse: "Early signal for humiliation, fear, anger, disgust, and de-escalation openings.",
  },
  {
    type: "trust_state",
    label: "TrustState",
    tier: "Full",
    description: "Ability, benevolence, integrity, and overall trust relationship.",
    conflictUse: "Whether process design can rely on direct bargaining or needs guarantees.",
  },
  {
    type: "power_dynamic",
    label: "PowerDynamic",
    tier: "Full",
    description: "Power asymmetry and basis, including coercive, reward, expert, legitimate, and referent power.",
    conflictUse: "Who can impose costs, offer benefits, withhold resources, or shape options.",
  },
];

export const ontologyEdges: OntologyEdgeSpec[] = [
  { type: "PARTY_TO", source: "Actor", target: "Conflict", description: "Actor is a party to a conflict." },
  { type: "PARTICIPATES_IN", source: "Actor", target: "Event", description: "Actor participates in an event." },
  { type: "HAS_INTEREST", source: "Actor", target: "Interest", description: "Actor holds an underlying interest." },
  { type: "PART_OF", source: "Event", target: "Conflict", description: "Event belongs to the conflict timeline." },
  { type: "CAUSED", source: "Event", target: "Event", description: "One event plausibly caused another." },
  { type: "AT_LOCATION", source: "Event", target: "Location", description: "Event occurred at a place." },
  { type: "WITHIN", source: "Location", target: "Location", description: "Place is nested inside another place." },
  { type: "ALLIED_WITH", source: "Actor", target: "Actor", description: "Actors cooperate or form a coalition." },
  { type: "OPPOSED_TO", source: "Actor", target: "Actor", description: "Actors are in opposition." },
  { type: "HAS_POWER_OVER", source: "Actor", target: "Actor", description: "One actor has leverage over another." },
  { type: "MEMBER_OF", source: "Actor", target: "Actor", description: "Actor belongs to another actor entity." },
  { type: "GOVERNED_BY", source: "Conflict", target: "Norm", description: "Conflict is governed by a rule, policy, law, or treaty." },
  { type: "VIOLATES", source: "Event", target: "Norm", description: "Event breaches a governing norm." },
  { type: "RESOLVED_THROUGH", source: "Conflict", target: "Process", description: "Conflict is handled through a process." },
  { type: "PRODUCES", source: "Process", target: "Outcome", description: "Process produces an outcome." },
  { type: "EXPERIENCES", source: "Actor", target: "EmotionalState", description: "Actor experiences an emotional state." },
  { type: "TRUSTS", source: "Actor", target: "Actor", description: "Actor has a trust relationship with another actor." },
  { type: "PROMOTES", source: "Actor", target: "Narrative", description: "Actor promotes a narrative or frame." },
  { type: "ABOUT", source: "Narrative", target: "Conflict", description: "Narrative is about a conflict." },
  { type: "EVIDENCED_BY", source: "Event", target: "Evidence", description: "Event is grounded in evidence." },
];

export const ontologyTiers = [
  {
    name: "Essential",
    nodes: 7,
    edges: 6,
    color: "#10b981",
    description: "Core conflict map: actors, events, issues, places, processes, and outcomes.",
  },
  {
    name: "Standard",
    nodes: 12,
    edges: 13,
    color: "#3b82f6",
    description: "Adds interests, norms, narratives, evidence, and explicit roles.",
  },
  {
    name: "Full",
    nodes: 15,
    edges: 20,
    color: "#a855f7",
    description: "Adds emotion, trust, power, alliances, opposition, and causal reasoning.",
  },
];

export const graphOpsPipeline = [
  {
    name: "Open Corpus",
    detail: "Books, reports, transcripts, filings, public-domain corpora, meeting notes.",
    output: "Raw text chunks",
  },
  {
    name: "Ontology Extraction",
    detail: "Gemini extracts only TACITUS node and edge types, then validators reject malformed claims.",
    output: "Typed nodes and relationships",
  },
  {
    name: "Neo4j Aura",
    detail: "Each claim lands in a queryable knowledge graph with evidence, confidence, tenant, and workspace IDs.",
    output: "Operational conflict graph",
  },
  {
    name: "Databricks Delta",
    detail: "Jobs snapshot Neo4j into Delta, compute graph quality, review queues, actor features, and link candidates.",
    output: "Tables and review queues",
  },
  {
    name: "TACITUS Apps",
    detail: "GraphRAG, dashboards, analysts, and mediators query structured facts instead of loose text chunks.",
    output: "Explainable intelligence",
  },
];

export const conflictOntologyExtensions = [
  {
    name: "Escalation",
    frameworks: "Glasl, Kriesberg",
    graphSignals: "CAUSED event chains, severity velocity, PARTY_TO density, unresolved issues.",
  },
  {
    name: "Ripeness",
    frameworks: "Zartman, Lederach",
    graphSignals: "Mutually hurting stalemate, viable process nodes, mediator roles, trust repair events.",
  },
  {
    name: "Power",
    frameworks: "French/Raven",
    graphSignals: "HAS_POWER_OVER, resource control, role authority, sanction capacity, alliance asymmetry.",
  },
  {
    name: "Interests",
    frameworks: "Fisher/Ury, Burton",
    graphSignals: "HAS_INTEREST links, issue-interest separation, unmet basic needs, BATNA hints.",
  },
  {
    name: "Norms",
    frameworks: "Legal, policy, treaty, social norm analysis",
    graphSignals: "GOVERNED_BY, VIOLATES, evidence-backed rule breaches, severity and intent.",
  },
  {
    name: "Narratives",
    frameworks: "Winslade/Monk, Galtung",
    graphSignals: "PROMOTES frames, ABOUT conflicts, identity claims, contradiction between narratives and events.",
  },
];

export const sampleCypherQueries = [
  {
    title: "Find active conflicts by workspace",
    prompt: "Show active conflicts in this workspace.",
    cypher:
      "MATCH (c:ConflictNode:Conflict {workspace_id: $workspace_id})\nRETURN c.id, c.name, c.status, c.glasl_stage\nORDER BY coalesce(c.glasl_stage, 0) DESC\nLIMIT 25;",
  },
  {
    title: "Power asymmetry map",
    prompt: "Who has leverage over whom?",
    cypher:
      "MATCH (a:ConflictNode:Actor)-[r:HAS_POWER_OVER]->(b:ConflictNode:Actor)\nWHERE a.workspace_id = $workspace_id\nRETURN a.name AS source, b.name AS target, r.domain, r.magnitude, r.confidence\nORDER BY coalesce(r.magnitude, 0) DESC;",
  },
  {
    title: "Norm violations with evidence",
    prompt: "Which events violated rules and what evidence supports them?",
    cypher:
      "MATCH (e:ConflictNode:Event)-[v:VIOLATES]->(n:ConflictNode:Norm)\nOPTIONAL MATCH (e)-[:EVIDENCED_BY]->(ev:ConflictNode:Evidence)\nWHERE e.workspace_id = $workspace_id\nRETURN e.name, n.name, v.severity, collect(ev.name)[0..5] AS evidence;",
  },
  {
    title: "Causal escalation chain",
    prompt: "What caused the latest escalation?",
    cypher:
      "MATCH path = (first:ConflictNode:Event)-[:CAUSED*1..5]->(last:ConflictNode:Event)\nWHERE first.workspace_id = $workspace_id\nRETURN path\nORDER BY length(path) DESC\nLIMIT 10;",
  },
  {
    title: "Databricks review queue",
    prompt: "What should an analyst review first?",
    cypher:
      "MATCH ()-[r]->()\nWHERE r.workspace_id = $workspace_id AND coalesce(r.confidence, 1.0) < 0.72\nRETURN type(r) AS edge_type, r.id, r.confidence, r.source_quote\nORDER BY r.confidence ASC\nLIMIT 50;",
  },
];

export const benchmarkPlan = [
  {
    task: "Commitment tracking",
    baselineWeakness: "Often treats ambiguous acceptance as full agreement or misses later denial.",
    dialecticaAdvantage: "Builds actor-commitment-contestation subgraphs with provenance on each message.",
  },
  {
    task: "Position vs interest",
    baselineWeakness: "Summarizes stated demands without separating deeper constraints and needs.",
    dialecticaAdvantage: "Extracts Issue, Interest, Norm, and Actor links separately before answering.",
  },
  {
    task: "Causal chain",
    baselineWeakness: "Narrates chronology but does not distinguish order from causation.",
    dialecticaAdvantage: "Requires CAUSED edges with confidence, evidence, and review flags.",
  },
  {
    task: "Narrative drift",
    baselineWeakness: "Gives a generic sentiment summary.",
    dialecticaAdvantage: "Tracks PROMOTES and ABOUT relationships across turns and actors.",
  },
  {
    task: "Norm and policy constraints",
    baselineWeakness: "Misses which rules bind which actions.",
    dialecticaAdvantage: "Uses GOVERNED_BY and VIOLATES edges so policy constraints are queryable.",
  },
];

export const databricksJobs = [
  {
    name: "Book AI Extraction Demo",
    jobId: "136658630245751",
    actionKey: "book-demo",
    status: "Succeeded",
    purpose: "Seeds open book chunks and extracts TACITUS ontology candidates with Databricks AI Functions.",
    output: "raw_text_chunks: 35 rows; ai_extraction_candidates: 35 rows",
    runUrl:
      "https://dbc-69e04818-40fb.cloud.databricks.com/?o=7474658425841042#job/136658630245751/run/227559218086552",
  },
  {
    name: "Operational Loop",
    jobId: "958424080973640",
    status: "Ready for Neo4j secrets",
    purpose: "Writes candidates to Neo4j, snapshots Neo4j to Delta, computes graph quality, and builds review queues.",
    output: "nodes_bronze, edges_bronze, actor_features, graph_quality_signals, review_queue",
  },
  {
    name: "Complex Book Graph Demo",
    jobId: "261036137711214",
    actionKey: "complex-demo",
    status: "Succeeded",
    purpose: "Runs War and Peace, Crime and Punishment, and The Federalist Papers through the TACITUS ontology extraction pipeline.",
    output:
      "Run 795929402349644: raw_text_chunks now 333 rows; ai_extraction_candidates now 275 rows; claim_review_queue has 216 items",
    runUrl:
      "https://dbc-69e04818-40fb.cloud.databricks.com/?o=7474658425841042#job/261036137711214/run/795929402349644",
  },
  {
    name: "Neurosymbolic Benchmark",
    jobId: "278369455996320",
    actionKey: "benchmark",
    status: "Manual",
    purpose: "Compares baseline LLM answers against DIALECTICA graph-grounded answers.",
    output: "benchmark_items, benchmark_prompts, benchmark_answers, benchmark_judgments",
  },
  {
    name: "KGE Link Candidates",
    jobId: "921155103888424",
    status: "Manual",
    purpose: "Runs graph embedding/link prediction on Delta edge tables after enough graph data exists.",
    output: "kge_link_candidates",
  },
  {
    name: "Pipeline Artifact Ingestion",
    jobId: "238139876238377",
    actionKey: "pipeline-artifacts",
    status: "Succeeded",
    purpose: "Reads GraphOps pipeline-plan artifacts staged by the frontend and writes normalized Delta control-plane tables.",
    output: "pipeline_plans, pipeline_blocks, pipeline_ontology_profiles, pipeline_benchmark_blocks, pipeline_terminal_agents",
    runUrl:
      "https://dbc-69e04818-40fb.cloud.databricks.com/?o=7474658425841042#job/238139876238377/run/108767554485462",
  },
];

export const liveDeltaTables = [
  {
    table: "raw_text_chunks",
    rows: 333,
    role: "Source material split by workspace, source, chunk, and tenant.",
  },
  {
    table: "ai_extraction_candidates",
    rows: 275,
    role: "LLM-produced TACITUS node/edge JSON awaiting validation and graph writeback.",
  },
  {
    table: "ontology_profile_coverage",
    rows: 4,
    role: "Coverage scores for human-friction, literary, policy, and mediation profiles.",
  },
  {
    table: "source_reliability_signals",
    rows: 3,
    role: "Source-level trust, extraction freshness, chunk counts, and candidate volume.",
  },
  {
    table: "temporal_event_signals",
    rows: 3,
    role: "Event/process/outcome density and temporal edge coverage by source.",
  },
  {
    table: "claim_review_queue",
    rows: 216,
    role: "Low-confidence, weak-evidence, and audit-sampled claims for human review.",
  },
  {
    table: "pipeline_plans",
    rows: 1,
    role: "Frontend-created workspace pipeline artifacts normalized into Delta.",
  },
  {
    table: "pipeline_blocks",
    rows: 9,
    role: "Block-by-block pipeline configuration for ingestion, ontology, graph, agents, and benchmark stages.",
  },
  {
    table: "pipeline_ontology_profiles",
    rows: 1,
    role: "Aletheia dynamic ontology profiles with required nodes, edges, and core mappings.",
  },
  {
    table: "pipeline_benchmark_blocks",
    rows: 6,
    role: "Benchmark requirements attached to each pipeline plan.",
  },
  {
    table: "pipeline_terminal_agents",
    rows: 6,
    role: "Planned terminal agents for verification, GraphRAG planning, and benchmark judging.",
  },
];

export const sourcePacks = [
  {
    id: "books-complex-conflict-lab",
    name: "Complex Book Conflict Lab",
    sources: "War and Peace, Crime and Punishment, The Federalist Papers",
    profile: "literary-conflict + political-policy",
    nextRun: "Complex Book Graph Demo",
    why:
      "Stress-tests actors, events, norms, interests, temporal phases, public narratives, and causal chains on open-source books.",
  },
  {
    id: "books-romeo-juliet",
    name: "Romeo and Juliet Starter",
    sources: "Project Gutenberg 1513",
    profile: "literary-conflict + mediation-resolution",
    nextRun: "Book AI Extraction Demo",
    why:
      "Compact conflict escalation case for testing alliances, family opposition, emotion, trust collapse, and mediation failure.",
  },
  {
    id: "policy-friction-lab",
    name: "Policy Friction Lab",
    sources: "Open policy memos, statutes, meeting transcripts, public consultation notes",
    profile: "policy-analysis",
    nextRun: "Future policy ingestion workflow",
    why:
      "Maps constraints, institutions, veto players, implementation risks, legal norms, and public narratives.",
  },
  {
    id: "praxis-human-friction",
    name: "Praxis Human Friction",
    sources: "Team messages, meeting notes, user-provided case material",
    profile: "human-friction + mediation-resolution",
    nextRun: "Future private workspace ingestion workflow",
    why:
      "Makes DIALECTICA embeddable in Praxis: commitments, contested scope, trust repair, roles, and next questions.",
  },
];

export const precompiledNeeds = [
  {
    id: "understand-literary-conflict",
    label: "Understand a book conflict",
    objective: "Extract actors, episodes, commitments, constraints, events, narratives, and actor states from a book.",
    profile: "literary-conflict",
    sampleKey: "romeo-juliet-conflict",
    caseId: "romeo-juliet-conflict",
    workspaceId: "books-romeo-juliet",
    defaultQuestion: "Which events and commitments intensify the conflict in Romeo and Juliet?",
  },
  {
    id: "mediate-human-friction",
    label: "Prepare a mediator brief",
    objective: "Extract commitments, contested scope, trust state, constraints, interests, and next verification questions.",
    profile: "mediation-resolution",
    sampleKey: "mediation-commitments",
    caseId: "mediation-commitments",
    workspaceId: "praxis-human-friction",
    defaultQuestion: "What commitments constrain Alex and what should a mediator verify first?",
  },
  {
    id: "policy-constraint-map",
    label: "Map policy constraints",
    objective: "Extract institutions, norms, constraints, leverage, implementation risks, and required process steps.",
    profile: "policy-analysis",
    sampleKey: "",
    caseId: "policy-constraint-map",
    workspaceId: "policy-friction-lab",
    defaultQuestion: "Which constraints block the feasible policy options?",
  },
  {
    id: "field-intelligence-brief",
    label: "Structure field reports",
    objective: "Separate source claims, direct observations, inferred claims, actor states, events, locations, and gaps.",
    profile: "field-intelligence",
    sampleKey: "",
    caseId: "field-intelligence-brief",
    workspaceId: "conflict-desk-field",
    defaultQuestion: "What changed, what is verified, and what remains uncertain?",
  },
];

export const topTenBuildPriorities = [
  {
    item: "Upload-to-Databricks ingestion",
    why: "Every TXT/PDF/source pack should be staged to the lakehouse with workspace, case, ontology, and objective metadata.",
    status: "started",
  },
  {
    item: "Neo4j production writeback",
    why: "Graph memory becomes real when accepted primitives and relationships land in Aura with provenance and case separation.",
    status: "blocked on rotated secrets",
  },
  {
    item: "GraphOps agent launchpad",
    why: "Operators need one-click Source Scout, Ontology Builder, Claim Verifier, Temporal Analyst, GraphRAG Planner, and Benchmark Judge runs.",
    status: "started",
  },
  {
    item: "Dynamic ontology builder",
    why: "The user objective should choose required primitives, profile coverage gates, and extraction prompts.",
    status: "next",
  },
  {
    item: "Review queue UI",
    why: "Low-confidence claims, missing evidence, contradictions, and inferred facts must become analyst work.",
    status: "next",
  },
  {
    item: "Live Neo4j graph explorer",
    why: "Users should see the actual case graph, not only a static preview, after each ingestion run.",
    status: "next",
  },
  {
    item: "Databricks Delta ingestion tables for uploads",
    why: "DBFS-staged uploads need a job that turns them into raw_text_chunks, extraction candidates, and quality tables.",
    status: "next",
  },
  {
    item: "Graph-grounded answer API",
    why: "DIALECTICA should answer hard conflict questions with Cypher context, source spans, and confidence.",
    status: "next",
  },
  {
    item: "Benchmark workbench",
    why: "Baseline LLM vs graph-grounded TACITUS comparisons should be runnable and inspectable from the frontend.",
    status: "started",
  },
  {
    item: "Embeddable product contract",
    why: "Praxis and future TACITUS products need stable GraphOps endpoints, permissions, audit logs, and workspace scoping.",
    status: "documented",
  },
];

export const nextSprintPriorities = [
  {
    item: "Workspace-as-project model",
    why: "Every book, conflict, mediation file, policy case, or argument map should become a workspace with repeatable pipelines.",
    deliverable: "Workspace template picker and scoped pipeline plan.",
  },
  {
    item: "Composable pipeline blocks",
    why: "Users should assemble ingestion, ontology, graph, agent, and benchmark steps block by block.",
    deliverable: "Block catalog with implemented, partial, and planned states.",
  },
  {
    item: "Temporal episode builder",
    why: "Conflict analysis depends on phases, turning points, commitments, and state changes over time.",
    deliverable: "Episode segmentation block and episode-scoped graph writes.",
  },
  {
    item: "Dynamic ontology engine",
    why: "Ontology should adapt to the user role, objective, source type, situation, and question pattern.",
    deliverable: "Aletheia profile generator with core mappings and validation gates.",
  },
  {
    item: "Knowledge graph strategy graph",
    why: "DIALECTICA should not only store facts; it should store reusable analytical methods and resolution frameworks.",
    deliverable: "Situation graph plus abstract knowledge graph plus reasoning graph.",
  },
  {
    item: "Databricks upload ingestion job",
    why: "Frontend-staged uploads need an automated lakehouse job to convert JSON artifacts into Delta tables.",
    deliverable: "Workspace-file ingestion notebook and bundle job.",
  },
  {
    item: "Neo4j pipeline artifact writeback",
    why: "Pipeline plans, ontology versions, and benchmark runs should be queryable graph objects.",
    deliverable: "PipelineRun, PipelineBlock, OntologyProfile, BenchmarkRun nodes.",
  },
  {
    item: "Agent terminal blocks",
    why: "Pipelines should end in concrete agents: verifier, mediator brief writer, GraphRAG planner, benchmark judge.",
    deliverable: "Allowlisted agent actions and result artifacts.",
  },
  {
    item: "Benchmark block library",
    why: "Each workflow needs measurable tests: provenance, causal precision, graph coverage, temporal accuracy.",
    deliverable: "Benchmark block templates attached to pipeline plans.",
  },
  {
    item: "Connector-neutral backend plan",
    why: "Databricks is powerful, but the architecture should also support Python/DuckDB, Neo4j-only, FalkorDB, and local mode.",
    deliverable: "Backend mode selector with block compatibility rules.",
  },
];

export const workspaceProjectTemplates = [
  {
    id: "book-conflict-lab",
    name: "Book Conflict Lab",
    workspacePrefix: "books",
    description: "Public-domain books or chapters turned into character, episode, narrative, and escalation graphs.",
    defaultObjective: "Understand conflict dynamics, turning points, commitments, constraints, and narratives in a book.",
    recommendedProfile: "literary-conflict",
    sourceExamples: "Romeo and Juliet, War and Peace, Crime and Punishment",
  },
  {
    id: "mediation-case-file",
    name: "Mediation Case File",
    workspacePrefix: "mediation",
    description: "Meeting notes, emails, transcripts, and position statements structured for a mediator.",
    defaultObjective: "Separate positions, interests, commitments, trust problems, constraints, and viable intervention options.",
    recommendedProfile: "mediation-resolution",
    sourceExamples: "Intake notes, party statements, negotiation transcript",
  },
  {
    id: "policy-friction-map",
    name: "Policy Friction Map",
    workspacePrefix: "policy",
    description: "Policy proposals, statutes, public comments, and implementation memos structured as constraint graphs.",
    defaultObjective: "Map actors, rules, constraints, veto points, implementation risks, and policy options.",
    recommendedProfile: "policy-analysis",
    sourceExamples: "Statute, agency memo, hearing transcript, public consultation",
  },
  {
    id: "argument-claim-graph",
    name: "Argument Claim Graph",
    workspacePrefix: "arguments",
    description: "Debates, essays, legal arguments, or analytic claims decomposed into claim, evidence, objection, and warrant graphs.",
    defaultObjective: "Extract claims, warrants, evidence, counterclaims, assumptions, and unresolved disputes.",
    recommendedProfile: "human-friction",
    sourceExamples: "Debate transcript, op-ed corpus, legal memo, research dispute",
  },
  {
    id: "field-situation-portal",
    name: "Field Situation Portal",
    workspacePrefix: "situation",
    description: "Reports and observations structured into actors, events, source trust, uncertainty, and collection gaps.",
    defaultObjective: "Identify verified events, actor states, uncertain claims, source reliability, and what changed.",
    recommendedProfile: "field-intelligence",
    sourceExamples: "Situation reports, interviews, public records, local observations",
  },
  {
    id: "labor-union-mediation",
    name: "Labor Union Mediation",
    workspacePrefix: "labor",
    description: "Union, employer, regulator, and mediator materials structured for negotiation readiness.",
    defaultObjective:
      "Build a mediation graph for labor conflict: parties, commitments, disputed terms, leverage, legal constraints, process options, and trust repair.",
    recommendedProfile: "mediation-resolution",
    sourceExamples: "Collective agreement, bargaining notes, union statements, employer memos, media reports",
  },
  {
    id: "regional-border-process",
    name: "Regional Border Process",
    workspacePrefix: "regional-border",
    description: "Small territorial or administrative border dispute structured for meeting preparation and policy dialogue.",
    defaultObjective:
      "Prepare a meeting brief by mapping actors, jurisdictional claims, norms, territorial narratives, incidents, constraints, and de-escalation options.",
    recommendedProfile: "policy-analysis",
    sourceExamples: "Maps, meeting minutes, public statements, local media, legal documents, historical summaries",
  },
  {
    id: "expert-method-graph",
    name: "Expert Method Graph",
    workspacePrefix: "expert-method",
    description: "Abstract frameworks, mediator thinking, legal methods, HR processes, and negotiation doctrine as reusable knowledge graphs.",
    defaultObjective:
      "Extract abstract concepts, diagnostic methods, decision rules, intervention patterns, and expert reasoning traces from knowledge sources.",
    recommendedProfile: "human-friction",
    sourceExamples: "Mediator manuals, legal opinions, HR playbooks, conflict-resolution books, expert interview notes",
  },
];

export const pipelineBlockCatalog = [
  {
    id: "source-upload",
    stage: "Ingest",
    name: "Source Upload",
    status: "implemented",
    backend: "frontend + Databricks staging",
    description: "Accept TXT/PDF/pasted text and preserve workspace, case, objective, ontology profile, and source metadata.",
  },
  {
    id: "lakehouse-chunking",
    stage: "Ingest",
    name: "Lakehouse Chunking",
    status: "partial",
    backend: "Databricks Delta",
    description: "Convert staged uploads into raw_text_chunks with offsets, source IDs, and extraction run IDs.",
  },
  {
    id: "local-python-digestion",
    stage: "Ingest",
    name: "Local Python Digestion",
    status: "implemented",
    backend: "Python CLI",
    description: "Run the local TACITUS core v1 ingestion pipeline without Databricks for low-cost in-house mode.",
  },
  {
    id: "aletheia-ontology-profile",
    stage: "Ontology",
    name: "Aletheia Dynamic Ontology",
    status: "partial",
    backend: "frontend + validators",
    description: "Generate a case-specific ontology profile that maps custom concepts back to TACITUS core primitives.",
  },
  {
    id: "temporal-episode-splitter",
    stage: "Temporal",
    name: "Temporal Episode Splitter",
    status: "planned",
    backend: "Databricks or Python",
    description: "Segment sources into episodes, phases, turning points, valid_from/valid_to, and observed_at timelines.",
  },
  {
    id: "primitive-extraction",
    stage: "Structure",
    name: "TACITUS Primitive Extraction",
    status: "implemented",
    backend: "frontend API + Python CLI + Databricks AI",
    description: "Extract actors, claims, commitments, constraints, events, narratives, actor states, and evidence spans.",
  },
  {
    id: "neo4j-memory-write",
    stage: "Graph",
    name: "Neo4j Graph Memory",
    status: "blocked on rotated secrets",
    backend: "Neo4j Aura",
    description: "Write scoped nodes and relationships with provenance, episodes, ontology versions, and extraction run IDs.",
  },
  {
    id: "falkordb-alternative",
    stage: "Graph",
    name: "FalkorDB Adapter",
    status: "planned",
    backend: "FalkorDB",
    description: "Optional RedisGraph-compatible graph backend for lighter deployments where Neo4j is not required.",
  },
  {
    id: "abstract-knowledge-graph",
    stage: "Reason",
    name: "Abstract Knowledge Graph",
    status: "planned",
    backend: "Neo4j + ontology files",
    description: "Store reusable conflict-resolution concepts, frameworks, diagnostics, and intervention patterns.",
  },
  {
    id: "agent-result-terminal",
    stage: "Act",
    name: "Agent Result Terminal",
    status: "partial",
    backend: "GraphOps allowlisted agents",
    description: "Run verifier, temporal analyst, GraphRAG planner, mediator brief writer, and benchmark judge agents.",
  },
  {
    id: "benchmark-evaluation",
    stage: "Benchmark",
    name: "Benchmark Evaluation",
    status: "partial",
    backend: "Databricks + evaluator prompts",
    description: "Score baseline LLM answers against graph-grounded answers for provenance, causality, temporal accuracy, and ontology coverage.",
  },
];

export const benchmarkBlockCatalog = [
  {
    id: "provenance-fidelity",
    name: "Provenance Fidelity",
    metric: "Can every answer cite the exact source span and extraction run?",
    appliesTo: "all workflows",
  },
  {
    id: "temporal-accuracy",
    name: "Temporal Accuracy",
    metric: "Does the answer distinguish before/after, valid_from/valid_to, and episode transitions?",
    appliesTo: "conflict, policy, field reports",
  },
  {
    id: "causal-precision",
    name: "Causal Precision",
    metric: "Does the system separate chronology from asserted or inferred causation?",
    appliesTo: "conflict escalation and policy analysis",
  },
  {
    id: "commitment-recall",
    name: "Commitment Recall",
    metric: "Are promises, denials, constraints, and contested scope captured with actor links?",
    appliesTo: "mediation and human friction",
  },
  {
    id: "ontology-coverage",
    name: "Ontology Coverage",
    metric: "Does the graph contain the required nodes and edges for the selected user objective?",
    appliesTo: "dynamic ontology workflows",
  },
  {
    id: "baseline-vs-graph",
    name: "Baseline vs Graph-Grounded Answer",
    metric: "Does DIALECTICA improve answer support, causal precision, ambiguity handling, and graph overlap?",
    appliesTo: "all benchmarked pipelines",
  },
];

export const pipelineConfigurationExamples = [
  {
    id: "labor-union-mediation-live",
    title: "Labor Union Mediation Pipeline",
    user: "Mediator preparing for bargaining or shuttle diplomacy",
    objective:
      "Know what each side claims, what was promised, what constraints are legal or financial, and which trust repair options are credible.",
    sources: ["Collective agreement", "union demands", "employer offer", "meeting notes", "local media"],
    ontologyFocus: ["Actor", "Commitment", "Constraint", "Interest", "Leverage", "ActorState", "Episode"],
    episodes: ["pre-bargaining", "strike threat", "mediated session", "tentative agreement", "compliance review"],
    graphOutputs: ["commitment ledger", "red-line map", "trust-state timeline", "mediator option graph"],
    benchmark: "Commitment recall + provenance fidelity + intervention usefulness",
  },
  {
    id: "regional-border-meeting",
    title: "Regional Border Process Pipeline",
    user: "Policy analyst preparing a meeting on a small territorial dispute",
    objective:
      "Separate jurisdictional claims, historical narratives, incidents, legal norms, veto players, and de-escalation paths.",
    sources: ["maps", "local media", "meeting transcript", "administrative law", "stakeholder letters"],
    ontologyFocus: ["Actor", "Claim", "Narrative", "Constraint", "Event", "Source", "EvidenceSpan"],
    episodes: ["historical claim", "administrative change", "public escalation", "closed-door meeting", "proposed settlement"],
    graphOutputs: ["claim-evidence graph", "actor influence graph", "norm constraint map", "meeting prep brief"],
    benchmark: "Causal precision + temporal accuracy + source reliability",
  },
  {
    id: "romeo-human-friction",
    title: "Romeo and Juliet Human Friction Pipeline",
    user: "Researcher testing whether literature can become a deterministic conflict graph",
    objective:
      "Model love, power, family identity, banishment, secrecy, escalation, and failed mediation as queryable graph structure.",
    sources: ["Project Gutenberg Romeo and Juliet", "scene summaries", "optional scholarly notes"],
    ontologyFocus: ["Actor", "Narrative", "Event", "Constraint", "Commitment", "ActorState", "Episode"],
    episodes: ["family feud", "secret bond", "violent escalation", "banishment", "failed intervention"],
    graphOutputs: ["character conflict graph", "love-power-constraint map", "escalation timeline", "counterfactual question set"],
    benchmark: "Ontology coverage + temporal accuracy + graph-grounded answer quality",
  },
  {
    id: "expert-mediator-methods",
    title: "Expert Mediator Method Graph",
    user: "TACITUS developer building reusable expert reasoning substrate",
    objective:
      "Turn mediation and legal reasoning frameworks into reusable abstract knowledge graphs that can be applied to new cases.",
    sources: ["mediation manuals", "legal opinions", "HR playbooks", "expert notes"],
    ontologyFocus: ["Claim", "Interest", "Constraint", "Leverage", "Narrative", "EvidenceSpan", "ExtractionRun"],
    episodes: ["diagnosis", "option generation", "risk review", "intervention design", "post-agreement learning"],
    graphOutputs: ["method graph", "diagnostic checklist graph", "intervention pattern graph", "expert reasoning trace"],
    benchmark: "Recommendation groundedness + framework recall + analyst review score",
  },
];

export const pipelineStageGuide = [
  {
    stage: "Ingest",
    color: "blue",
    purpose: "Bring sources into a scoped workspace with provenance, trust, license, and source type.",
  },
  {
    stage: "Ontology",
    color: "violet",
    purpose: "Select or generate the Aletheia ontology profile for the user objective and case type.",
  },
  {
    stage: "Temporal",
    color: "amber",
    purpose: "Split the situation into episodes, phases, turning points, and valid time ranges.",
  },
  {
    stage: "Structure",
    color: "emerald",
    purpose: "Extract TACITUS primitives and map custom case concepts back to core primitives.",
  },
  {
    stage: "Graph",
    color: "cyan",
    purpose: "Write situation, source, temporal, knowledge, reasoning, and activity graph layers.",
  },
  {
    stage: "Reason",
    color: "fuchsia",
    purpose: "Apply abstract knowledge graphs, frameworks, symbolic checks, and graph retrieval.",
  },
  {
    stage: "Act",
    color: "rose",
    purpose: "Run task-specific agents and produce briefs, questions, review queues, and user artifacts.",
  },
  {
    stage: "Benchmark",
    color: "slate",
    purpose: "Measure whether graph-grounded answers beat baseline LLM answers for the selected task.",
  },
];

export const dynamicOntologyEngine = {
  name: "Aletheia Dynamic Ontology Engine",
  shortName: "Aletheia",
  purpose:
    "Create, maintain, and modify case-specific ontologies while forcing every extension to map back to TACITUS core primitives.",
  inputs: ["user role", "objective", "source type", "case type", "question pattern", "risk tolerance"],
  outputs: [
    "OntologyProfile",
    "ProfileRequirement",
    "CustomType -> CorePrimitive mapping",
    "validation gates",
    "benchmark expectations",
  ],
  coreRule:
    "A custom type is allowed only if it maps to Actor, Claim, Interest, Constraint, Leverage, Commitment, Event, Narrative, Source, Episode, ActorState, ExtractionRun, or EvidenceSpan.",
};

export const ingestionTreeTemplate = [
  {
    level: "Document",
    output: "SourceDocument",
    purpose: "Preserve title, file type, trust level, source id, license, and case/workspace ownership.",
  },
  {
    level: "Chunk",
    output: "SourceChunk",
    purpose: "Split text or PDF content into character-offset chunks for repeatable extraction.",
  },
  {
    level: "Evidence",
    output: "EvidenceSpan",
    purpose: "Bind each extracted graph item to a specific source span.",
  },
  {
    level: "Ontology Profile",
    output: "Profile requirements",
    purpose: "Choose what to look for based on the user objective: literary conflict, mediation, policy, or intelligence.",
  },
  {
    level: "Primitive Extraction",
    output: "Actor, Claim, Commitment, Constraint, Event, Narrative, ActorState",
    purpose: "Create TACITUS primitives with confidence, source id, extraction run id, and case separation.",
  },
  {
    level: "Graph Memory",
    output: "Neo4j TacitusCoreV1 nodes and relationships",
    purpose: "Store the case so users can keep adding books, reports, episodes, and new ontology extensions.",
  },
];

export const analystFlow = [
  {
    step: "1. Define the mission",
    operatorQuestion: "What do I need to understand, decide, mediate, or monitor?",
    systemAction:
      "DIALECTICA selects or suggests an ontology profile from the user role, objective, source type, and question type.",
    graphOutput: "UseCase, OntologyProfile, QuestionType, ProfileRequirement",
  },
  {
    step: "2. Bring sources",
    operatorQuestion: "What text, transcript, book, memo, report, or field note should ground this case?",
    systemAction:
      "Databricks chunks the source pack, records provenance, source trust, and extraction run metadata.",
    graphOutput: "Source, Document, Chunk, Evidence, Claim",
  },
  {
    step: "3. Extract primitives",
    operatorQuestion: "Who are the actors, what happened, what matters, and what is contested?",
    systemAction:
      "AI extraction emits only allowed TACITUS primitives and relationships, then validation gates reject malformed claims.",
    graphOutput: "Actor, Event, Conflict, Issue, Interest, Norm, Process, Outcome",
  },
  {
    step: "4. Build situation memory",
    operatorQuestion: "How are the facts connected across time, place, sources, and claims?",
    systemAction:
      "Neo4j stores the operational graph with workspace, tenant, confidence, assertion type, and evidence on every fact.",
    graphOutput: "Situation Graph + Source Graph + Temporal Graph",
  },
  {
    step: "5. Reason and review",
    operatorQuestion: "What is inferred, uncertain, contradictory, or ready for expert review?",
    systemAction:
      "Databricks computes profile coverage, temporal density, low-confidence claims, link candidates, and benchmark results.",
    graphOutput: "Inference, ReasoningTrace, OperationalSignal, ReviewDecision",
  },
  {
    step: "6. Answer with provenance",
    operatorQuestion: "What should I believe, what should I ask next, and what could de-escalate?",
    systemAction:
      "GraphRAG retrieves typed subgraphs and forces the LLM to answer with evidence, uncertainty, and missing facts.",
    graphOutput: "Provenance-backed answer + next collection plan",
  },
];

export const researchSignals = [
  {
    claim: "Ontology grounding improves factual recall and correctness",
    evidence:
      "OG-RAG reports higher accurate-fact recall and response correctness by grounding retrieval in domain ontologies.",
    source: "ACL Anthology, OG-RAG",
    url: "https://aclanthology.org/2025.emnlp-main.1674/",
  },
  {
    claim: "Knowledge graphs are a recognized hallucination-mitigation path",
    evidence:
      "Recent surveys frame KG-augmented generation as a way to add structured factual memory, provenance, and verification.",
    source: "ScienceDirect survey",
    url: "https://www.sciencedirect.com/science/article/pii/S1570826824000301",
  },
  {
    claim: "Graph embeddings and link prediction support missing-relationship discovery",
    evidence:
      "Neo4j GDS documents node embeddings and link prediction as downstream graph ML tasks for discovering likely relationships.",
    source: "Neo4j Graph Data Science",
    url: "https://neo4j.com/docs/graph-data-science/current/machine-learning/node-embeddings/",
  },
  {
    claim: "Repeatable data/AI workflows belong in orchestrated jobs",
    evidence:
      "Databricks Lakeflow Jobs are designed to coordinate ETL, notebooks, ML, AI workloads, monitoring, and repeatable execution.",
    source: "Databricks Lakeflow Jobs",
    url: "https://docs.databricks.com/aws/en/jobs/",
  },
];

export const conflictUseCases = [
  {
    name: "Civilian mediation desk",
    userNeed: "A mediator needs the interests, positions, trust injuries, power asymmetries, and viable next questions.",
    ontologyEmphasis: "Interest, Issue, TrustState, PowerDynamic, Process, Outcome, Role",
    aha:
      "The system separates what parties demand from what they need, then shows which claims are verified, inferred, or contested.",
  },
  {
    name: "Policy friction analysis",
    userNeed: "A policy team needs constraints, jurisdictions, veto players, implementation risks, and public narratives.",
    ontologyEmphasis: "Norm, Actor, Location, Process, Interest, Narrative, Outcome",
    aha:
      "A plain summary says 'budget and timing'; the graph shows which rule binds which actor and which constraint blocks which option.",
  },
  {
    name: "Field intelligence understanding",
    userNeed:
      "An analyst needs to turn fragmentary reports into a source-aware situation graph without confusing rumor, direct observation, and inference.",
    ontologyEmphasis: "Source, Claim, Evidence, Actor, Event, Location, TemporalInterval, Inference",
    aha:
      "Every claim carries provenance and assertion type, so the LLM cannot silently treat sketchy or inferred material as ground truth.",
  },
  {
    name: "Literary conflict lab",
    userNeed: "A researcher wants deterministic questions about characters, motives, turning points, alliances, and escalation.",
    ontologyEmphasis: "Actor, Event, Narrative, EmotionalState, ConflictPhase, Evidence",
    aha:
      "A book becomes a repeatable conflict corpus for testing extraction quality before using private or operational material.",
  },
  {
    name: "Praxis team companion",
    userNeed: "A team needs commitments, contested scope, decision drift, trust repair, and next actions from messy collaboration data.",
    ontologyEmphasis: "Actor, Issue, Interest, TrustState, Role, Process, Claim",
    aha:
      "DIALECTICA can be embedded as a service: Praxis sends source material and gets back a graph-grounded friction brief.",
  },
];

export const operatorDeliverables = [
  {
    name: "Actor and leverage map",
    description: "Who can act, block, escalate, mediate, comply, or impose costs.",
    graphBasis: "Actor, Role, PARTY_TO, HAS_POWER_OVER, ALLIED_WITH, OPPOSED_TO",
  },
  {
    name: "Escalation timeline",
    description: "What happened, what merely preceded, what plausibly caused, and what changed phase.",
    graphBasis: "Event, Episode, TemporalInterval, PRECEDES, CAUSED, ESCALATES",
  },
  {
    name: "Interest-position matrix",
    description: "What each party says it wants versus the need, fear, value, or constraint behind the position.",
    graphBasis: "Actor, Issue, Interest, Narrative, HAS_INTEREST, PROMOTES",
  },
  {
    name: "Norm and constraint ledger",
    description: "Which rule, policy, contract, jurisdiction, or social norm governs each option.",
    graphBasis: "Norm, Process, Outcome, GOVERNED_BY, VIOLATES, PRODUCES",
  },
  {
    name: "Source confidence ledger",
    description: "Which claims are trusted, user-asserted, inferred, sketchy, contested, or unverified.",
    graphBasis: "Source, Evidence, Claim, assertion_type, source_trust, claim_status",
  },
  {
    name: "Mediation readiness brief",
    description: "Whether a process is viable now, what would reduce risk, and what next questions matter.",
    graphBasis: "TrustState, PowerDynamic, Process, Outcome, Interest, ReviewDecision",
  },
  {
    name: "Intelligence gaps",
    description: "What the system cannot responsibly answer yet because evidence or graph coverage is missing.",
    graphBasis: "OntologyProfile, OperationalSignal, claim_review_queue, profile coverage",
  },
];

export const benchmarkRunCards = [
  {
    run: "complex-books-ontology-001",
    n: 5,
    graphSnapshot: "books-complex-conflict-lab / Delta candidates / run 795929402349644",
    evaluator: "Databricks model judge + gold summaries",
    metrics: "provenance, graph overlap, causal precision, ambiguity handling",
    failureMode: "Current weak point: graph context still falls back to Delta until Neo4j writeback secrets are configured.",
  },
  {
    run: "human-friction-commitments-001",
    n: 5,
    graphSnapshot: "synthetic workplace/family/policy/diplomatic items",
    evaluator: "Gold summary and JSON judge rubric",
    metrics: "commitment tracking, position-interest separation, narrative drift",
    failureMode: "Needs more adversarial examples with sarcasm, implicit commitments, and multi-speaker ambiguity.",
  },
  {
    run: "future-mediator-eval-001",
    n: 30,
    graphSnapshot: "private or public mediation transcripts with redaction",
    evaluator: "Human expert plus LLM judge disagreement analysis",
    metrics: "interests, viable process options, trust repair, harm-aware uncertainty",
    failureMode: "Must avoid recommending action from unverified sensitive claims.",
  },
];

export const safetyBoundaries = [
  {
    boundary: "Human review before action",
    detail: "DIALECTICA can structure, retrieve, and compare claims; high-impact decisions require analyst or mediator review.",
  },
  {
    boundary: "Source sensitivity",
    detail: "Every source pack should carry sensitivity, trust class, license, and permitted-use metadata before extraction.",
  },
  {
    boundary: "Inference is labeled",
    detail: "Model hypotheses, inferred facts, and explicit source claims are stored differently and shown differently.",
  },
  {
    boundary: "Non-escalation by design",
    detail: "Resolution-oriented outputs emphasize uncertainty, de-escalation options, missing facts, and civilian harm risk.",
  },
];

export const qualityGates = [
  {
    gate: "Ontology validity",
    check: "Every extracted object must use an allowed TACITUS label or relationship.",
    failureAction: "Reject malformed candidate before Neo4j writeback.",
  },
  {
    gate: "Evidence grounding",
    check: "Every claim should carry a source quote, chunk id, source id, and assertion type.",
    failureAction: "Send to claim_review_queue as weak_or_missing_evidence_quote.",
  },
  {
    gate: "Temporal separation",
    check: "PRECEDES, CAUSED, ESCALATES, and DE_ESCALATES must stay distinct.",
    failureAction: "Downgrade causal confidence and require analyst review.",
  },
  {
    gate: "Profile coverage",
    check: "The active ontology profile must have enough required node and edge coverage.",
    failureAction: "Ask for more sources or run profile-specific extraction.",
  },
  {
    gate: "Provenance state",
    check: "Separate explicit, inferred, user_asserted, model_hypothesis, and imported claims.",
    failureAction: "Prevent unverified inferred facts from being treated as ground truth.",
  },
];

export const orchestrationEvents = [
  {
    event: "source.pack.created",
    payload: "workspace_id, source_ids, trust_policy, ontology_profile",
    consumer: "Databricks ingestion job",
  },
  {
    event: "ontology.profile.selected",
    payload: "profile_id, objective, required_nodes, required_edges, question_types",
    consumer: "Ontology Builder and extraction prompt generator",
  },
  {
    event: "claims.extracted",
    payload: "candidate_table, model_endpoint, run_id, workspace_id",
    consumer: "Validation, quality gates, Neo4j writeback",
  },
  {
    event: "graph.updated",
    payload: "workspace_id, graph_version, changed_nodes, changed_edges",
    consumer: "GraphRAG Planner, benchmarks, TACITUS products",
  },
  {
    event: "benchmark.completed",
    payload: "run_id, baseline_scores, dialectica_scores, failures",
    consumer: "Publication dashboard and model improvement loop",
  },
];

export const embeddableSurfaces = [
  {
    product: "Praxis",
    capability: "Human-friction companion",
    contract:
      "Pass messages and objective; receive typed commitments, interests, trust risks, repair moves, and provenance-backed next questions.",
  },
  {
    product: "Policy Lab",
    capability: "Constraint and stakeholder graph",
    contract:
      "Pass policy docs; receive actors, jurisdictions, norms, veto players, implementation risks, and testable process options.",
  },
  {
    product: "Conflict Desk",
    capability: "Situation portal",
    contract:
      "Pass source stream; receive actor map, phase timeline, escalation signals, causal chains, and review queue.",
  },
  {
    product: "Benchmark Lab",
    capability: "Neurosymbolic evaluation",
    contract:
      "Pass questions and gold criteria; receive baseline versus graph-grounded scores with failure categories.",
  },
];

export const graphCategories = [
  {
    category: "Identity",
    nodes: ["User", "Project", "Workspace", "Situation"],
    question: "Who owns this analysis and which situation is being modeled?",
  },
  {
    category: "Source",
    nodes: ["Source", "Document", "Chunk", "Evidence", "Claim"],
    question: "Where did each fact come from and how trustworthy is it?",
  },
  {
    category: "Situation",
    nodes: ["Actor", "Conflict", "Event", "Issue", "Interest", "Norm", "Process", "Outcome"],
    question: "What is happening, who is involved, and what matters?",
  },
  {
    category: "Temporal",
    nodes: ["Episode", "TemporalInterval", "ConflictPhase", "PhaseAssertion"],
    question: "What phase is the conflict in and how did it change over time?",
  },
  {
    category: "Reasoning",
    nodes: ["Inference", "ReasoningTrace", "InferredFact", "OperationalSignal"],
    question: "What did TACITUS infer and which claims still need verification?",
  },
  {
    category: "Profile",
    nodes: ["OntologyProfile", "UseCase", "QuestionType", "ProfileRequirement"],
    question: "Which ontology should be active for this user objective?",
  },
];

export const ontologyContracts = [
  {
    tier: "Live core extraction",
    status: "implemented",
    labels: "Actor, Conflict, Event, Issue, Interest, Norm, Process, Outcome, Location, Evidence, Role, Narrative, EmotionalState, TrustState, PowerDynamic",
    relationships: "PARTY_TO, PARTICIPATES_IN, HAS_INTEREST, CAUSED, VIOLATES, EVIDENCED_BY, TRUSTS, HAS_POWER_OVER, PROMOTES",
  },
  {
    tier: "Dynamic profile layer",
    status: "implemented in Delta quality tables and Neo4j schema files",
    labels: "OntologyProfile, UseCase, QuestionType, ProfileRequirement, ConflictPhase, TemporalInterval, Episode",
    relationships: "HAS_PROFILE, REQUIRES_LABEL, REQUIRES_RELATIONSHIP, HAS_PHASE, OCCURS_DURING, PRECEDES",
  },
  {
    tier: "Reasoning and review layer",
    status: "implemented as schema/runbook, enabled after Neo4j writeback secrets",
    labels: "Claim, Inference, ReasoningTrace, OperationalSignal, ReviewDecision",
    relationships: "ASSERTS, SUPPORTS, CONTRADICTS, GENERATED_BY, REVIEWED_BY, FLAGS",
  },
  {
    tier: "Product-specific extensions",
    status: "planned per product profile",
    labels: "Commitment, VetoPlayer, BATNAHint, MediationOption, IntelligenceGap",
    relationships: "DENIES_SCOPE, REPAIRS_TRUST, BLOCKS_OPTION, REDUCES_RISK, NEEDS_COLLECTION",
  },
];

export const neo4jStatus = [
  {
    item: "Schema and constraints",
    state: "ready",
    detail: "Base and dynamic graph-layer Cypher files exist under infrastructure/neo4j.",
  },
  {
    item: "Read-only query API",
    state: "ready when env secrets exist",
    detail: "The protected frontend calls an allowlisted server-side Neo4j route, never raw browser credentials.",
  },
  {
    item: "Databricks writeback",
    state: "implemented, waiting fresh secrets",
    detail: "The notebook writes accepted candidates into Neo4j after neo4j-uri/user/password/database are added to the Databricks secret scope.",
  },
  {
    item: "Graph versioning",
    state: "next",
    detail: "Each writeback should stamp graph_version, source_pack_version, ontology_profile_version, and run_id.",
  },
];

export const databricksNeo4jExplanation = [
  {
    title: "Neo4j is the live memory",
    detail:
      "Neo4j stores the operational conflict graph: actors, events, interests, norms, evidence, power, trust, narratives, and reasoning traces. It is optimized for connected questions like who influenced whom, what caused escalation, which norms were violated, and what evidence supports each claim.",
  },
  {
    title: "Databricks is the analytical engine",
    detail:
      "Databricks snapshots graph data into Delta tables, applies AI extraction with ai_query, computes quality signals, creates review queues, and runs benchmark comparisons at scale. It is the repeatable lab where we test whether TACITUS improves conflict reasoning.",
  },
  {
    title: "DIALECTICA is the contract",
    detail:
      "The TACITUS ontology forces every extraction into a typed structure: 15 node types and 20 relationship types. This prevents free-form summaries from becoming the source of truth and makes errors inspectable, reviewable, and fixable.",
  },
  {
    title: "The benchmark proves the value",
    detail:
      "We compare a baseline LLM against a graph-grounded TACITUS answer on commitment tracking, causality, interest separation, narrative drift, and policy constraints. The target is higher provenance, better causal precision, and fewer unsupported claims.",
  },
];

export const ahaWorkflows = [
  {
    name: "Book to Conflict Graph",
    steps:
      "Romeo and Juliet -> chunks -> Databricks AI extraction -> ontology candidates -> Neo4j situation graph -> graph quality review.",
    value: "Shows how unstructured text becomes a computable conflict model.",
  },
  {
    name: "Human Friction Review Queue",
    steps:
      "Low-confidence edges, missing evidence, orphan nodes, and unresolved contradictions become analyst review items.",
    value: "Turns AI uncertainty into a concrete workflow instead of hiding it in prose.",
  },
  {
    name: "Baseline vs DIALECTICA Benchmark",
    steps:
      "Ask the same hard question to a plain LLM and a graph-grounded TACITUS prompt, then score both.",
    value: "Measures whether neurosymbolic structure improves conflict reasoning.",
  },
  {
    name: "Policy Constraint Mapping",
    steps:
      "Extract actors, norms, constraints, interests, violations, and viable processes from policy documents.",
    value: "Extends the same graph backbone from interpersonal conflict to governance and policy design.",
  },
];

export const benchmarkScenarios = [
  {
    id: "commitment-tracking",
    title: "Commitment Tracking",
    domain: "Workplace",
    question: "Was there a commitment on content ownership, when was it made, and who later contested it?",
    input:
      "Sam: So we're agreed - you own the Q4 launch deck content, I handle design. Lock it in by Thursday? Alex: Sounds good. I'll pick it up after the Jenkins pitch. Alex later says: I never said I'd own it. Just help.",
    baselineAnswer:
      "Alex seems to have agreed to help with the launch deck, but the commitment is ambiguous and later disputed.",
    dialecticaAnswer:
      "DIALECTICA creates Actor nodes for Sam and Alex, a Commitment/Issue object for Q4 launch deck ownership, ASSERTED/ACKNOWLEDGED_AMBIGUOUSLY/DENIES_SCOPE-style benchmark edges, and evidence spans for each message. The graph-grounded answer is: Sam asserted content ownership, Alex ambiguously accepted, and Alex later contested the scope.",
    scores: {
      baseline: { provenance: 0.45, causality: 0.35, graph: 0.4, ambiguity: 0.55 },
      dialectica: { provenance: 0.92, causality: 0.74, graph: 0.88, ambiguity: 0.9 },
    },
  },
  {
    id: "policy-constraints",
    title: "Policy Constraint Extraction",
    domain: "Policy",
    question: "Which constraints shape the feasible policy options?",
    input:
      "The agency can reallocate emergency funds only after committee notice. The mayor wants immediate shelter expansion, while the finance office warns that state matching funds expire if reporting is late.",
    baselineAnswer:
      "The agency faces budget constraints, timing issues, and reporting requirements.",
    dialecticaAnswer:
      "DIALECTICA separates Actors (agency, mayor, finance office), Norms (committee notice, matching-fund reporting), Interests (rapid shelter expansion, preserving funds), and Process constraints. The graph answer identifies which rule governs which action and which actor is constrained.",
    scores: {
      baseline: { provenance: 0.5, causality: 0.48, graph: 0.35, ambiguity: 0.52 },
      dialectica: { provenance: 0.89, causality: 0.82, graph: 0.86, ambiguity: 0.84 },
    },
  },
  {
    id: "causal-escalation",
    title: "Causal Escalation Chain",
    domain: "Diplomatic",
    question: "Identify the plausible escalation chain and evidence for each step.",
    input:
      "After the inspection delay, State A suspended talks. State B announced reciprocal tariffs. Regional partners then postponed the summit, citing uncertainty.",
    baselineAnswer:
      "The escalation likely went from inspection delay to suspended talks, then tariffs, then postponed summit.",
    dialecticaAnswer:
      "DIALECTICA distinguishes temporal order from CAUSED edges: inspection delay -> suspended talks, suspended talks -> reciprocal tariffs, uncertainty around tariffs/talks -> postponed summit. Each edge is stored with confidence and source quote, so analysts can accept, reject, or downgrade causal claims.",
    scores: {
      baseline: { provenance: 0.58, causality: 0.62, graph: 0.42, ambiguity: 0.46 },
      dialectica: { provenance: 0.9, causality: 0.88, graph: 0.84, ambiguity: 0.8 },
    },
  },
];

export const situationPortalBlueprint = [
  {
    stage: "Ingest",
    operatorView: "Choose a source pack: book, policy memo, transcript, complaint, report, or case file.",
    graphView: "Document, Chunk, Evidence, Workspace, Project, User.",
    databricksView: "Delta raw_text_chunks with source IDs, chunk IDs, tenant IDs, and workspace IDs.",
  },
  {
    stage: "Structure",
    operatorView: "Run TACITUS ontology extraction and inspect candidate nodes/edges before graph writeback.",
    graphView: "Actor, Conflict, Event, Issue, Interest, Norm, Process, Outcome, Narrative, PowerDynamic.",
    databricksView: "ai_extraction_candidates with JSON, confidence, model endpoint, extractor, and timestamp.",
  },
  {
    stage: "Validate",
    operatorView: "See missing evidence, low-confidence relationships, orphan nodes, causal ambiguity, and review priority.",
    graphView: "ReviewDecision, OperationalSignal, ReasoningTrace, InferredFact.",
    databricksView: "review_queue, graph_quality_signals, actor_features.",
  },
  {
    stage: "Query",
    operatorView: "Ask hard questions about causality, power, interests, norms, trust, and policy constraints.",
    graphView: "Allowlisted Cypher, GraphRAG context, provenance-backed answers.",
    databricksView: "SQL tables and benchmark outputs for repeatable evaluation.",
  },
  {
    stage: "Benchmark",
    operatorView: "Compare traditional LLM answers against DIALECTICA graph-grounded answers.",
    graphView: "Typed subgraph overlap, provenance, contradiction, causal chain, narrative drift.",
    databricksView: "benchmark_items, benchmark_prompts, benchmark_answers, benchmark_judgments.",
  },
];

export const dynamicOntologyTables = [
  {
    table: "ontology_profile_coverage",
    purpose: "Shows whether a workspace has enough Actor, Event, Norm, Interest, Trust, Power, and Narrative coverage for each use-case profile.",
  },
  {
    table: "source_reliability_signals",
    purpose: "Tracks source type, trust level, candidate volume, and extraction freshness.",
  },
  {
    table: "temporal_event_signals",
    purpose: "Measures event/process/outcome density and temporal relationship coverage.",
  },
  {
    table: "claim_review_queue",
    purpose: "Turns weak evidence, low confidence, and audit samples into concrete human review tasks.",
  },
];

export const ontologyProfileOptions = [
  {
    id: "human-friction",
    label: "Human Friction",
    objective: "Understand commitments, trust, emotions, power, contested scope, and repair opportunities.",
    requiredNodes: ["Actor", "Issue", "Interest", "EmotionalState", "TrustState", "PowerDynamic", "Process"],
    requiredEdges: ["PARTY_TO", "HAS_INTEREST", "EXPERIENCES", "TRUSTS", "HAS_POWER_OVER", "RESOLVED_THROUGH"],
    questions: [
      "What was explicitly promised?",
      "Who later contested the scope?",
      "What trust repair would change the next interaction?",
    ],
  },
  {
    id: "literary-conflict",
    label: "Literary Conflict",
    objective: "Ask deterministic questions about characters, scenes, motives, alliances, turning points, and tragic escalation.",
    requiredNodes: ["Actor", "Event", "Narrative", "Location", "EmotionalState", "ConflictPhase"],
    requiredEdges: ["PARTICIPATES_IN", "CAUSED", "PROMOTES", "AT_LOCATION", "EXPERIENCES", "OPPOSED_TO"],
    questions: [
      "Which events changed the conflict phase?",
      "Which characters promote which narrative?",
      "What evidence supports the causal turning point?",
    ],
  },
  {
    id: "policy-analysis",
    label: "Policy Analysis",
    objective: "Map actors, jurisdictions, constraints, norms, interests, veto players, and implementation risks.",
    requiredNodes: ["Actor", "Norm", "Interest", "Process", "Outcome", "Evidence", "Location"],
    requiredEdges: ["GOVERNED_BY", "VIOLATES", "HAS_INTEREST", "MEMBER_OF", "PRODUCES", "EVIDENCED_BY"],
    questions: [
      "Which rules bind which actors?",
      "Who has veto power or implementation leverage?",
      "Which constraints are legal, financial, temporal, or political?",
    ],
  },
  {
    id: "mediation-resolution",
    label: "Mediation / Resolution",
    objective: "Generate intervention insight: interests vs positions, ripeness, process options, guarantees, and next questions.",
    requiredNodes: ["Actor", "Interest", "Process", "Outcome", "TrustState", "PowerDynamic", "Role"],
    requiredEdges: ["HAS_INTEREST", "RESOLVED_THROUGH", "PRODUCES", "TRUSTS", "HAS_POWER_OVER", "PARTICIPATES_IN"],
    questions: [
      "What interests are separable from stated positions?",
      "What process option is viable now?",
      "What guarantee would reduce perceived risk?",
    ],
  },
];

export const agenticTools = [
  {
    name: "Source Scout",
    runSurface: "Databricks ingestion",
    purpose: "Finds and chunks books, memos, transcripts, reports, or user-uploaded material with source trust metadata.",
  },
  {
    name: "Ontology Builder",
    runSurface: "Frontend + Databricks",
    purpose: "Chooses an ontology profile from use case, objective, user role, question type, and source mix.",
  },
  {
    name: "Claim Verifier",
    runSurface: "Delta + Neo4j",
    purpose: "Ranks claims by confidence, evidence strength, source trust, contradiction risk, and review priority.",
  },
  {
    name: "Temporal Analyst",
    runSurface: "Databricks quality job",
    purpose: "Separates chronology from causality and detects conflict phase transitions.",
  },
  {
    name: "GraphRAG Planner",
    runSurface: "Neo4j query API",
    purpose: "Turns user questions into safe graph traversals plus context packs for an LLM.",
  },
  {
    name: "Benchmark Judge",
    runSurface: "Databricks benchmark",
    purpose: "Compares baseline LLM answers with graph-grounded answers using provenance, graph overlap, and causal precision.",
  },
];

export const ambitionRoadmap = [
  {
    horizon: "Now",
    goal: "Operator console for Databricks + Neo4j graph creation and benchmark demos.",
    proof: "Public-domain books become Delta candidates; protected frontend shows jobs, ontology, queries, and benchmark comparisons.",
  },
  {
    horizon: "Next",
    goal: "Neo4j writeback and live graph visualizations from real extracted data.",
    proof: "Databricks writes accepted candidates to Neo4j, then snapshots graph quality and review queues.",
  },
  {
    horizon: "After",
    goal: "Situation portals for specific conflicts, teams, policy questions, and negotiations.",
    proof: "Each portal has sources, actors, interests, norms, causal chains, trust/power maps, and benchmarked answer quality.",
  },
  {
    horizon: "Publication",
    goal: "Show that neurosymbolic conflict intelligence beats plain LLM reasoning.",
    proof: "Benchmarks report graph overlap, provenance F1, causal precision, and contradiction handling.",
  },
];

export const demoGraph: GraphData = {
  nodes: [
    {
      id: "conflict_ravenna",
      label: "Conflict",
      node_type: "conflict",
      name: "Ravenna Port Strike",
      confidence: 0.94,
      properties: { glasl_stage: 5, status: "escalating", centrality: 0.95 },
    },
    {
      id: "actor_union",
      label: "Actor",
      node_type: "actor",
      name: "Dockworkers Union",
      confidence: 0.92,
      properties: { actor_type: "organization", centrality: 0.86 },
    },
    {
      id: "actor_port",
      label: "Actor",
      node_type: "actor",
      name: "Port Authority",
      confidence: 0.93,
      properties: { actor_type: "organization", centrality: 0.82 },
    },
    {
      id: "actor_mediator",
      label: "Actor",
      node_type: "actor",
      name: "Labor Mediator",
      confidence: 0.88,
      properties: { actor_type: "person", centrality: 0.55 },
    },
    {
      id: "event_walkout",
      label: "Event",
      node_type: "event",
      name: "Night-shift walkout",
      confidence: 0.9,
      properties: { severity: 0.76, occurred_at: "2026-04-18", centrality: 0.7 },
    },
    {
      id: "event_lockout",
      label: "Event",
      node_type: "event",
      name: "Gate access suspended",
      confidence: 0.86,
      properties: { severity: 0.81, occurred_at: "2026-04-19", centrality: 0.72 },
    },
    {
      id: "interest_safety",
      label: "Interest",
      node_type: "interest",
      name: "Fatigue safety",
      confidence: 0.89,
      properties: { priority: "high", centrality: 0.45 },
    },
    {
      id: "norm_contract",
      label: "Norm",
      node_type: "norm",
      name: "Collective agreement",
      confidence: 0.87,
      properties: { centrality: 0.42 },
    },
    {
      id: "emotion_anger",
      label: "EmotionalState",
      node_type: "emotional_state",
      name: "Anger and humiliation",
      confidence: 0.78,
      properties: { intensity: 0.82, valence: -0.7, centrality: 0.36 },
    },
    {
      id: "trust_low",
      label: "TrustState",
      node_type: "trust_state",
      name: "Low institutional trust",
      confidence: 0.8,
      properties: { overall: 0.22, centrality: 0.38 },
    },
    {
      id: "process_mediation",
      label: "Process",
      node_type: "process",
      name: "Emergency mediation",
      confidence: 0.84,
      properties: { status: "proposed", centrality: 0.48 },
    },
    {
      id: "evidence_minutes",
      label: "Evidence",
      node_type: "evidence",
      name: "Meeting minutes excerpt",
      confidence: 0.91,
      properties: { reliability: 0.88, centrality: 0.34 },
    },
  ],
  links: [
    { id: "e1", source: "actor_union", target: "conflict_ravenna", edge_type: "PARTY_TO", weight: 0.92, confidence: 0.94 },
    { id: "e2", source: "actor_port", target: "conflict_ravenna", edge_type: "PARTY_TO", weight: 0.92, confidence: 0.94 },
    { id: "e3", source: "event_walkout", target: "conflict_ravenna", edge_type: "PART_OF", weight: 0.72, confidence: 0.9 },
    { id: "e4", source: "event_lockout", target: "conflict_ravenna", edge_type: "PART_OF", weight: 0.78, confidence: 0.87 },
    { id: "e5", source: "event_walkout", target: "event_lockout", edge_type: "CAUSED", weight: 0.7, confidence: 0.75 },
    { id: "e6", source: "actor_union", target: "interest_safety", edge_type: "HAS_INTEREST", weight: 0.8, confidence: 0.89 },
    { id: "e7", source: "conflict_ravenna", target: "norm_contract", edge_type: "GOVERNED_BY", weight: 0.68, confidence: 0.86 },
    { id: "e8", source: "event_lockout", target: "norm_contract", edge_type: "VIOLATES", weight: 0.56, confidence: 0.66 },
    { id: "e9", source: "actor_port", target: "actor_union", edge_type: "HAS_POWER_OVER", weight: 0.76, confidence: 0.8 },
    { id: "e10", source: "actor_union", target: "emotion_anger", edge_type: "EXPERIENCES", weight: 0.67, confidence: 0.78 },
    { id: "e11", source: "actor_union", target: "actor_port", edge_type: "TRUSTS", weight: 0.22, confidence: 0.8 },
    { id: "e12", source: "conflict_ravenna", target: "process_mediation", edge_type: "RESOLVED_THROUGH", weight: 0.46, confidence: 0.84 },
    { id: "e13", source: "actor_mediator", target: "event_lockout", edge_type: "PARTICIPATES_IN", weight: 0.44, confidence: 0.79 },
    { id: "e14", source: "event_lockout", target: "evidence_minutes", edge_type: "EVIDENCED_BY", weight: 0.9, confidence: 0.91 },
  ],
};
