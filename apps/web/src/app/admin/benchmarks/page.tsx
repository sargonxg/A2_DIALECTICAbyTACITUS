"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Target,
  Play,
  Loader2,
  Clock,
  AlertTriangle,
  CheckCircle2,
  ChevronDown,
  ArrowLeftRight,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { cn } from "@/lib/utils";
import { api } from "@/lib/api";
import { formatRelative } from "@/lib/utils";

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */

interface MetricScore {
  precision: number;
  recall: number;
  f1: number;
  true_positives: number;
  false_positives: number;
  false_negatives: number;
}

interface BenchmarkResults {
  overall: MetricScore;
  by_node_type: Record<string, MetricScore>;
  by_edge_type: Record<string, MetricScore>;
  graph_augmented: MetricScore | null;
  evaluation_points: number;
  extraction_time_ms: number;
  hallucination_rate: number;
}

interface BenchmarkRun {
  benchmark_id: string;
  corpus_id: string;
  tier: string;
  model: string;
  results: BenchmarkResults;
  completed_at: string;
}

/* ------------------------------------------------------------------ */
/*  Constants                                                          */
/* ------------------------------------------------------------------ */

const CORPORA = [
  { value: "jcpoa", label: "JCPOA Nuclear Negotiations" },
  { value: "romeo_juliet", label: "Romeo & Juliet" },
  { value: "crime_punishment", label: "Crime and Punishment" },
  { value: "war_peace", label: "War and Peace" },
  { value: "custom", label: "Custom Text" },
];

const TIERS = [
  { value: "essential", label: "Essential" },
  { value: "standard", label: "Standard" },
  { value: "full", label: "Full" },
];

const MODELS = [
  { value: "gemini-2.5-flash", label: "Gemini 2.5 Flash" },
  { value: "gemini-2.5-pro", label: "Gemini 2.5 Pro" },
];

const CHART_COLORS = {
  precision: "#14b8a6",
  recall: "#f59e0b",
  f1: "#8b5cf6",
};

/* ------------------------------------------------------------------ */
/*  Helpers                                                            */
/* ------------------------------------------------------------------ */

function pct(v: number): string {
  return `${(v * 100).toFixed(1)}%`;
}

function breakdownToChartData(
  breakdown: Record<string, MetricScore>,
): Array<{ name: string; precision: number; recall: number; f1: number }> {
  return Object.entries(breakdown).map(([name, m]) => ({
    name,
    precision: Math.round(m.precision * 100),
    recall: Math.round(m.recall * 100),
    f1: Math.round(m.f1 * 100),
  }));
}

function f1Color(f1: number): string {
  if (f1 >= 0.8) return "text-success";
  if (f1 >= 0.5) return "text-warning";
  return "text-danger";
}

/* ------------------------------------------------------------------ */
/*  Sub-components                                                     */
/* ------------------------------------------------------------------ */

function MetricCard({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="card text-center">
      <p className="text-xs text-text-secondary uppercase tracking-wider mb-1">{label}</p>
      <p className="text-3xl font-bold text-text-primary">{value}</p>
      {sub && <p className="text-xs text-text-secondary mt-1">{sub}</p>}
    </div>
  );
}

function BreakdownChart({
  title,
  data,
}: {
  title: string;
  data: Array<{ name: string; precision: number; recall: number; f1: number }>;
}) {
  if (data.length === 0) return null;
  return (
    <div className="card">
      <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wider mb-4">
        {title}
      </h3>
      <ResponsiveContainer width="100%" height={Math.max(200, data.length * 40)}>
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 5, right: 20, bottom: 5, left: 100 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis
            type="number"
            domain={[0, 100]}
            tick={{ fill: "#94a3b8", fontSize: 10 }}
            stroke="#334155"
            unit="%"
          />
          <YAxis
            type="category"
            dataKey="name"
            tick={{ fill: "#94a3b8", fontSize: 10 }}
            stroke="#334155"
            width={90}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#0f172a",
              border: "1px solid #1e293b",
              borderRadius: "0.375rem",
              color: "#f1f5f9",
            }}
            formatter={(value: number) => `${value}%`}
          />
          <Legend wrapperStyle={{ color: "#94a3b8", fontSize: 11 }} />
          <Bar dataKey="precision" fill={CHART_COLORS.precision} name="Precision" radius={[0, 2, 2, 0]} />
          <Bar dataKey="recall" fill={CHART_COLORS.recall} name="Recall" radius={[0, 2, 2, 0]} />
          <Bar dataKey="f1" fill={CHART_COLORS.f1} name="F1" radius={[0, 2, 2, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

function ResultsDisplay({ run }: { run: BenchmarkRun }) {
  const r = run.results;
  const nodeData = breakdownToChartData(r.by_node_type);
  const edgeData = breakdownToChartData(r.by_edge_type);

  return (
    <div className="space-y-4">
      {/* Overall metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <MetricCard label="Precision" value={pct(r.overall.precision)} sub={`TP: ${r.overall.true_positives} FP: ${r.overall.false_positives}`} />
        <MetricCard label="Recall" value={pct(r.overall.recall)} sub={`TP: ${r.overall.true_positives} FN: ${r.overall.false_negatives}`} />
        <MetricCard label="F1 Score" value={pct(r.overall.f1)} />
        <MetricCard label="Hallucination Rate" value={pct(r.hallucination_rate)} sub={r.hallucination_rate > 0.2 ? "High" : r.hallucination_rate > 0.1 ? "Moderate" : "Low"} />
      </div>

      {/* Secondary metrics */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        <div className="card flex items-center gap-3">
          <Clock size={16} className="text-text-secondary" />
          <div>
            <p className="text-xs text-text-secondary">Extraction Time</p>
            <p className="text-sm font-semibold text-text-primary">{r.extraction_time_ms.toFixed(0)} ms</p>
          </div>
        </div>
        <div className="card flex items-center gap-3">
          <Target size={16} className="text-text-secondary" />
          <div>
            <p className="text-xs text-text-secondary">Evaluation Points</p>
            <p className="text-sm font-semibold text-text-primary">{r.evaluation_points}</p>
          </div>
        </div>
        {r.graph_augmented && (
          <div className="card flex items-center gap-3">
            <CheckCircle2 size={16} className="text-accent" />
            <div>
              <p className="text-xs text-text-secondary">Graph-Augmented F1</p>
              <p className={cn("text-sm font-semibold", f1Color(r.graph_augmented.f1))}>
                {pct(r.graph_augmented.f1)}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Breakdown charts */}
      <BreakdownChart title="Per Node Type" data={nodeData} />
      <BreakdownChart title="Per Edge Type" data={edgeData} />
    </div>
  );
}

function ComparisonView({ runA, runB }: { runA: BenchmarkRun; runB: BenchmarkRun }) {
  const metrics: Array<{ label: string; a: string; b: string; better: "a" | "b" | "tie" }> = [
    {
      label: "Precision",
      a: pct(runA.results.overall.precision),
      b: pct(runB.results.overall.precision),
      better: runA.results.overall.precision > runB.results.overall.precision ? "a" : runA.results.overall.precision < runB.results.overall.precision ? "b" : "tie",
    },
    {
      label: "Recall",
      a: pct(runA.results.overall.recall),
      b: pct(runB.results.overall.recall),
      better: runA.results.overall.recall > runB.results.overall.recall ? "a" : runA.results.overall.recall < runB.results.overall.recall ? "b" : "tie",
    },
    {
      label: "F1",
      a: pct(runA.results.overall.f1),
      b: pct(runB.results.overall.f1),
      better: runA.results.overall.f1 > runB.results.overall.f1 ? "a" : runA.results.overall.f1 < runB.results.overall.f1 ? "b" : "tie",
    },
    {
      label: "Hallucination",
      a: pct(runA.results.hallucination_rate),
      b: pct(runB.results.hallucination_rate),
      better: runA.results.hallucination_rate < runB.results.hallucination_rate ? "a" : runA.results.hallucination_rate > runB.results.hallucination_rate ? "b" : "tie",
    },
    {
      label: "Extraction Time",
      a: `${runA.results.extraction_time_ms.toFixed(0)} ms`,
      b: `${runB.results.extraction_time_ms.toFixed(0)} ms`,
      better: runA.results.extraction_time_ms < runB.results.extraction_time_ms ? "a" : runA.results.extraction_time_ms > runB.results.extraction_time_ms ? "b" : "tie",
    },
  ];

  return (
    <div className="card">
      <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wider mb-4">
        Comparison
      </h3>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border">
              <th className="text-left py-2 text-text-secondary font-medium">Metric</th>
              <th className="text-right py-2 text-text-secondary font-medium">
                {runA.corpus_id} ({runA.model})
              </th>
              <th className="text-right py-2 text-text-secondary font-medium">
                {runB.corpus_id} ({runB.model})
              </th>
            </tr>
          </thead>
          <tbody>
            {metrics.map((m) => (
              <tr key={m.label} className="border-b border-border/50">
                <td className="py-2 text-text-primary">{m.label}</td>
                <td
                  className={cn(
                    "py-2 text-right font-mono",
                    m.better === "a" ? "text-success" : "text-text-secondary",
                  )}
                >
                  {m.a}
                </td>
                <td
                  className={cn(
                    "py-2 text-right font-mono",
                    m.better === "b" ? "text-success" : "text-text-secondary",
                  )}
                >
                  {m.b}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Main page                                                          */
/* ------------------------------------------------------------------ */

export default function BenchmarksPage() {
  // Config state
  const [corpus, setCorpus] = useState("jcpoa");
  const [tier, setTier] = useState("standard");
  const [model, setModel] = useState("gemini-2.5-flash");
  const [includeGraph, setIncludeGraph] = useState(false);

  // Run state
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentRun, setCurrentRun] = useState<BenchmarkRun | null>(null);

  // History
  const [history, setHistory] = useState<BenchmarkRun[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(true);

  // Comparison
  const [compareMode, setCompareMode] = useState(false);
  const [compareA, setCompareA] = useState<string | null>(null);
  const [compareB, setCompareB] = useState<string | null>(null);

  const fetchHistory = useCallback(async () => {
    try {
      setLoadingHistory(true);
      const data = await api.getBenchmarkHistory(50);
      setHistory(data as unknown as BenchmarkRun[]);
    } catch {
      // History fetch failure is non-critical
    } finally {
      setLoadingHistory(false);
    }
  }, []);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  const handleRun = async () => {
    setRunning(true);
    setError(null);
    setCurrentRun(null);
    try {
      const result = await api.runBenchmark({
        corpus_id: corpus,
        tier,
        model,
        include_graph_augmented: includeGraph,
      });
      const run = result as unknown as BenchmarkRun;
      setCurrentRun(run);
      // Refresh history
      await fetchHistory();
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Benchmark run failed";
      setError(message);
    } finally {
      setRunning(false);
    }
  };

  const runA = compareA ? history.find((h) => h.benchmark_id === compareA) : null;
  const runB = compareB ? history.find((h) => h.benchmark_id === compareB) : null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Target size={20} className="text-accent" />
          <h2 className="text-lg font-semibold text-text-primary">Extraction Benchmarks</h2>
        </div>
        <span className="text-xs text-text-secondary">
          {history.length} run{history.length !== 1 ? "s" : ""} recorded
        </span>
      </div>

      {/* Configuration panel */}
      <div className="card">
        <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wider mb-4">
          Configuration
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Corpus */}
          <div>
            <label className="block text-xs text-text-secondary mb-1">Corpus</label>
            <div className="relative">
              <select
                value={corpus}
                onChange={(e) => setCorpus(e.target.value)}
                className="w-full bg-surface-hover border border-border rounded-md px-3 py-2 text-sm text-text-primary appearance-none cursor-pointer focus:outline-none focus:border-accent"
              >
                {CORPORA.map((c) => (
                  <option key={c.value} value={c.value}>
                    {c.label}
                  </option>
                ))}
              </select>
              <ChevronDown
                size={14}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-text-secondary pointer-events-none"
              />
            </div>
          </div>

          {/* Tier */}
          <div>
            <label className="block text-xs text-text-secondary mb-1">Tier</label>
            <div className="relative">
              <select
                value={tier}
                onChange={(e) => setTier(e.target.value)}
                className="w-full bg-surface-hover border border-border rounded-md px-3 py-2 text-sm text-text-primary appearance-none cursor-pointer focus:outline-none focus:border-accent"
              >
                {TIERS.map((t) => (
                  <option key={t.value} value={t.value}>
                    {t.label}
                  </option>
                ))}
              </select>
              <ChevronDown
                size={14}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-text-secondary pointer-events-none"
              />
            </div>
          </div>

          {/* Model */}
          <div>
            <label className="block text-xs text-text-secondary mb-1">Model</label>
            <div className="relative">
              <select
                value={model}
                onChange={(e) => setModel(e.target.value)}
                className="w-full bg-surface-hover border border-border rounded-md px-3 py-2 text-sm text-text-primary appearance-none cursor-pointer focus:outline-none focus:border-accent"
              >
                {MODELS.map((m) => (
                  <option key={m.value} value={m.value}>
                    {m.label}
                  </option>
                ))}
              </select>
              <ChevronDown
                size={14}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-text-secondary pointer-events-none"
              />
            </div>
          </div>

          {/* Run button + graph toggle */}
          <div className="flex flex-col justify-end gap-2">
            <label className="flex items-center gap-2 text-xs text-text-secondary cursor-pointer">
              <input
                type="checkbox"
                checked={includeGraph}
                onChange={(e) => setIncludeGraph(e.target.checked)}
                className="rounded border-border bg-surface-hover accent-accent"
              />
              Graph-augmented
            </label>
            <button
              onClick={handleRun}
              disabled={running}
              className={cn(
                "flex items-center justify-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors",
                running
                  ? "bg-surface-active text-text-secondary cursor-not-allowed"
                  : "bg-accent text-surface hover:bg-accent/90",
              )}
            >
              {running ? (
                <>
                  <Loader2 size={14} className="animate-spin" />
                  Running...
                </>
              ) : (
                <>
                  <Play size={14} />
                  Run Benchmark
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="card border-danger/30 flex items-start gap-3">
          <AlertTriangle size={16} className="text-danger mt-0.5" />
          <div>
            <p className="text-sm font-medium text-danger">Benchmark Failed</p>
            <p className="text-xs text-text-secondary mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* Current results */}
      {currentRun && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <CheckCircle2 size={16} className="text-success" />
            <h3 className="text-sm font-semibold text-text-primary">
              Latest Result: {currentRun.corpus_id} / {currentRun.tier} / {currentRun.model}
            </h3>
          </div>
          <ResultsDisplay run={currentRun} />
        </div>
      )}

      {/* History */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wider">
            Run History
          </h3>
          <button
            onClick={() => {
              setCompareMode(!compareMode);
              setCompareA(null);
              setCompareB(null);
            }}
            className={cn(
              "flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs transition-colors",
              compareMode
                ? "bg-accent/10 text-accent"
                : "text-text-secondary hover:text-text-primary hover:bg-surface-hover",
            )}
          >
            <ArrowLeftRight size={12} />
            {compareMode ? "Cancel Compare" : "Compare"}
          </button>
        </div>

        {compareMode && (
          <p className="text-xs text-text-secondary mb-3">
            Select two runs to compare. Click a row to select it.
          </p>
        )}

        {loadingHistory ? (
          <div className="flex items-center justify-center py-8 text-text-secondary">
            <Loader2 size={16} className="animate-spin mr-2" />
            Loading history...
          </div>
        ) : history.length === 0 ? (
          <p className="text-sm text-text-secondary text-center py-8">
            No benchmark runs yet. Run your first benchmark above.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  {compareMode && <th className="py-2 w-8"></th>}
                  <th className="text-left py-2 text-text-secondary font-medium">Date</th>
                  <th className="text-left py-2 text-text-secondary font-medium">Corpus</th>
                  <th className="text-left py-2 text-text-secondary font-medium">Tier</th>
                  <th className="text-left py-2 text-text-secondary font-medium">Model</th>
                  <th className="text-right py-2 text-text-secondary font-medium">Precision</th>
                  <th className="text-right py-2 text-text-secondary font-medium">Recall</th>
                  <th className="text-right py-2 text-text-secondary font-medium">F1</th>
                  <th className="text-right py-2 text-text-secondary font-medium">Time</th>
                </tr>
              </thead>
              <tbody>
                {history.map((run) => {
                  const isSelectedA = compareA === run.benchmark_id;
                  const isSelectedB = compareB === run.benchmark_id;
                  const isSelected = isSelectedA || isSelectedB;

                  return (
                    <tr
                      key={run.benchmark_id}
                      className={cn(
                        "border-b border-border/50 transition-colors",
                        compareMode
                          ? "cursor-pointer hover:bg-surface-hover"
                          : "cursor-pointer hover:bg-surface-hover",
                        isSelected && "bg-accent/5",
                      )}
                      onClick={() => {
                        if (compareMode) {
                          if (isSelectedA) {
                            setCompareA(null);
                          } else if (isSelectedB) {
                            setCompareB(null);
                          } else if (!compareA) {
                            setCompareA(run.benchmark_id);
                          } else if (!compareB) {
                            setCompareB(run.benchmark_id);
                          }
                        } else {
                          setCurrentRun(run);
                        }
                      }}
                    >
                      {compareMode && (
                        <td className="py-2">
                          <div
                            className={cn(
                              "w-4 h-4 rounded border flex items-center justify-center text-xs",
                              isSelected
                                ? "border-accent bg-accent text-surface"
                                : "border-border",
                            )}
                          >
                            {isSelectedA ? "A" : isSelectedB ? "B" : ""}
                          </div>
                        </td>
                      )}
                      <td className="py-2 text-text-secondary">
                        {formatRelative(run.completed_at)}
                      </td>
                      <td className="py-2 text-text-primary">{run.corpus_id}</td>
                      <td className="py-2 text-text-secondary">{run.tier}</td>
                      <td className="py-2 text-text-secondary">{run.model}</td>
                      <td className="py-2 text-right font-mono text-text-primary">
                        {pct(run.results.overall.precision)}
                      </td>
                      <td className="py-2 text-right font-mono text-text-primary">
                        {pct(run.results.overall.recall)}
                      </td>
                      <td
                        className={cn(
                          "py-2 text-right font-mono font-semibold",
                          f1Color(run.results.overall.f1),
                        )}
                      >
                        {pct(run.results.overall.f1)}
                      </td>
                      <td className="py-2 text-right text-text-secondary">
                        {run.results.extraction_time_ms.toFixed(0)} ms
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Comparison view */}
      {compareMode && runA && runB && <ComparisonView runA={runA} runB={runB} />}
    </div>
  );
}
