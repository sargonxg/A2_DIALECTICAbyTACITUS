"use client";

import { motion } from "framer-motion";

interface Props {
  value: number;
}

export function HallucinationGauge({ value }: Props) {
  const pct = Math.round(value * 100);
  const color = value < 0.1 ? "#34d399" : value < 0.2 ? "#fbbf24" : "#fb7185";

  return (
    <div data-test="hallucination-gauge" className="min-w-[150px]" title={`Hallucination risk: ${pct}%`}>
      <div className="mb-1 flex items-center justify-between text-[11px] uppercase tracking-wide text-text-secondary">
        <span>Hallucination risk</span>
        <span className="font-mono text-text-primary">{pct}%</span>
      </div>
      <div className="h-2 rounded-full bg-surface-active">
        <motion.div
          className="h-2 rounded-full"
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.7, ease: "easeOut" }}
          style={{ backgroundColor: color }}
        />
      </div>
    </div>
  );
}
