"use client";

import { motion } from "framer-motion";
import type { CuratedReasoningQuestion } from "./types";
import { DialecticaAnswerPanel } from "./DialecticaAnswerPanel";
import { LLMComparisonPanel } from "./LLMComparisonPanel";

interface Props {
  question: CuratedReasoningQuestion;
  counterfactualActive: boolean;
  onTraceOpen: () => void;
}

export function AnswerComparison({ question, counterfactualActive, onTraceOpen }: Props) {
  return (
    <motion.div
      key={question.id}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className="grid gap-4 xl:grid-cols-2"
    >
      <LLMComparisonPanel question={question} />
      <DialecticaAnswerPanel
        question={question}
        counterfactualActive={counterfactualActive}
        onTraceOpen={onTraceOpen}
      />
    </motion.div>
  );
}
