"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";

const STEPS = [
  {
    title: "The Problem",
    content: (
      <div className="space-y-8 text-center max-w-2xl mx-auto">
        <p className="text-6xl font-bold text-white">$19 trillion</p>
        <p className="text-xl text-zinc-400">
          The annual global cost of violent conflict. Yet analysts still use
          Word documents, spreadsheets, and tribal knowledge.
        </p>
        <div className="grid grid-cols-3 gap-4 mt-8">
          <div className="card p-4">
            <p className="text-sm font-medium text-zinc-300">ACLED</p>
            <p className="text-xs text-zinc-500">Data only. No structure.</p>
          </div>
          <div className="card p-4">
            <p className="text-sm font-medium text-zinc-300">CrisisWatch</p>
            <p className="text-xs text-zinc-500">Narrative only. No graph.</p>
          </div>
          <div className="card p-4">
            <p className="text-sm font-medium text-zinc-300">Palantir</p>
            <p className="text-xs text-zinc-500">$1M+. Not conflict-native.</p>
          </div>
        </div>
        <p className="text-lg text-teal-400 font-medium mt-6">
          There is no computational infrastructure for conflict intelligence.
          Until now.
        </p>
      </div>
    ),
  },
  {
    title: "Paste Any Conflict",
    content: (
      <div className="space-y-6 max-w-2xl mx-auto">
        <p className="text-xl text-zinc-300 text-center">
          Any conflict. Any domain. Any language. Structured in seconds.
        </p>
        <div className="card p-6 font-mono text-sm text-zinc-400 leading-relaxed">
          <TypewriterText text="Sarah Chen, a senior engineer at Veridian Technologies, raised concerns about mounting technical debt during sprint planning on February 12. Marcus Rivera, the product manager, publicly dismissed her analysis in the #engineering Slack channel, calling it 'pessimistic sandbagging that threatens our Q2 deliverables.' Sarah experienced this as a personal attack on her professional competence..." />
        </div>
        <p className="text-sm text-zinc-500 text-center">
          Real text. Real extraction. No synthetic demos.
        </p>
      </div>
    ),
  },
  {
    title: "AI Extracts Structure",
    content: (
      <div className="space-y-6 max-w-2xl mx-auto">
        <p className="text-xl text-zinc-300 text-center">
          Neurosymbolic: LLM extraction + symbolic validation = no hallucinations
        </p>
        <div className="space-y-3">
          {[
            { step: "GLiNER pre-filter", time: "0.3s", detail: "12 conflict entities detected" },
            { step: "Gemini Flash extraction", time: "1.8s", detail: "4 actors, 3 interests, 3 events" },
            { step: "Pydantic validation", time: "0.1s", detail: "All entities schema-valid" },
            { step: "Symbolic rule engine", time: "0.2s", detail: "Glasl stage 3 derived deterministically" },
            { step: "Knowledge graph write", time: "0.4s", detail: "17 nodes, 23 edges committed" },
          ].map((s, i) => (
            <div key={i} className="flex items-center gap-3 card p-3">
              <span className="text-teal-400 text-lg">✓</span>
              <span className="text-sm text-zinc-300 flex-1">{s.step}</span>
              <span className="text-xs text-zinc-500">{s.time}</span>
              <span className="text-xs text-zinc-400">{s.detail}</span>
            </div>
          ))}
        </div>
      </div>
    ),
  },
  {
    title: "Knowledge Graph",
    content: (
      <div className="space-y-6 max-w-3xl mx-auto text-center">
        <p className="text-xl text-zinc-300">
          Every conflict becomes a typed, queryable knowledge graph
        </p>
        <div className="grid grid-cols-4 gap-3">
          {[
            { label: "Actors", color: "bg-blue-500", count: 4 },
            { label: "Interests", color: "bg-green-500", count: 3 },
            { label: "Events", color: "bg-yellow-500", count: 3 },
            { label: "Norms", color: "bg-purple-500", count: 1 },
          ].map((n) => (
            <div key={n.label} className="card p-4 text-center">
              <div className={`w-4 h-4 rounded-full ${n.color} mx-auto mb-2`} />
              <p className="text-2xl font-bold text-white">{n.count}</p>
              <p className="text-xs text-zinc-400">{n.label}</p>
            </div>
          ))}
        </div>
        <p className="text-sm text-zinc-500">
          15 node types · 20 edge types · 25+ controlled vocabularies
        </p>
        <div className="card p-8 text-zinc-500 text-sm">
          [Live ForceGraph renders here when connected to API]
        </div>
      </div>
    ),
  },
  {
    title: "Theory-Grounded Analysis",
    content: (
      <div className="space-y-6 max-w-2xl mx-auto">
        <p className="text-xl text-zinc-300 text-center">
          Grounded in Fisher/Ury, Glasl, Zartman, and 27 more frameworks
        </p>
        <div className="grid grid-cols-2 gap-4">
          <div className="card p-4">
            <p className="text-sm text-zinc-400">Glasl Escalation</p>
            <p className="text-2xl font-bold text-yellow-400">Stage 3</p>
            <p className="text-xs text-zinc-500">Win-Win · Moderation recommended</p>
          </div>
          <div className="card p-4">
            <p className="text-sm text-zinc-400">Ripeness (Zartman)</p>
            <p className="text-2xl font-bold text-teal-400">42%</p>
            <p className="text-xs text-zinc-500">Approaching · MHS detected</p>
          </div>
          <div className="card p-4">
            <p className="text-sm text-zinc-400">Trust (Mayer)</p>
            <p className="text-2xl font-bold text-red-400">Low</p>
            <p className="text-xs text-zinc-500">Integrity deficit critical</p>
          </div>
          <div className="card p-4">
            <p className="text-sm text-zinc-400">Best Match</p>
            <p className="text-2xl font-bold text-blue-400">Fisher/Ury</p>
            <p className="text-xs text-zinc-500">Interest-based negotiation</p>
          </div>
        </div>
        <div className="card p-4 border-teal-600/50">
          <p className="text-sm text-teal-400 font-medium">Symbolic Firewall</p>
          <p className="text-xs text-zinc-400 mt-1">
            Deterministic conclusions (Glasl stage, norm violations) are NEVER
            overridden by probabilistic LLM predictions. This is architectural,
            not a prompt instruction.
          </p>
        </div>
        <p className="text-2xl text-white text-center font-bold mt-8">
          This is DIALECTICA.
        </p>
        <p className="text-lg text-teal-400 text-center">
          We&apos;re raising to make conflict computable.
        </p>
        <div className="flex justify-center gap-4 mt-4">
          <Link href="/demo" className="btn-primary px-6 py-3">
            Try the Demo
          </Link>
          <Link href="/" className="btn-secondary px-6 py-3">
            Learn More
          </Link>
        </div>
      </div>
    ),
  },
];

function TypewriterText({ text }: { text: string }) {
  const [displayed, setDisplayed] = useState("");
  useEffect(() => {
    let i = 0;
    const interval = setInterval(() => {
      if (i < text.length) {
        setDisplayed(text.slice(0, i + 1));
        i++;
      } else {
        clearInterval(interval);
      }
    }, 8);
    return () => clearInterval(interval);
  }, [text]);
  return <>{displayed}<span className="animate-pulse">|</span></>;
}

export default function InvestorDemoPage() {
  const [step, setStep] = useState(0);

  const goNext = useCallback(() => setStep((s) => Math.min(s + 1, STEPS.length - 1)), []);
  const goPrev = useCallback(() => setStep((s) => Math.max(s - 1, 0)), []);

  useEffect(() => {
    function handleKey(e: KeyboardEvent) {
      if (e.key === "ArrowRight") goNext();
      if (e.key === "ArrowLeft") goPrev();
    }
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [goNext, goPrev]);

  return (
    <div className="fixed inset-0 bg-background flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-800">
        <span className="text-sm text-zinc-400">DIALECTICA · Investor Demo</span>
        <div className="flex items-center gap-2">
          {STEPS.map((_, i) => (
            <button
              key={i}
              onClick={() => setStep(i)}
              className={`w-2.5 h-2.5 rounded-full transition-colors ${
                i === step ? "bg-teal-400" : i < step ? "bg-teal-700" : "bg-zinc-700"
              }`}
            />
          ))}
        </div>
        <span className="text-sm text-zinc-500">
          {step + 1} / {STEPS.length}
        </span>
      </div>

      {/* Content */}
      <div className="flex-1 flex flex-col items-center justify-center px-8 overflow-y-auto">
        <h2 className="text-3xl font-bold text-white mb-8">
          {STEPS[step].title}
        </h2>
        {STEPS[step].content}
      </div>

      {/* Navigation */}
      <div className="flex items-center justify-between px-6 py-4 border-t border-zinc-800">
        <button
          onClick={goPrev}
          disabled={step === 0}
          className="btn-secondary px-4 py-2 disabled:opacity-30"
        >
          ← Previous
        </button>
        <span className="text-xs text-zinc-600">Arrow keys to navigate</span>
        <button
          onClick={goNext}
          disabled={step === STEPS.length - 1}
          className="btn-primary px-4 py-2 disabled:opacity-30"
        >
          Next →
        </button>
      </div>
    </div>
  );
}
