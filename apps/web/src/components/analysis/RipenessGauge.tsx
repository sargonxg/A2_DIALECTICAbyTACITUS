"use client";

interface Props {
  mhsScore: number;
  meoScore: number;
  isRipe: boolean;
}

export default function RipenessGauge({ mhsScore, meoScore, isRipe }: Props) {
  const overall = (mhsScore + meoScore) / 2;

  return (
    <div className="card">
      <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wider mb-3">
        Zartman Ripeness
      </h3>
      <div className="flex items-center justify-center gap-8">
        <GaugeCircle label="MHS" value={mhsScore} color="#f59e0b" />
        <GaugeCircle label="MEO" value={meoScore} color="#14b8a6" />
      </div>
      <div className="text-center mt-3">
        <span className={`badge ${isRipe ? "bg-success/20 text-success" : "bg-warning/20 text-warning"}`}>
          {isRipe ? "Ripe for Resolution" : "Not Yet Ripe"}
        </span>
      </div>
    </div>
  );
}

function GaugeCircle({ label, value, color }: { label: string; value: number; color: string }) {
  const pct = value * 100;
  const r = 40;
  const circ = 2 * Math.PI * r;
  const offset = circ - (pct / 100) * circ;

  return (
    <div className="text-center">
      <svg width={100} height={100} viewBox="0 0 100 100">
        <circle cx="50" cy="50" r={r} fill="none" stroke="#1e293b" strokeWidth="8" />
        <circle
          cx="50" cy="50" r={r} fill="none" stroke={color} strokeWidth="8"
          strokeDasharray={circ} strokeDashoffset={offset}
          strokeLinecap="round" transform="rotate(-90 50 50)"
        />
        <text x="50" y="50" textAnchor="middle" dominantBaseline="middle" fill="#f1f5f9" fontSize="16" fontFamily="monospace">
          {pct.toFixed(0)}
        </text>
      </svg>
      <p className="text-xs text-text-secondary mt-1">{label}</p>
    </div>
  );
}
