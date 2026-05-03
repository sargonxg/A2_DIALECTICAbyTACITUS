"use client";

import { motion, useReducedMotion } from "framer-motion";
import { ChevronLeft, ChevronRight, ListTree, Pause, Play } from "lucide-react";
import { ACT_TITLES } from "../data/narratorScripts";

interface Props {
  act: number;
  title: string;
  caption: string;
  paused: boolean;
  onNext: () => void;
  onPrev: () => void;
  onTogglePause: () => void;
  onToggleLog: () => void;
  children: React.ReactNode;
}

export function ActFrame({
  act,
  title,
  caption,
  paused,
  onNext,
  onPrev,
  onTogglePause,
  onToggleLog,
  children,
}: Props) {
  const reduceMotion = useReducedMotion();
  return (
    <motion.section
      data-act={act}
      initial={reduceMotion ? false : { opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45 }}
      className="min-h-screen px-5 py-5 md:px-8"
    >
      <div className="mx-auto flex min-h-[calc(100vh-2.5rem)] max-w-7xl flex-col rounded-lg border border-border bg-surface">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border px-4 py-3">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-accent">
              Act {act} / 11
            </p>
            <h1 className="text-xl font-semibold text-text-primary">{title}</h1>
          </div>
          <div className="flex items-center gap-2">
            <button className="btn-secondary inline-flex items-center gap-2" onClick={onToggleLog}>
              <ListTree size={15} />
              Event log
            </button>
            <button className="btn-secondary inline-flex items-center gap-2" onClick={onTogglePause}>
              {paused ? <Play size={15} /> : <Pause size={15} />}
              {paused ? "Resume" : "Pause"}
            </button>
            <button className="btn-secondary" onClick={onPrev} aria-label="Previous act">
              <ChevronLeft size={16} />
            </button>
            <button
              className="btn-primary inline-flex items-center gap-2"
              onClick={onNext}
              data-test="skip-act"
            >
              Skip
              <ChevronRight size={15} />
            </button>
          </div>
        </div>

        <div className="flex gap-1 border-b border-border px-4 py-2">
          {ACT_TITLES.map((item, index) => (
            <span
              key={item}
              className={`h-1.5 flex-1 rounded-full ${index <= act ? "bg-accent" : "bg-background"}`}
              title={item}
            />
          ))}
        </div>

        <div className="grid flex-1 gap-5 p-4 xl:grid-cols-[1fr_360px]">
          <div className="min-h-[520px]">{children}</div>
          <aside className="rounded-lg border border-border bg-background p-4">
            <p className="text-xs font-semibold uppercase tracking-wide text-text-secondary">
              Narrator
            </p>
            <p className="mt-3 text-sm leading-6 text-text-primary">{caption}</p>
          </aside>
        </div>
      </div>
    </motion.section>
  );
}
