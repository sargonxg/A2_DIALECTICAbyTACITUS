"use client";

import type { TrustPair } from "@/types/analysis";

interface Props {
  pairs: TrustPair[];
  actors: string[];
}

function trustColor(val: number): string {
  if (val >= 0.7) return "#10b981";
  if (val >= 0.4) return "#f59e0b";
  return "#f43f5e";
}

export default function TrustMatrix({ pairs, actors }: Props) {
  const matrix = new Map<string, number>();
  pairs.forEach((p) => {
    matrix.set(`${p.actor_a}:${p.actor_b}`, p.overall);
    matrix.set(`${p.actor_b}:${p.actor_a}`, p.overall);
  });

  return (
    <div className="card overflow-x-auto">
      <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wider mb-3">Trust Matrix</h3>
      <table className="w-full text-xs">
        <thead>
          <tr>
            <th className="text-left text-text-secondary p-1"></th>
            {actors.map((a) => (
              <th key={a} className="text-center text-text-secondary p-1 max-w-[80px] truncate">{a}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {actors.map((row) => (
            <tr key={row}>
              <td className="text-text-secondary p-1 max-w-[80px] truncate">{row}</td>
              {actors.map((col) => {
                const val = row === col ? 1.0 : matrix.get(`${row}:${col}`) ?? 0;
                return (
                  <td key={col} className="p-1 text-center">
                    <span
                      className="inline-block w-8 h-8 rounded-sm leading-8 font-mono text-[10px]"
                      style={{ backgroundColor: trustColor(val) + "30", color: trustColor(val) }}
                    >
                      {(val * 100).toFixed(0)}
                    </span>
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
