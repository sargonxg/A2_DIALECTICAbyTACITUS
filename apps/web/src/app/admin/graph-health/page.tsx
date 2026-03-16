"use client";

import { Heart, CheckCircle } from "lucide-react";

export default function GraphHealthPage() {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-text-primary flex items-center gap-2"><Heart size={20} /> Graph Health</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card"><p className="text-text-secondary text-xs mb-1">Total Nodes</p><p className="text-2xl font-mono font-bold text-text-primary">0</p></div>
        <div className="card"><p className="text-text-secondary text-xs mb-1">Total Edges</p><p className="text-2xl font-mono font-bold text-text-primary">0</p></div>
        <div className="card"><p className="text-text-secondary text-xs mb-1">Orphan Nodes</p><p className="text-2xl font-mono font-bold text-success">0</p></div>
      </div>
      <div className="card flex items-center gap-2">
        <CheckCircle size={16} className="text-success" />
        <span className="text-sm text-text-primary">Graph consistency: All checks passed</span>
      </div>
    </div>
  );
}
