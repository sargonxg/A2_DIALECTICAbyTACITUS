"use client";

import { motion, useReducedMotion } from "framer-motion";

export function EntityBubble({
  label,
  type,
  confidence = 0.7,
}: {
  label: string;
  type: string;
  confidence?: number;
}) {
  const reduceMotion = useReducedMotion();
  const size = 34 + confidence * 28;
  return (
    <motion.div
      initial={reduceMotion ? false : { scale: 0, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      className="flex items-center justify-center rounded-full border border-accent/40 bg-accent/10 text-center text-[11px] font-semibold text-text-primary"
      style={{ width: size, height: size, boxShadow: `0 0 0 ${confidence * 14}px rgba(56,189,248,0.08)` }}
      title={`${type} confidence ${confidence.toFixed(2)}`}
    >
      {label}
    </motion.div>
  );
}
