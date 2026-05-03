"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { api } from "@/lib/api";
import type { GraphData } from "@/types/graph";
import { ActFrame } from "./primitives/ActFrame";
import { DemoModeBanner } from "./primitives/DemoModeBanner";
import { EventLogDrawer } from "./primitives/EventLogDrawer";
import { loadReplay, playReplay } from "./primitives/ReplayDriver";
import type { DemoMode, PipelineEvent } from "./primitives/types";
import { DOORS, type DemoDoor } from "./data/doors";
import { narratorFor, ACT_TITLES } from "./data/narratorScripts";
import { REPLAY_METADATA } from "./data/replayMetadata";
import { Act00MissionFraming } from "./act00_MissionFraming";
import { Act01ThreeDoors } from "./act01_ThreeDoors";
import { Act02SourceReveal } from "./act02_SourceReveal";
import { Act03Chunking } from "./act03_Chunking";
import { Act04GlinerPrefilter } from "./act04_GlinerPrefilter";
import { Act05GeminiExtraction } from "./act05_GeminiExtraction";
import { Act06ValidationRepair } from "./act06_ValidationRepair";
import { Act07Coreference } from "./act07_Coreference";
import { Act08Relationships } from "./act08_Relationships";
import { Act09EmbeddingProjection } from "./act09_EmbeddingProjection";
import { Act10GraphMaterialised } from "./act10_GraphMaterialised";
import { Act11Handoff } from "./act11_Handoff";

const EMPTY_GRAPH: GraphData = { nodes: [], links: [] };
const LISTENED_EVENTS = ["ready", "started", "complete", "failed", "info", "job"] as const;

export function DemoConductor() {
  const [act, setAct] = useState(0);
  const [door, setDoor] = useState<DemoDoor | null>(null);
  const [mode, setMode] = useState<DemoMode>("idle");
  const [modeDetail, setModeDetail] = useState("");
  const [sourceText, setSourceText] = useState("");
  const [events, setEvents] = useState<PipelineEvent[]>([]);
  const [graph, setGraph] = useState<GraphData>(EMPTY_GRAPH);
  const [paused, setPaused] = useState(false);
  const [logOpen, setLogOpen] = useState(false);
  const cleanupRef = useRef<(() => void) | null>(null);

  const appendEvent = useCallback((event: PipelineEvent) => {
    setEvents((prev) => [...prev, event]);
    if (event.graph) setGraph(event.graph);
  }, []);

  const latestCounts = useMemo(() => {
    const byStep = new Map<string, Record<string, number>>();
    for (const event of events) {
      if (event.counts) byStep.set(event.step, event.counts);
    }
    return byStep;
  }, [events]);

  const runReplay = useCallback(
    async (selected: DemoDoor, reason: string) => {
      cleanupRef.current?.();
      setMode("replay");
      setModeDetail(`${reason} Captured ${REPLAY_METADATA[selected.id].capturedAt}.`);
      const frames = await loadReplay(selected.replayPath);
      cleanupRef.current = playReplay(frames, appendEvent);
    },
    [appendEvent],
  );

  const startScenario = useCallback(
    async (selected: DemoDoor) => {
      cleanupRef.current?.();
      setDoor(selected);
      setAct(2);
      setEvents([]);
      setGraph(EMPTY_GRAPH);
      setMode("idle");
      setModeDetail("");

      try {
        if (selected.ingestKind === "text" && "text_path" in selected.ingestParams) {
          const text = await fetch(selected.ingestParams.text_path).then((res) => res.text());
          setSourceText(text.slice(0, 6000));
        } else {
          setSourceText(`${selected.sourceTitle}\n\nLive extraction will fetch the public-domain text through the API.`);
        }

        let jobId = "";
        if (selected.ingestKind === "gutenberg" && "book_id" in selected.ingestParams) {
          const result = await api.ingestGutenberg(selected.workspaceId, selected.ingestParams);
          jobId = result.job_id;
        } else if ("tier" in selected.ingestParams) {
          const text = await fetch((selected.ingestParams as { text_path: string }).text_path).then((res) =>
            res.text(),
          );
          const result = (await api.extract({
            workspace_id: selected.workspaceId,
            text,
            tier: selected.ingestParams.tier === "lite" ? "essential" : selected.ingestParams.tier,
          })) as unknown as { job_id?: string; id?: string };
          jobId = result.job_id ?? result.id ?? "";
        }

        if (!jobId) throw new Error("Extraction did not return a job id.");
        setMode("live");
        setModeDetail(`Job ${jobId}.`);
        const source = api.streamExtraction(selected.workspaceId, jobId);
        const handler = (raw: Event) => {
          const message = raw as MessageEvent<string>;
          const parsed = JSON.parse(message.data) as PipelineEvent;
          if (parsed.job) {
            appendEvent({ job_id: jobId, step: "job", status: String(parsed.job.status), job: parsed.job });
            void api
              .getGraph(selected.workspaceId)
              .then((data) =>
                setGraph({
                  nodes: data.nodes.map((node) => ({
                    id: node.id,
                    label: node.label ?? node.type,
                    node_type: (node.type ?? node.label) as never,
                    name: String(node.properties?.name ?? node.id),
                    confidence: Number(node.properties?.confidence ?? 0.8),
                    properties: node.properties ?? {},
                  })),
                  links: data.edges.map((edge) => ({
                    id: edge.id ?? `${edge.source}-${edge.target}-${edge.type}`,
                    source: edge.source,
                    target: edge.target,
                    edge_type: edge.type,
                    weight: edge.weight ?? 1,
                    confidence: Number(edge.properties?.confidence ?? 0.8),
                  })),
                }),
              )
              .catch(() => undefined);
            return;
          }
          appendEvent(parsed);
        };
        LISTENED_EVENTS.forEach((name) => source.addEventListener(name, handler));
        source.onerror = () => {
          source.close();
          void runReplay(selected, "Live stream disconnected.");
        };
        cleanupRef.current = () => source.close();
      } catch (error) {
        await runReplay(selected, error instanceof Error ? error.message : "Live API unavailable.");
      }
    },
    [appendEvent, runReplay],
  );

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "ArrowRight") setAct((value) => Math.min(11, value + 1));
      if (event.key === "ArrowLeft") setAct((value) => Math.max(0, value - 1));
      if (event.key === " ") setPaused((value) => !value);
      if (event.key.toLowerCase() === "l") setLogOpen((value) => !value);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  useEffect(() => {
    if (paused || act < 2 || act >= 11) return;
    const timer = window.setTimeout(() => setAct((value) => Math.min(11, value + 1)), 6500);
    return () => window.clearTimeout(timer);
  }, [act, paused, events.length]);

  useEffect(() => () => cleanupRef.current?.(), []);

  const counts = {
    chunks: latestCounts.get("chunk_document")?.chunks ?? 0,
    density: latestCounts.get("gliner_prefilter")?.entity_density_avg ?? 0,
    raw: latestCounts.get("extract_entities")?.entities_raw ?? 0,
    valid: latestCounts.get("validate_schema")?.entities_valid ?? 0,
    invalid: latestCounts.get("validate_schema")?.entities_invalid ?? 0,
    merged: latestCounts.get("resolve_coreference")?.merged_pairs ?? 0,
    edges: latestCounts.get("extract_relationships")?.edges_valid ?? 0,
    nodesWritten: latestCounts.get("write_to_graph")?.nodes_written ?? 0,
    edgesWritten: latestCounts.get("write_to_graph")?.edges_written ?? 0,
  };

  const body = renderAct({
    act,
    door,
    sourceText,
    counts,
    graph,
    onShow: () => setAct(1),
    onPick: startScenario,
    onReset: () => {
      cleanupRef.current?.();
      setDoor(null);
      setMode("idle");
      setEvents([]);
      setAct(1);
    },
  });

  return (
    <>
      <DemoModeBanner mode={mode} detail={modeDetail} />
      <ActFrame
        act={act}
        title={ACT_TITLES[act] ?? "Demo"}
        caption={narratorFor(door?.id ?? null, act)}
        paused={paused}
        onNext={() => setAct((value) => Math.min(11, value + 1))}
        onPrev={() => setAct((value) => Math.max(0, value - 1))}
        onTogglePause={() => setPaused((value) => !value)}
        onToggleLog={() => setLogOpen((value) => !value)}
      >
        {body}
      </ActFrame>
      <EventLogDrawer open={logOpen} events={events} onClose={() => setLogOpen(false)} />
    </>
  );
}

function renderAct(args: {
  act: number;
  door: DemoDoor | null;
  sourceText: string;
  counts: {
    chunks: number;
    density: number;
    raw: number;
    valid: number;
    invalid: number;
    merged: number;
    edges: number;
    nodesWritten: number;
    edgesWritten: number;
  };
  graph: GraphData;
  onShow: () => void;
  onPick: (door: DemoDoor) => void;
  onReset: () => void;
}) {
  if (args.act === 0) return <Act00MissionFraming onShow={args.onShow} />;
  if (args.act === 1) return <Act01ThreeDoors onPick={args.onPick} />;
  if (args.act === 2) return <Act02SourceReveal door={args.door} sourceText={args.sourceText} />;
  if (args.act === 3) return <Act03Chunking chunks={args.counts.chunks} />;
  if (args.act === 4) return <Act04GlinerPrefilter chunks={args.counts.chunks} avgDensity={args.counts.density} />;
  if (args.act === 5) return <Act05GeminiExtraction rawEntities={args.counts.raw} />;
  if (args.act === 6) return <Act06ValidationRepair valid={args.counts.valid} invalid={args.counts.invalid} />;
  if (args.act === 7) return <Act07Coreference mergedPairs={args.counts.merged} />;
  if (args.act === 8) return <Act08Relationships edges={args.counts.edges} />;
  if (args.act === 9) return <Act09EmbeddingProjection nodes={args.counts.valid} />;
  if (args.act === 10)
    return (
      <Act10GraphMaterialised
        graph={args.graph}
        nodesWritten={args.counts.nodesWritten}
        edgesWritten={args.counts.edgesWritten}
      />
    );
  return <Act11Handoff door={args.door ?? DOORS[0]} onReset={args.onReset} />;
}
