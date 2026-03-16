"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import QueryInput from "@/components/query/QueryInput";
import QueryResult from "@/components/query/QueryResult";
import ReasoningTrace from "@/components/query/ReasoningTrace";
import { useAnalysis } from "@/hooks/useReasoning";
import type { AnalysisMode, AnalysisResult } from "@/types/api";
import type { ReasoningStep } from "@/types/analysis";

export default function AnalysisPage() {
  const { id } = useParams();
  const [results, setResults] = useState<AnalysisResult[]>([]);
  const analysis = useAnalysis();

  const handleSubmit = async (query: string, mode: AnalysisMode) => {
    const result = await analysis.mutateAsync({
      workspace_id: id as string,
      query,
      mode,
      include_theory: true,
    });
    setResults((prev) => [result, ...prev]);
  };

  return (
    <div className="flex gap-4 h-[calc(100vh-14rem)]">
      {/* Chat panel */}
      <div className="flex-1 flex flex-col">
        <div className="flex-1 overflow-y-auto space-y-4 mb-4">
          {results.length === 0 && (
            <div className="text-center py-16">
              <p className="text-text-secondary">Ask a question about this conflict to get started.</p>
            </div>
          )}
          {results.map((r, i) => (
            <QueryResult key={i} result={r} />
          ))}
        </div>
        <QueryInput onSubmit={handleSubmit} loading={analysis.isPending} />
      </div>

      {/* Context panel */}
      <div className="w-80 flex-shrink-0 overflow-y-auto space-y-4">
        <div className="card">
          <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wider mb-2">Analysis Context</h3>
          <p className="text-sm text-text-secondary">Select a query mode and ask questions. Results include evidence and theory-grounded insights.</p>
        </div>
      </div>
    </div>
  );
}
