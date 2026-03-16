'use client';

import React from 'react';
import { ShieldAlert, ShieldCheck, ShieldX, Activity } from 'lucide-react';

interface GlaslStageIndicatorProps {
  stage: number;
  level: string;
  confidence: number;
  interventionType: string;
}

interface StageConfig {
  color: string;
  bgColor: string;
  borderColor: string;
  ringColor: string;
  label: string;
  zone: 'win-win' | 'win-lose' | 'lose-lose';
}

const STAGE_CONFIGS: Record<number, StageConfig> = {
  1: { color: '#22c55e', bgColor: 'bg-green-500/20', borderColor: 'border-green-500/40', ringColor: 'ring-green-500', label: 'Hardening', zone: 'win-win' },
  2: { color: '#22c55e', bgColor: 'bg-green-500/20', borderColor: 'border-green-500/40', ringColor: 'ring-green-500', label: 'Debate & Polemics', zone: 'win-win' },
  3: { color: '#22c55e', bgColor: 'bg-green-500/20', borderColor: 'border-green-500/40', ringColor: 'ring-green-500', label: 'Actions Not Words', zone: 'win-win' },
  4: { color: '#eab308', bgColor: 'bg-yellow-500/20', borderColor: 'border-yellow-500/40', ringColor: 'ring-yellow-500', label: 'Images & Coalitions', zone: 'win-lose' },
  5: { color: '#eab308', bgColor: 'bg-yellow-500/20', borderColor: 'border-yellow-500/40', ringColor: 'ring-yellow-500', label: 'Loss of Face', zone: 'win-lose' },
  6: { color: '#eab308', bgColor: 'bg-yellow-500/20', borderColor: 'border-yellow-500/40', ringColor: 'ring-yellow-500', label: 'Strategy of Threats', zone: 'win-lose' },
  7: { color: '#ef4444', bgColor: 'bg-red-500/20', borderColor: 'border-red-500/40', ringColor: 'ring-red-500', label: 'Limited Destructive Blows', zone: 'lose-lose' },
  8: { color: '#ef4444', bgColor: 'bg-red-500/20', borderColor: 'border-red-500/40', ringColor: 'ring-red-500', label: 'Fragmentation', zone: 'lose-lose' },
  9: { color: '#ef4444', bgColor: 'bg-red-500/20', borderColor: 'border-red-500/40', ringColor: 'ring-red-500', label: 'Together into the Abyss', zone: 'lose-lose' },
};

const ZONE_CONFIGS = {
  'win-win': { label: 'Win–Win', color: '#22c55e', icon: ShieldCheck, description: 'Negotiable — de-escalation achievable through dialogue' },
  'win-lose': { label: 'Win–Lose', color: '#eab308', icon: ShieldAlert, description: 'Mediation required — parties seek unilateral advantage' },
  'lose-lose': { label: 'Lose–Lose', color: '#ef4444', icon: ShieldX, description: 'Crisis intervention — mutual destruction risk' },
};

function getZoneForStage(stage: number): 'win-win' | 'win-lose' | 'lose-lose' {
  if (stage <= 3) return 'win-win';
  if (stage <= 6) return 'win-lose';
  return 'lose-lose';
}

function getInterventionBadgeStyle(type: string): string {
  const lower = type.toLowerCase();
  if (lower.includes('mediat')) return 'bg-teal-600/20 text-teal-400 border-teal-600/30';
  if (lower.includes('negotiat')) return 'bg-blue-600/20 text-blue-400 border-blue-600/30';
  if (lower.includes('facilitat')) return 'bg-purple-600/20 text-purple-400 border-purple-600/30';
  if (lower.includes('arbitrat')) return 'bg-orange-600/20 text-orange-400 border-orange-600/30';
  if (lower.includes('crisis')) return 'bg-red-600/20 text-red-400 border-red-600/30';
  return 'bg-zinc-700/50 text-zinc-300 border-zinc-600/30';
}

export function GlaslStageIndicator({
  stage,
  level,
  confidence,
  interventionType,
}: GlaslStageIndicatorProps) {
  const clampedStage = Math.min(9, Math.max(1, Math.round(stage)));
  const currentZone = getZoneForStage(clampedStage);
  const zoneConfig = ZONE_CONFIGS[currentZone];
  const ZoneIcon = zoneConfig.icon;
  const confidencePct = Math.round(confidence * 100);

  return (
    <div className="rounded-xl border border-[#27272a] bg-[#18181b] p-5 space-y-5">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-zinc-400" />
            <span className="text-xs font-semibold uppercase tracking-widest text-zinc-400">
              Glasl Escalation Model
            </span>
          </div>
          <h3 className="text-lg font-semibold text-white">
            Stage {clampedStage}: {STAGE_CONFIGS[clampedStage]?.label ?? 'Unknown'}
          </h3>
          <p className="text-sm text-zinc-400">{level}</p>
        </div>
        {/* Zone badge */}
        <div
          className="flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-sm font-medium"
          style={{
            color: zoneConfig.color,
            borderColor: `${zoneConfig.color}40`,
            backgroundColor: `${zoneConfig.color}15`,
          }}
        >
          <ZoneIcon className="w-4 h-4" />
          {zoneConfig.label}
        </div>
      </div>

      {/* Stage track */}
      <div className="space-y-2">
        {/* Zone labels */}
        <div className="grid grid-cols-3 text-center text-[10px] font-medium uppercase tracking-widest">
          <span className="text-green-500">Win–Win</span>
          <span className="text-yellow-500">Win–Lose</span>
          <span className="text-red-500">Lose–Lose</span>
        </div>
        {/* Stage pills */}
        <div className="flex gap-1">
          {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((s) => {
            const cfg = STAGE_CONFIGS[s];
            const isActive = s === clampedStage;
            const isPast = s < clampedStage;
            return (
              <div
                key={s}
                className={[
                  'flex-1 rounded-md flex flex-col items-center justify-center py-2 transition-all duration-200 relative',
                  isActive
                    ? `ring-2 ${cfg.ringColor} shadow-lg`
                    : '',
                  isPast ? 'opacity-60' : '',
                  !isActive && !isPast ? 'opacity-30' : '',
                ].join(' ')}
                style={{
                  backgroundColor: isActive || isPast ? `${cfg.color}20` : `${cfg.color}08`,
                  borderWidth: '1px',
                  borderStyle: 'solid',
                  borderColor: `${cfg.color}${isActive ? '80' : '30'}`,
                }}
              >
                <span
                  className="text-sm font-bold"
                  style={{ color: isActive ? cfg.color : `${cfg.color}99` }}
                >
                  {s}
                </span>
                {isActive && (
                  <span
                    className="absolute -bottom-1.5 left-1/2 -translate-x-1/2 w-0 h-0"
                    style={{
                      borderLeft: '5px solid transparent',
                      borderRight: '5px solid transparent',
                      borderTop: `5px solid ${cfg.color}`,
                    }}
                  />
                )}
              </div>
            );
          })}
        </div>
        {/* Stage descriptions row */}
        <div className="flex gap-1">
          {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((s) => {
            const cfg = STAGE_CONFIGS[s];
            const isActive = s === clampedStage;
            return (
              <div
                key={s}
                className="flex-1 text-center"
                style={{ minWidth: 0 }}
              >
                {isActive && (
                  <span
                    className="block text-[9px] font-medium leading-tight mt-1"
                    style={{ color: cfg.color }}
                  >
                    {cfg.label}
                  </span>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Confidence bar */}
      <div className="space-y-1.5">
        <div className="flex items-center justify-between text-xs">
          <span className="text-zinc-400 font-medium">Model Confidence</span>
          <span className="font-semibold" style={{ color: STAGE_CONFIGS[clampedStage]?.color }}>
            {confidencePct}%
          </span>
        </div>
        <div className="h-2 rounded-full bg-zinc-800 overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-700 ease-out"
            style={{
              width: `${confidencePct}%`,
              backgroundColor: STAGE_CONFIGS[clampedStage]?.color,
            }}
          />
        </div>
      </div>

      {/* Footer row */}
      <div className="flex items-center justify-between gap-3 pt-1">
        <div className="space-y-0.5">
          <p className="text-[10px] uppercase tracking-widest text-zinc-500 font-medium">
            Recommended Intervention
          </p>
          <span
            className={[
              'inline-block rounded border px-2 py-0.5 text-xs font-medium',
              getInterventionBadgeStyle(interventionType),
            ].join(' ')}
          >
            {interventionType}
          </span>
        </div>
        <div className="text-right space-y-0.5">
          <p className="text-[10px] uppercase tracking-widest text-zinc-500 font-medium">Zone</p>
          <p className="text-xs text-zinc-300">{zoneConfig.description}</p>
        </div>
      </div>
    </div>
  );
}

export default GlaslStageIndicator;
