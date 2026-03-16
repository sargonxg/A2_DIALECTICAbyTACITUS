"use client";

import { useRef, useState } from "react";
import {
  Upload,
  Download,
  Database,
  CheckCircle2,
  XCircle,
  Loader2,
  FileJson,
} from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

const SAMPLE_WORKSPACES = [
  {
    id: "jcpoa-2015",
    name: "JCPOA Nuclear Negotiations",
    domain: "diplomatic",
    scale: "international",
    description: "Iran nuclear deal multilateral negotiations (2013–2015)",
  },
  {
    id: "hr-mediation-2023",
    name: "HR Workplace Mediation",
    domain: "organizational",
    scale: "interpersonal",
    description: "HR conflict mediation case study with trust breakdown",
  },
  {
    id: "commercial-dispute-2024",
    name: "Commercial Contract Dispute",
    domain: "commercial",
    scale: "organizational",
    description: "Cross-border commercial arbitration with power asymmetry",
  },
];

interface Props {
  workspaceId?: string;
}

type OpState = "idle" | "loading" | "success" | "error";

function StatusBadge({ state, message }: { state: OpState; message?: string }) {
  if (state === "idle") return null;
  if (state === "loading")
    return (
      <span className="flex items-center gap-1.5 text-[#71717a] text-xs">
        <Loader2 size={12} className="animate-spin" /> Processing…
      </span>
    );
  if (state === "success")
    return (
      <span className="flex items-center gap-1.5 text-green-400 text-xs">
        <CheckCircle2 size={12} /> {message || "Done"}
      </span>
    );
  return (
    <span className="flex items-center gap-1.5 text-red-400 text-xs">
      <XCircle size={12} /> {message || "Error"}
    </span>
  );
}

export function DataImportExport({ workspaceId }: Props) {
  const fileRef = useRef<HTMLInputElement>(null);
  const [importState, setImportState] = useState<OpState>("idle");
  const [importMsg, setImportMsg] = useState("");
  const [exportState, setExportState] = useState<OpState>("idle");
  const [seedStates, setSeedStates] = useState<Record<string, OpState>>({});
  const [selectedWorkspace, setSelectedWorkspace] = useState(workspaceId || "");

  function getApiKey() {
    return typeof window !== "undefined"
      ? localStorage.getItem("dialectica_api_key") || ""
      : "";
  }

  async function handleImport(file: File) {
    if (!selectedWorkspace) {
      setImportMsg("Select a workspace ID first");
      setImportState("error");
      return;
    }
    setImportState("loading");
    try {
      const text = await file.text();
      const body = JSON.parse(text);
      const res = await fetch(
        `${API_URL}/v1/workspaces/${selectedWorkspace}/import`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-API-Key": getApiKey(),
          },
          body: JSON.stringify(body),
        },
      );
      if (!res.ok) {
        const msg = await res.text().catch(() => res.statusText);
        throw new Error(msg);
      }
      setImportMsg(`Imported ${file.name}`);
      setImportState("success");
    } catch (err) {
      setImportMsg(err instanceof Error ? err.message : "Import failed");
      setImportState("error");
    }
  }

  async function handleExport() {
    if (!selectedWorkspace) {
      setExportState("error");
      return;
    }
    setExportState("loading");
    try {
      const res = await fetch(
        `${API_URL}/v1/workspaces/${selectedWorkspace}/export`,
        {
          headers: { "X-API-Key": getApiKey() },
        },
      );
      if (!res.ok) throw new Error(res.statusText);
      const data = await res.json();
      const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: "application/json",
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${selectedWorkspace}-graph.json`;
      a.click();
      URL.revokeObjectURL(url);
      setExportState("success");
    } catch (err) {
      setExportState("error");
    }
  }

  async function handleSeed(ws: (typeof SAMPLE_WORKSPACES)[0]) {
    setSeedStates((s) => ({ ...s, [ws.id]: "loading" }));
    try {
      // Create workspace
      const createRes = await fetch(`${API_URL}/v1/workspaces`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": getApiKey(),
        },
        body: JSON.stringify({
          name: ws.name,
          domain: ws.domain,
          scale: ws.scale,
        }),
      });
      if (!createRes.ok) throw new Error(await createRes.text());
      setSeedStates((s) => ({ ...s, [ws.id]: "success" }));
    } catch {
      setSeedStates((s) => ({ ...s, [ws.id]: "error" }));
    }
  }

  return (
    <div className="space-y-6">
      {/* Workspace selector */}
      <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-5">
        <h3 className="text-[#fafafa] text-sm font-semibold mb-3">Target Workspace</h3>
        <input
          type="text"
          value={selectedWorkspace}
          onChange={(e) => setSelectedWorkspace(e.target.value)}
          placeholder="workspace-id (e.g. jcpoa-2015)"
          className="w-full bg-[#09090b] border border-[#27272a] rounded-md px-3 py-2 text-sm text-[#fafafa] placeholder-[#52525b] font-mono focus:outline-none focus:border-teal-600"
        />
      </div>

      {/* Import */}
      <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-5">
        <div className="flex items-center gap-2 mb-3">
          <Upload size={16} className="text-[#71717a]" />
          <h3 className="text-[#fafafa] text-sm font-semibold">Import Graph Data</h3>
        </div>
        <p className="text-[#71717a] text-xs mb-4">
          Upload a JSON file containing nodes and edges for the selected workspace.
          Format: <code className="text-[#a1a1aa] font-mono">{"{ nodes: [...], edges: [...] }"}</code>
        </p>
        <input
          ref={fileRef}
          type="file"
          accept=".json,application/json"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) handleImport(file);
          }}
        />
        <div className="flex items-center gap-3">
          <button
            onClick={() => fileRef.current?.click()}
            disabled={importState === "loading"}
            className="flex items-center gap-2 px-4 py-2 rounded-md bg-[#27272a] hover:bg-[#3f3f46] text-[#fafafa] text-sm transition-colors disabled:opacity-50"
          >
            <FileJson size={14} />
            Choose JSON File
          </button>
          <StatusBadge state={importState} message={importMsg} />
        </div>
      </div>

      {/* Export */}
      <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-5">
        <div className="flex items-center gap-2 mb-3">
          <Download size={16} className="text-[#71717a]" />
          <h3 className="text-[#fafafa] text-sm font-semibold">Export Graph Data</h3>
        </div>
        <p className="text-[#71717a] text-xs mb-4">
          Download the full graph for the selected workspace as JSON.
        </p>
        <div className="flex items-center gap-3">
          <button
            onClick={handleExport}
            disabled={exportState === "loading" || !selectedWorkspace}
            className="flex items-center gap-2 px-4 py-2 rounded-md bg-teal-600/20 hover:bg-teal-600/30 border border-teal-600/30 text-teal-400 text-sm transition-colors disabled:opacity-50"
          >
            <Download size={14} />
            Export JSON
          </button>
          <StatusBadge state={exportState} />
        </div>
      </div>

      {/* Seed data */}
      <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-5">
        <div className="flex items-center gap-2 mb-1">
          <Database size={16} className="text-[#71717a]" />
          <h3 className="text-[#fafafa] text-sm font-semibold">Sample Workspaces</h3>
        </div>
        <p className="text-[#71717a] text-xs mb-4">
          Create the three built-in example workspaces. Each will be created as an empty
          workspace — use the extraction pipeline to populate with sample data.
        </p>
        <div className="space-y-3">
          {SAMPLE_WORKSPACES.map((ws) => (
            <div
              key={ws.id}
              className="flex items-center justify-between gap-4 p-3 bg-[#09090b] border border-[#27272a] rounded-md"
            >
              <div className="min-w-0">
                <p className="text-[#fafafa] text-sm font-medium truncate">{ws.name}</p>
                <p className="text-[#71717a] text-xs truncate">{ws.description}</p>
                <p className="text-[#52525b] text-xs font-mono mt-0.5">{ws.id}</p>
              </div>
              <div className="flex items-center gap-2 flex-shrink-0">
                <StatusBadge state={seedStates[ws.id] || "idle"} />
                <button
                  onClick={() => handleSeed(ws)}
                  disabled={
                    seedStates[ws.id] === "loading" ||
                    seedStates[ws.id] === "success"
                  }
                  className="px-3 py-1.5 rounded-md bg-[#27272a] hover:bg-[#3f3f46] text-[#fafafa] text-xs transition-colors disabled:opacity-50"
                >
                  {seedStates[ws.id] === "success" ? "Created" : "Load"}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
