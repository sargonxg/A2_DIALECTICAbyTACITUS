"use client";

import { useState } from "react";
import QueryInput from "@/components/query/QueryInput";
import type { AnalysisMode } from "@/types/api";
import { Brain } from "lucide-react";

export default function AskPage() {
  const [text, setText] = useState("");
  const [result, setResult] = useState<string | null>(null);

  const handleAnalyze = (query: string, mode: AnalysisMode) => {
    setResult(`Analysis (${mode}): Processing "${query}" — This feature requires an active workspace. Go to Workspaces to create one and run analysis with full context.`);
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-text-primary flex items-center gap-2">
        <Brain size={24} /> Quick Analysis
      </h1>
      <p className="text-text-secondary">Paste conflict text for quick extraction and analysis without a workspace.</p>

      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={8}
        className="input-base w-full"
        placeholder="Paste conflict text here..."
      />

      <QueryInput onSubmit={handleAnalyze} />

      {result && (
        <div className="card">
          <p className="text-text-primary text-sm">{result}</p>
        </div>
      )}
    </div>
  );
}
