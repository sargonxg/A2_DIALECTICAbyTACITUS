"use client";

import { PipelineMonitor } from "@/components/admin/PipelineMonitor";
import { GitBranch, Info } from "lucide-react";

export default function ExtractionPage() {
  return (
    <div className="p-8 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-[#fafafa] mb-1">Extraction Pipeline</h1>
        <p className="text-[#a1a1aa] text-sm">
          Monitor NLP extraction jobs: entity detection, relation extraction, escalation scoring.
        </p>
      </div>

      {/* Pipeline info banner */}
      <div className="flex items-start gap-3 p-4 bg-[#18181b] border border-[#27272a] rounded-lg mb-6">
        <Info size={15} className="text-teal-500 flex-shrink-0 mt-0.5" />
        <div>
          <p className="text-[#fafafa] text-sm font-medium mb-1">About the Extraction Pipeline</p>
          <p className="text-[#71717a] text-xs leading-relaxed">
            DIALECTICA ingests raw conflict documents and runs them through a multi-stage NLP pipeline:
            (1) entity extraction for actors, positions, issues; (2) relation detection to build edges;
            (3) escalation scoring using the Glasl model; (4) trust graph construction.
            Jobs shown below are read from the pipeline queue. Refresh to see updates.
          </p>
        </div>
      </div>

      {/* Pipeline stages */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-8">
        {[
          { step: "1", label: "Entity Extraction", desc: "Actors, issues, positions, events" },
          { step: "2", label: "Relation Detection", desc: "Stance, trust, power, alliances" },
          { step: "3", label: "Escalation Scoring", desc: "Glasl stage + trajectory" },
          { step: "4", label: "Graph Build", desc: "Neo4j / Memgraph ingestion" },
        ].map((s) => (
          <div key={s.step} className="bg-[#18181b] border border-[#27272a] rounded-lg p-3">
            <div className="flex items-center gap-2 mb-1">
              <span className="w-5 h-5 rounded-full bg-teal-600/20 border border-teal-600/30 text-teal-400 text-xs flex items-center justify-center font-mono flex-shrink-0">
                {s.step}
              </span>
              <p className="text-[#fafafa] text-xs font-medium">{s.label}</p>
            </div>
            <p className="text-[#52525b] text-xs">{s.desc}</p>
          </div>
        ))}
      </div>

      <PipelineMonitor />
    </div>
  );
}
