"use client";

import { useState, useEffect } from "react";
import { Key, Eye, EyeOff, Save, Trash2, CheckCircle2, Info, ExternalLink } from "lucide-react";
import Link from "next/link";

export default function ApiKeysPage() {
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
        <p className="text-[#a1a1aa] text-sm">Manage your DIALECTICA API key for authentication.</p>
      </div>

      {/* Current key display */}
      <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-5 mb-6">
        <div className="flex items-center gap-2 mb-4">
          <Key size={16} className="text-[#71717a]" />
          <h2 className="text-[#fafafa] text-sm font-semibold">Current API Key</h2>
        </div>

        <div className="flex items-center gap-3 p-3 bg-[#09090b] border border-[#27272a] rounded-md mb-4">
          <Key size={14} className="text-[#52525b] flex-shrink-0" />
          <span className="text-sm font-mono text-[#a1a1aa] flex-1">
            {apiKey ? maskKey(apiKey) : <span className="text-[#52525b] italic">No key stored</span>}
          </span>
          {apiKey && (
            <span className="text-xs text-green-400 flex items-center gap-1">
              <CheckCircle2 size={12} /> Active
            </span>
          )}
        </div>

        {/* Update key */}
        <p className="text-[#71717a] text-xs mb-2">Update API Key</p>
        <div className="flex gap-2 mb-3">
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
              aria-label={showKey ? "Hide key" : "Show key"}
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
            title="Clear stored key"
          >
            <Trash2 size={14} />
            {cleared ? "Cleared" : "Clear"}
          </button>
        </div>

        <p className="text-[#52525b] text-xs">
          Keys are stored in <code className="font-mono text-[#71717a]">localStorage</code> under{" "}
          <code className="font-mono text-[#71717a]">dialectica_api_key</code> and sent as the{" "}
          <code className="font-mono text-[#71717a]">X-API-Key</code> header on every API request.
        </p>
      </div>

      {/* How to get a key */}
      <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-5 mb-6">
        <div className="flex items-center gap-2 mb-4">
          <Info size={16} className="text-[#71717a]" />
          <h2 className="text-[#fafafa] text-sm font-semibold">How to Get an API Key</h2>
        </div>
        <ol className="space-y-3 text-sm text-[#a1a1aa]">
          <li className="flex gap-3">
            <span className="flex-shrink-0 w-5 h-5 rounded-full bg-teal-600/20 border border-teal-600/30 text-teal-400 text-xs flex items-center justify-center font-mono">1</span>
            <span>Contact your DIALECTICA administrator or platform owner to request an API key.</span>
          </li>
          <li className="flex gap-3">
            <span className="flex-shrink-0 w-5 h-5 rounded-full bg-teal-600/20 border border-teal-600/30 text-teal-400 text-xs flex items-center justify-center font-mono">2</span>
            <span>
              For self-hosted deployments, generate a key via the backend admin CLI:{" "}
              <code className="font-mono text-[#fafafa] text-xs bg-[#09090b] border border-[#27272a] rounded px-1.5 py-0.5">
                dialectica-admin create-key --name my-key
              </code>
            </span>
          </li>
          <li className="flex gap-3">
            <span className="flex-shrink-0 w-5 h-5 rounded-full bg-teal-600/20 border border-teal-600/30 text-teal-400 text-xs flex items-center justify-center font-mono">3</span>
            <span>Paste the key in the field above and click Save. It will be used for all subsequent API calls.</span>
          </li>
          <li className="flex gap-3">
            <span className="flex-shrink-0 w-5 h-5 rounded-full bg-teal-600/20 border border-teal-600/30 text-teal-400 text-xs flex items-center justify-center font-mono">4</span>
            <span>Admin keys (with <code className="font-mono text-[#fafafa] text-xs bg-[#09090b] border border-[#27272a] rounded px-1.5 py-0.5">role=admin</code>) have full access. Analyst keys have read-only access to workspaces and analysis.</span>
          </li>
        </ol>
      </div>

      {/* Security note */}
      <div className="p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
        <div className="flex items-start gap-2">
          <Info size={14} className="text-yellow-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-yellow-400 text-sm font-medium mb-1">Security Notice</p>
            <p className="text-yellow-400/80 text-xs">
              API keys are stored in browser localStorage and sent in plaintext over HTTP. For production use, ensure your API endpoint uses HTTPS and rotate keys regularly. Never share your admin key.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
