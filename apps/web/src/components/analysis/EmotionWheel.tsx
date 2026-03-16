"use client";

const EMOTIONS = [
  { name: "Joy", color: "#fbbf24", angle: 0 },
  { name: "Trust", color: "#34d399", angle: 45 },
  { name: "Fear", color: "#60a5fa", angle: 90 },
  { name: "Surprise", color: "#818cf8", angle: 135 },
  { name: "Sadness", color: "#93c5fd", angle: 180 },
  { name: "Disgust", color: "#a78bfa", angle: 225 },
  { name: "Anger", color: "#f87171", angle: 270 },
  { name: "Anticipation", color: "#fb923c", angle: 315 },
];

interface Props {
  intensities: Record<string, number>;
}

export default function EmotionWheel({ intensities }: Props) {
  const r = 80;
  const cx = 100;
  const cy = 100;

  return (
    <div className="card">
      <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wider mb-3">Plutchik Emotion Wheel</h3>
      <svg viewBox="0 0 200 200" className="w-full max-w-[200px] mx-auto">
        {EMOTIONS.map((emotion) => {
          const intensity = intensities[emotion.name.toLowerCase()] ?? 0;
          const rad = (emotion.angle * Math.PI) / 180;
          const dist = r * Math.max(0.2, intensity);
          const x = cx + Math.cos(rad) * dist;
          const y = cy + Math.sin(rad) * dist;
          return (
            <g key={emotion.name}>
              <line x1={cx} y1={cy} x2={x} y2={y} stroke={emotion.color} strokeWidth={2} opacity={0.5} />
              <circle cx={x} cy={y} r={Math.max(6, intensity * 14)} fill={emotion.color} opacity={0.8} />
              <text x={cx + Math.cos(rad) * (r + 15)} y={cy + Math.sin(rad) * (r + 15)} textAnchor="middle" dominantBaseline="middle" fill="#94a3b8" fontSize="8">
                {emotion.name}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
