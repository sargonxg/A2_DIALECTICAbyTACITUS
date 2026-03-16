"use client";

import { useState, useEffect } from "react";
import { UsageCharts } from "@/components/admin/UsageCharts";
import { Key, Eye, EyeOff, Save, CheckCircle2 } from "lucide-react";

export default function UsagePage() {
  const [apiKey, setApiKey] = useState("");
  const [inputKey, setInputKey] = useState("");
  const [showKey, setShowKey] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem("dialectica_api_key") || "";
    setApiKey(stored);
    setInputKey(stored);
  }, []);

  function maskKey(key: string): string {
    if (!key) return "";
    if (key.length <= 4) return "****";
    return "****" + key.slice(-4);
  }

  function handleSave() {
    localStorage.setItem("dialectica_api_key", inputKey);
    setApiKey(inputKey);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  }

  return (
    <div className="p-8 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-[#fafafa] mb-1">Usage</h1>
        <p className="text-[#a1a1aa] text-sm">API usage statistics and key configuration.</p>
      </div>

      {/* API Key section */}
      <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-5 mb-8">
        <div className="flex items-center gap-2 mb-4">
          <Key size={16} className="text-[#71717a]" />
          <h2 className="text-[#fafafa] text-sm font-semibold">API Key</h2>
        </div>

        <div className="mb-3">
          <p className="text-[#71717a] text-xs mb-1">Current Key</p>
          <p className="text-[#a1a1aa] text-sm font-mono bg-[#09090b] border border-[#27272a] rounded px-3 py-1.5">
            {apiKey ? maskKey(apiKey) : <span className="text-[#52525b]">Not set</span>}
          </p>
        </div>

        <div className="flex gap-2">
          <div className="relative flex-1">
            <input
              type={showKey ? "text" : "password"}
              value={inputKey}
              onChange={(e) => setInputKey(e.target.value)}
              placeholder="Enter API key…"
              className="w-full bg-[#09090b] border border-[#27272a] rounded-md px-3 py-2 pr-10 text-sm text-[#fafafa] placeholder-[#52525b] font-mono focus:outline-none focus:border-teal-600"
            />
            <button
              type="button"
              onClick={() => setShowKey((v) => !v)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-[#52525b] hover:text-[#a1a1aa] transition-colors"
              aria-label={showKey ? "Hide key" : "Show key"}
            >
              {showKey ? <EyeOff size={14} /> : <Eye size={14} />}
            </button>
          </div>
          <button
            onClick={handleSave}
            className="flex items-center gap-1.5 px-4 py-2 rounded-md bg-teal-600/20 hover:bg-teal-600/30 border border-teal-600/30 text-teal-400 text-sm transition-colors"
          >
            {saved ? <CheckCircle2 size={14} /> : <Save size={14} />}
            {saved ? "Saved" : "Save"}
          </button>
        </div>
      </div>

      {/* Charts */}
      <UsageCharts />
    </div>
  );
}
