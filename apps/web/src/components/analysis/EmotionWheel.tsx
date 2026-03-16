'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { Heart, RefreshCw, AlertCircle } from 'lucide-react';
import { graphApi, type GraphNode } from '@/lib/api';

interface EmotionWheelProps {
  workspaceId: string;
}

// Plutchik primary emotions with associated colours
interface PlutchikEmotion {
  id: string;
  label: string;
  color: string;
  textColor: string;
  opposite: string;
  // SVG path segment params
  startAngle: number; // degrees
}

const PLUTCHIK_EMOTIONS: PlutchikEmotion[] = [
  { id: 'joy', label: 'Joy', color: '#facc15', textColor: '#713f12', opposite: 'sadness', startAngle: 0 },
  { id: 'trust', label: 'Trust', color: '#4ade80', textColor: '#14532d', opposite: 'disgust', startAngle: 45 },
  { id: 'fear', label: 'Fear', color: '#166534', textColor: '#bbf7d0', opposite: 'anger', startAngle: 90 },
  { id: 'surprise', label: 'Surprise', color: '#22d3ee', textColor: '#083344', opposite: 'anticipation', startAngle: 135 },
  { id: 'sadness', label: 'Sadness', color: '#3b82f6', textColor: '#eff6ff', opposite: 'joy', startAngle: 180 },
  { id: 'disgust', label: 'Disgust', color: '#a855f7', textColor: '#faf5ff', opposite: 'trust', startAngle: 225 },
  { id: 'anger', label: 'Anger', color: '#ef4444', textColor: '#fff1f2', opposite: 'fear', startAngle: 270 },
  { id: 'anticipation', label: 'Anticipation', color: '#f97316', textColor: '#fff7ed', opposite: 'surprise', startAngle: 315 },
];

const EMOTION_ALIASES: Record<string, string> = {
  happy: 'joy',
  happiness: 'joy',
  joyful: 'joy',
  scared: 'fear',
  fearful: 'fear',
  afraid: 'fear',
  disgusted: 'disgust',
  repulsed: 'disgust',
  surprised: 'surprise',
  shocked: 'surprise',
  sad: 'sadness',
  sorrowful: 'sadness',
  grief: 'sadness',
  angry: 'anger',
  rage: 'anger',
  furious: 'anger',
  anticipatory: 'anticipation',
  hopeful: 'anticipation',
  trusting: 'trust',
};

function normaliseEmotion(raw: string): string {
  const lower = raw.toLowerCase().trim();
  return EMOTION_ALIASES[lower] ?? lower;
}

function findPlutchik(id: string): PlutchikEmotion | undefined {
  return PLUTCHIK_EMOTIONS.find(
    (e) => e.id === id || e.label.toLowerCase() === id,
  );
}

// Polar to Cartesian for SVG arc
function polarToCartesian(cx: number, cy: number, r: number, angleDeg: number) {
  const rad = ((angleDeg - 90) * Math.PI) / 180;
  return {
    x: cx + r * Math.cos(rad),
    y: cy + r * Math.sin(rad),
  };
}

function arcPath(
  cx: number,
  cy: number,
  outerR: number,
  innerR: number,
  startAngle: number,
  endAngle: number,
): string {
  const o1 = polarToCartesian(cx, cy, outerR, startAngle + 1);
  const o2 = polarToCartesian(cx, cy, outerR, endAngle - 1);
  const i1 = polarToCartesian(cx, cy, innerR, endAngle - 1);
  const i2 = polarToCartesian(cx, cy, innerR, startAngle + 1);
  const largeArc = endAngle - startAngle > 180 ? 1 : 0;
  return [
    `M ${o1.x} ${o1.y}`,
    `A ${outerR} ${outerR} 0 ${largeArc} 1 ${o2.x} ${o2.y}`,
    `L ${i1.x} ${i1.y}`,
    `A ${innerR} ${innerR} 0 ${largeArc} 0 ${i2.x} ${i2.y}`,
    'Z',
  ].join(' ');
}

interface PlutchikWheelSVGProps {
  detectedEmotions: Set<string>;
  intensities: Record<string, number>;
}

function PlutchikWheelSVG({ detectedEmotions, intensities }: PlutchikWheelSVGProps) {
  const cx = 120;
  const cy = 120;
  const segments = 8;
  const sliceAngle = 360 / segments;

  return (
    <svg width="240" height="240" viewBox="0 0 240 240" className="mx-auto">
      {/* Background circle */}
      <circle cx={cx} cy={cy} r={115} fill="#09090b" />

      {PLUTCHIK_EMOTIONS.map((emotion) => {
        const isDetected = detectedEmotions.has(emotion.id);
        const intensity = intensities[emotion.id] ?? 0.5;
        const start = emotion.startAngle;
        const end = start + sliceAngle;

        // Three concentric rings: outer (low intensity), middle, inner (high)
        const rings = [
          { outerR: 110, innerR: 78, layer: 'outer' },
          { outerR: 75, innerR: 47, layer: 'middle' },
          { outerR: 44, innerR: 20, layer: 'inner' },
        ];

        return (
          <g key={emotion.id}>
            {rings.map(({ outerR, innerR, layer }) => {
              const isHighlighted =
                isDetected &&
                (layer === 'middle' ||
                  (layer === 'outer' && intensity >= 0.6) ||
                  (layer === 'inner' && intensity >= 0.85));

              const opacity = isDetected
                ? layer === 'outer'
                  ? 0.85
                  : layer === 'middle'
                  ? 0.65
                  : 0.45
                : layer === 'outer'
                ? 0.18
                : layer === 'middle'
                ? 0.12
                : 0.07;

              return (
                <path
                  key={layer}
                  d={arcPath(cx, cy, outerR, innerR, start, end)}
                  fill={emotion.color}
                  fillOpacity={isHighlighted ? opacity * 1.6 : opacity}
                  stroke="#09090b"
                  strokeWidth="1.5"
                  className="transition-all duration-500"
                />
              );
            })}

            {/* Label on outer ring */}
            {(() => {
              const midAngle = start + sliceAngle / 2;
              const labelR = 92;
              const pos = polarToCartesian(cx, cy, labelR, midAngle);
              const rotate = midAngle > 90 && midAngle < 270 ? midAngle - 90 + 180 : midAngle - 90;
              return (
                <text
                  x={pos.x}
                  y={pos.y}
                  textAnchor="middle"
                  dominantBaseline="middle"
                  fontSize="7.5"
                  fontWeight={isDetected ? '700' : '400'}
                  fill={isDetected ? emotion.textColor : '#71717a'}
                  transform={`rotate(${rotate}, ${pos.x}, ${pos.y})`}
                  className="select-none pointer-events-none transition-all duration-300"
                >
                  {emotion.label}
                </text>
              );
            })()}
          </g>
        );
      })}

      {/* Centre dot */}
      <circle cx={cx} cy={cy} r={18} fill="#18181b" stroke="#27272a" strokeWidth="1" />
      <text
        x={cx}
        y={cy}
        textAnchor="middle"
        dominantBaseline="middle"
        fontSize="7"
        fill="#52525b"
        className="select-none"
      >
        Plutchik
      </text>
    </svg>
  );
}

interface EmotionBadgeProps {
  emotion: PlutchikEmotion;
  intensity?: number;
  count?: number;
  actor?: string;
}

function EmotionBadge({ emotion, intensity, count, actor }: EmotionBadgeProps) {
  return (
    <div
      className="rounded-lg border px-3 py-2 space-y-1"
      style={{
        borderColor: `${emotion.color}40`,
        backgroundColor: `${emotion.color}18`,
      }}
    >
      <div className="flex items-center justify-between gap-2">
        <span className="text-xs font-bold" style={{ color: emotion.color }}>
          {emotion.label}
        </span>
        {count !== undefined && (
          <span className="text-[10px] text-zinc-500">×{count}</span>
        )}
      </div>
      {actor && <p className="text-[10px] text-zinc-500 truncate">{actor}</p>}
      {intensity !== undefined && (
        <div className="h-1 rounded-full bg-zinc-800/80 overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-500"
            style={{ width: `${Math.round(intensity * 100)}%`, backgroundColor: emotion.color }}
          />
        </div>
      )}
    </div>
  );
}

export function EmotionWheel({ workspaceId }: EmotionWheelProps) {
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await graphApi.getNodes(workspaceId, 'EmotionalState');
      setNodes(result.nodes);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load emotional state nodes');
    } finally {
      setLoading(false);
    }
  }, [workspaceId]);

  useEffect(() => {
    void load();
  }, [load]);

  // Parse emotion data from nodes
  interface ParsedEmotion {
    emotionId: string;
    plutchik?: PlutchikEmotion;
    rawLabel: string;
    intensity: number;
    actor: string;
    count: number;
  }

  const parsedEmotions: ParsedEmotion[] = [];
  const detectedEmotions = new Set<string>();
  const intensities: Record<string, number[]> = {};

  nodes.forEach((node) => {
    const p = node.properties;
    const rawLabel =
      (p.primary_emotion as string | undefined) ??
      (p.emotion as string | undefined) ??
      (p.emotion_type as string | undefined) ??
      node.name ??
      '';
    if (!rawLabel) return;

    const normId = normaliseEmotion(rawLabel);
    const plutchik = findPlutchik(normId);
    const intensity =
      typeof p.intensity === 'number'
        ? p.intensity
        : typeof p.intensity === 'string'
        ? parseFloat(p.intensity) || 0.5
        : 0.5;
    const actor =
      (p.actor_name as string | undefined) ??
      (p.actor as string | undefined) ??
      '';

    if (plutchik) {
      detectedEmotions.add(plutchik.id);
      if (!intensities[plutchik.id]) intensities[plutchik.id] = [];
      intensities[plutchik.id].push(intensity);
    }

    parsedEmotions.push({
      emotionId: plutchik?.id ?? normId,
      plutchik,
      rawLabel,
      intensity,
      actor,
      count: 1,
    });
  });

  // Aggregate: average intensity per emotion
  const avgIntensities: Record<string, number> = {};
  Object.entries(intensities).forEach(([k, vals]) => {
    avgIntensities[k] = vals.reduce((a, b) => a + b, 0) / vals.length;
  });

  // Group by emotionId for badge display
  const emotionGroups: Record<string, ParsedEmotion[]> = {};
  parsedEmotions.forEach((pe) => {
    if (!emotionGroups[pe.emotionId]) emotionGroups[pe.emotionId] = [];
    emotionGroups[pe.emotionId].push(pe);
  });

  const sortedGroups = Object.entries(emotionGroups).sort(([, a], [, b]) => b.length - a.length);

  return (
    <div className="rounded-xl border border-[#27272a] bg-[#18181b] p-5 space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between gap-3">
        <div className="space-y-0.5">
          <div className="flex items-center gap-2">
            <Heart className="w-4 h-4 text-zinc-400" />
            <span className="text-xs font-semibold uppercase tracking-widest text-zinc-400">
              Emotion Wheel
            </span>
          </div>
          <p className="text-sm text-zinc-400">Plutchik Model — detected emotional states</p>
        </div>
        <div className="flex items-center gap-2">
          {!loading && (
            <span className="text-xs text-zinc-500">
              {nodes.length} state{nodes.length !== 1 ? 's' : ''}
            </span>
          )}
          <button
            onClick={load}
            disabled={loading}
            className="p-1.5 rounded-lg border border-[#27272a] bg-zinc-900/50 text-zinc-400 hover:text-zinc-200 hover:border-zinc-600/60 transition-colors disabled:opacity-50"
            title="Refresh"
          >
            <RefreshCw className={['w-3.5 h-3.5', loading ? 'animate-spin' : ''].join(' ')} />
          </button>
        </div>
      </div>

      {/* Loading */}
      {loading && (
        <div className="flex flex-col items-center gap-4 py-4">
          <div className="w-48 h-48 rounded-full bg-zinc-800 animate-pulse" />
          <div className="grid grid-cols-4 gap-2 w-full">
            {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
              <div key={i} className="h-12 rounded-lg bg-zinc-800 animate-pulse" />
            ))}
          </div>
        </div>
      )}

      {/* Error */}
      {error && !loading && (
        <div className="rounded-lg border border-red-500/20 bg-red-500/5 px-4 py-3 flex items-start gap-2.5">
          <AlertCircle className="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <p className="text-sm font-medium text-red-400">Failed to load emotional state data</p>
            <p className="text-xs text-zinc-500">{error}</p>
            <button
              onClick={load}
              className="text-xs text-teal-400 hover:text-teal-300 font-medium transition-colors"
            >
              Try again
            </button>
          </div>
        </div>
      )}

      {/* Wheel + badges */}
      {!loading && !error && (
        <>
          {/* Wheel */}
          <div className="flex flex-col items-center gap-2">
            <PlutchikWheelSVG
              detectedEmotions={detectedEmotions}
              intensities={avgIntensities}
            />
            {nodes.length === 0 && (
              <p className="text-[11px] text-zinc-500 text-center">
                No EmotionalState nodes found — showing reference wheel
              </p>
            )}
            {nodes.length > 0 && detectedEmotions.size > 0 && (
              <p className="text-[11px] text-zinc-500 text-center">
                {detectedEmotions.size} emotion{detectedEmotions.size !== 1 ? 's' : ''} detected across{' '}
                {nodes.length} state record{nodes.length !== 1 ? 's' : ''}
              </p>
            )}
          </div>

          {/* Detected emotion badges */}
          {sortedGroups.length > 0 && (
            <div className="space-y-2">
              <p className="text-[10px] font-semibold uppercase tracking-widest text-zinc-500">
                Detected Emotions
              </p>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                {sortedGroups.map(([emotionId, group]) => {
                  const plutchik = findPlutchik(emotionId);
                  if (!plutchik) {
                    // Unknown/non-Plutchik emotion
                    return (
                      <div
                        key={emotionId}
                        className="rounded-lg border border-zinc-700/50 bg-zinc-800/50 px-3 py-2"
                      >
                        <span className="text-xs font-medium text-zinc-300 capitalize">
                          {emotionId}
                        </span>
                        <span className="ml-1 text-[10px] text-zinc-500">×{group.length}</span>
                      </div>
                    );
                  }
                  const avgInt = avgIntensities[plutchik.id];
                  const firstActor = group[0].actor;
                  return (
                    <EmotionBadge
                      key={emotionId}
                      emotion={plutchik}
                      intensity={avgInt}
                      count={group.length}
                      actor={firstActor || undefined}
                    />
                  );
                })}
              </div>
            </div>
          )}

          {/* All 8 Plutchik emotions palette */}
          <div className="border-t border-[#27272a] pt-3 space-y-2">
            <p className="text-[10px] font-semibold uppercase tracking-widest text-zinc-500">
              Plutchik Reference Palette
            </p>
            <div className="grid grid-cols-4 sm:grid-cols-8 gap-1.5">
              {PLUTCHIK_EMOTIONS.map((e) => {
                const isDetected = detectedEmotions.has(e.id);
                return (
                  <div
                    key={e.id}
                    className="rounded-lg px-2 py-1.5 text-center transition-all duration-300"
                    style={{
                      backgroundColor: `${e.color}${isDetected ? '30' : '12'}`,
                      borderWidth: '1px',
                      borderStyle: 'solid',
                      borderColor: `${e.color}${isDetected ? '60' : '25'}`,
                    }}
                  >
                    <p
                      className="text-[10px] font-semibold"
                      style={{ color: isDetected ? e.color : `${e.color}80` }}
                    >
                      {e.label}
                    </p>
                    {isDetected && (
                      <div
                        className="w-1.5 h-1.5 rounded-full mx-auto mt-1"
                        style={{ backgroundColor: e.color }}
                      />
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default EmotionWheel;
