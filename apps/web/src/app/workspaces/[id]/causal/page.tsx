"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import CausalChainViz from "@/components/graph/CausalChainViz";

export default function CausalPage() {
  const { id } = useParams();
  const [pearlLevel, setPearlLevel] = useState<"association" | "intervention" | "counterfactual">("association");

  return (
    <div className="space-y-6">
      <h2 className="text-lg font-semibold text-text-primary">Causal Analysis</h2>
      <CausalChainViz
        chain={{ events: [], links: [] }}
        pearlLevel={pearlLevel}
        onPearlChange={setPearlLevel}
      />
      <div className="card text-center py-12">
        <p className="text-text-secondary">Causal chains will populate as events and causal relationships are extracted.</p>
      </div>
    </div>
  );
}
