'use client';

import React from 'react';
import {
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Maximize2,
  Network,
  AlignCenter,
  Circle,
} from 'lucide-react';

interface GraphControlsProps {
  onZoomIn: () => void;
  onZoomOut: () => void;
  onReset: () => void;
  onFitView: () => void;
  selectedLayout: string;
  onLayoutChange: (layout: string) => void;
}

const LAYOUTS = [
  { id: 'force-directed', label: 'Force', icon: Network },
  { id: 'hierarchical',   label: 'Hierarchical', icon: AlignCenter },
  { id: 'circular',       label: 'Circular', icon: Circle },
];

function ControlButton({
  onClick,
  title,
  children,
}: {
  onClick: () => void;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      title={title}
      className={[
        'flex items-center justify-center w-9 h-9 rounded-md',
        'text-zinc-400 hover:text-white hover:bg-white/10',
        'transition-colors duration-150 focus:outline-none focus:ring-1 focus:ring-teal-600/50',
      ].join(' ')}
    >
      {children}
    </button>
  );
}

export function GraphControls({
  onZoomIn,
  onZoomOut,
  onReset,
  onFitView,
  selectedLayout,
  onLayoutChange,
}: GraphControlsProps) {
  return (
    <div className="flex flex-col gap-1 rounded-xl border border-[#27272a] bg-[#18181b] p-2 shadow-xl">
      {/* Zoom controls */}
      <ControlButton onClick={onZoomIn} title="Zoom in">
        <ZoomIn className="w-4 h-4" />
      </ControlButton>
      <ControlButton onClick={onZoomOut} title="Zoom out">
        <ZoomOut className="w-4 h-4" />
      </ControlButton>

      {/* Divider */}
      <div className="my-0.5 h-px bg-[#27272a]" />

      {/* Fit / Reset */}
      <ControlButton onClick={onFitView} title="Fit to view">
        <Maximize2 className="w-4 h-4" />
      </ControlButton>
      <ControlButton onClick={onReset} title="Reset view">
        <RotateCcw className="w-4 h-4" />
      </ControlButton>

      {/* Divider */}
      <div className="my-0.5 h-px bg-[#27272a]" />

      {/* Layout selector */}
      <div className="flex flex-col gap-0.5">
        {LAYOUTS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => onLayoutChange(id)}
            title={label}
            className={[
              'flex items-center justify-center w-9 h-9 rounded-md transition-colors duration-150',
              'focus:outline-none focus:ring-1 focus:ring-teal-600/50',
              selectedLayout === id
                ? 'bg-teal-600/20 text-teal-400 ring-1 ring-teal-600/40'
                : 'text-zinc-400 hover:text-white hover:bg-white/10',
            ].join(' ')}
          >
            <Icon className="w-4 h-4" />
          </button>
        ))}
      </div>

      {/* Layout label tooltip area */}
      <div className="px-1 pt-0.5">
        <p className="text-[9px] text-center uppercase tracking-widest text-zinc-600 font-medium">
          {LAYOUTS.find((l) => l.id === selectedLayout)?.label ?? 'Layout'}
        </p>
      </div>
    </div>
  );
}

export default GraphControls;
