"use client";

import { cn } from "@/lib/utils";
import { Check, Loader2 } from "lucide-react";

const STEPS = [
  "Document parsing",
  "GLiNER pre-filter",
  "Entity extraction",
  "Relationship extraction",
  "Temporal analysis",
  "Causal analysis",
  "Validation",
  "Graph commit",
];

interface Props {
  currentStep: number;
  status: "processing" | "completed" | "failed";
  error?: string;
}

export default function ExtractionProgress({ currentStep, status, error }: Props) {
  return (
    <div className="card space-y-3">
      <h3 className="font-semibold text-text-primary">Extraction Pipeline</h3>
      <div className="space-y-2">
        {STEPS.map((step, i) => {
          const done = i < currentStep;
          const active = i === currentStep && status === "processing";
          const failed = i === currentStep && status === "failed";
          return (
            <div key={step} className="flex items-center gap-3">
              <div className={cn(
                "w-6 h-6 rounded-full flex items-center justify-center text-xs",
                done ? "bg-success text-white" : active ? "bg-accent text-white" : failed ? "bg-danger text-white" : "bg-surface-hover text-text-secondary",
              )}>
                {done ? <Check size={12} /> : active ? <Loader2 size={12} className="animate-spin" /> : i + 1}
              </div>
              <span className={cn("text-sm", done ? "text-text-primary" : active ? "text-accent" : "text-text-secondary")}>{step}</span>
            </div>
          );
        })}
      </div>
      {error && <p className="text-sm text-danger mt-2">{error}</p>}
    </div>
  );
}
