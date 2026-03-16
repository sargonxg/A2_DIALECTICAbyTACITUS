"use client";

import { useEffect, useState } from "react";
import { Key, Eye, EyeOff, Save, Trash2, CheckCircle2, ArrowRight } from "lucide-react";
import Link from "next/link";

export default function DeveloperKeysPage() {
  const [apiKey, setApiKey] = useState("");
  const [inputKey, setInputKey] = useState("");
  const [showKey, setShowKey] = useState(false);
  const [saved, setSaved] = useState(false);
  const [cleared, setCleared] = useState(false);

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
    const trimmed = inputKey.trim();
    localStorage.setItem("dialectica_api_key", trimmed);
    setApiKey(trimmed);
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  }

  function handleClear() {
    localStorage.removeItem("dialectica_api_key");
    setApiKey("");
    setInputKey("");
    setCleared(true);
    setTimeout(() => setCleared(false), 2500);
  }

  return (
    <div className="p-8 max-w-3xl">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-[#fafafa] mb-1">API Keys</h1>
        <p className="text-[#a1a1aa] text-sm">
          Set your DIALECTICA API key to authenticate requests in the playground and SDK examples.
        </p>
      </div>

      {/* Key manager */}
      <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-5 mb-6">
        <div className="flex items-center gap-2 mb-4">
          <Key size={16} className="text-[#71717a]" />
          <h2 className="text-[#fafafa] text-sm font-semibold">Your API Key</h2>
          {apiKey && (
            <span className="ml-auto flex items-center gap-1 text-green-400 text-xs">
              <CheckCircle2 size={12} /> Active
            </span>
          )}
        </div>

        <div className="flex items-center gap-3 p-3 bg-[#09090b] border border-[#27272a] rounded-md mb-4">
          <Key size={13} className="text-[#52525b] flex-shrink-0" />
          <span className="text-sm font-mono text-[#a1a1aa] flex-1">
            {apiKey ? maskKey(apiKey) : <span className="text-[#52525b] italic">No key stored</span>}
          </span>
        </div>

        <p className="text-[#71717a] text-xs mb-2">Set / Update Key</p>
        <div className="flex gap-2 mb-4">
          <div className="relative flex-1">
            <input
              type={showKey ? "text" : "password"}
              value={inputKey}
              onChange={(e) => setInputKey(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSave()}
              placeholder="dk_live_…"
              className="w-full bg-[#09090b] border border-[#27272a] rounded-md px-3 py-2 pr-10 text-sm text-[#fafafa] placeholder-[#52525b] font-mono focus:outline-none focus:border-teal-600"
            />
            <button
              type="button"
              onClick={() => setShowKey((v) => !v)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-[#52525b] hover:text-[#a1a1aa] transition-colors"
            >
              {showKey ? <EyeOff size={14} /> : <Eye size={14} />}
            </button>
          </div>
          <button
            onClick={handleSave}
            disabled={!inputKey.trim()}
            className="flex items-center gap-1.5 px-4 py-2 rounded-md bg-teal-600/20 hover:bg-teal-600/30 border border-teal-600/30 text-teal-400 text-sm transition-colors disabled:opacity-50"
          >
            {saved ? <CheckCircle2 size={14} /> : <Save size={14} />}
            {saved ? "Saved!" : "Save"}
          </button>
          <button
            onClick={handleClear}
            disabled={!apiKey}
            className="flex items-center gap-1.5 px-3 py-2 rounded-md bg-red-500/10 hover:bg-red-500/20 border border-red-500/20 text-red-400 text-sm transition-colors disabled:opacity-50"
          >
            <Trash2 size={14} />
            {cleared ? "Cleared" : "Clear"}
          </button>
        </div>

        <p className="text-[#52525b] text-xs">
          Stored in <code className="font-mono text-[#71717a]">localStorage</code> as{" "}
          <code className="font-mono text-[#71717a]">dialectica_api_key</code>. Sent as{" "}
          <code className="font-mono text-[#71717a]">X-API-Key</code> header on all requests.
        </p>
      </div>

      {/* Link to full admin key management */}
      <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-5">
        <p className="text-[#71717a] text-sm mb-3">
          For full API key management (rotation, multiple keys, role assignment), visit the Admin panel.
        </p>
        <Link
          href="/admin/api-keys"
          className="inline-flex items-center gap-1.5 px-4 py-2 rounded-md bg-[#27272a] hover:bg-[#3f3f46] text-[#a1a1aa] hover:text-[#fafafa] text-sm transition-colors"
        >
          <Key size={14} />
          Admin API Keys
          <ArrowRight size={12} />
        </Link>
      </div>
    </div>
  );
}
