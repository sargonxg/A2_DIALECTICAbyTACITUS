"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import { Settings, ChevronRight } from "lucide-react";
import { useEffect, useState } from "react";

interface Crumb {
  label: string;
  href: string;
}

const ROUTE_LABELS: Record<string, string> = {
  "": "Dashboard",
  workspaces: "Workspaces",
  ask: "Ask",
  theory: "Theory",
  explore: "Explore",
  compare: "Compare",
  developers: "Developers",
  admin: "Admin",
  new: "New",
  graph: "Graph",
  analysis: "Analysis",
  timeline: "Timeline",
  actors: "Actors",
  causal: "Causal Chain",
  ingest: "Ingest",
  settings: "Settings",
  docs: "Documentation",
  keys: "API Keys",
  playground: "Playground",
  sdks: "SDKs",
  examples: "Examples",
  "api-keys": "API Keys",
  extraction: "Extraction",
  users: "Users",
  usage: "Usage",
  data: "Data",
  "graph-health": "Graph Health",
  system: "System",
  ontology: "Ontology",
};

function buildBreadcrumbs(pathname: string): Crumb[] {
  const segments = pathname.split("/").filter(Boolean);
  const crumbs: Crumb[] = [{ label: "Dashboard", href: "/" }];

  let href = "";
  for (const segment of segments) {
    href += `/${segment}`;
    const isUuid =
      /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/.test(
        segment,
      );
    const label = isUuid
      ? "Workspace"
      : (ROUTE_LABELS[segment] ?? segment.charAt(0).toUpperCase() + segment.slice(1));
    crumbs.push({ label, href });
  }

  return crumbs;
}

export function Header() {
  const pathname = usePathname();
  const crumbs = buildBreadcrumbs(pathname);

  const [apiKeySet, setApiKeySet] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);

  useEffect(() => {
    const check = () => {
      const key = localStorage.getItem("dialectica_api_key");
      setApiKeySet(!!key && key.trim().length > 0);
    };
    check();
    window.addEventListener("storage", check);
    return () => window.removeEventListener("storage", check);
  }, []);

  function handleSettingsClick() {
    setSettingsOpen((prev) => !prev);
  }

  function handleApiKeyChange(e: React.ChangeEvent<HTMLInputElement>) {
    const value = e.target.value.trim();
    if (value) {
      localStorage.setItem("dialectica_api_key", value);
    } else {
      localStorage.removeItem("dialectica_api_key");
    }
    setApiKeySet(!!value);
    window.dispatchEvent(new Event("storage"));
  }

  return (
    <header className="h-14 bg-[#18181b] border-b border-[#27272a] flex items-center justify-between px-6 sticky top-0 z-30">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-1.5 text-sm" aria-label="Breadcrumb">
        {crumbs.map((crumb, index) => {
          const isLast = index === crumbs.length - 1;
          return (
            <span key={crumb.href} className="flex items-center gap-1.5">
              {index > 0 && (
                <ChevronRight size={14} className="text-[#52525b]" aria-hidden="true" />
              )}
              {isLast ? (
                <span className="text-[#fafafa] font-medium">{crumb.label}</span>
              ) : (
                <Link
                  href={crumb.href}
                  className="text-[#a1a1aa] hover:text-[#fafafa] transition-colors"
                >
                  {crumb.label}
                </Link>
              )}
            </span>
          );
        })}
      </nav>

      {/* Right side controls */}
      <div className="flex items-center gap-3">
        {/* API key status indicator */}
        <div className="flex items-center gap-2">
          <div
            className={`w-2 h-2 rounded-full ${
              apiKeySet ? "bg-green-500" : "bg-[#52525b]"
            }`}
            title={apiKeySet ? "API key configured" : "No API key set"}
            aria-hidden="true"
          />
          <span className="text-[#a1a1aa] text-xs">
            {apiKeySet ? "API key set" : "No API key"}
          </span>
        </div>

        {/* Settings button */}
        <div className="relative">
          <button
            onClick={handleSettingsClick}
            className="p-1.5 rounded-md text-[#a1a1aa] hover:text-[#fafafa] hover:bg-[#27272a] transition-colors"
            title="Settings"
            aria-label="Open settings"
          >
            <Settings size={16} />
          </button>

          {/* Inline settings popover for API key */}
          {settingsOpen && (
            <>
              {/* Backdrop */}
              <div
                className="fixed inset-0 z-40"
                onClick={() => setSettingsOpen(false)}
                aria-hidden="true"
              />
              <div className="absolute right-0 top-9 z-50 w-80 bg-[#18181b] border border-[#27272a] rounded-lg shadow-xl p-4">
                <h3 className="text-[#fafafa] text-sm font-semibold mb-3">
                  Settings
                </h3>
                <div className="space-y-3">
                  <div>
                    <label
                      htmlFor="api-key-input"
                      className="block text-[#a1a1aa] text-xs mb-1.5"
                    >
                      API Key
                    </label>
                    <input
                      id="api-key-input"
                      type="password"
                      defaultValue={
                        typeof window !== "undefined"
                          ? localStorage.getItem("dialectica_api_key") ?? ""
                          : ""
                      }
                      onChange={handleApiKeyChange}
                      placeholder="Enter your API key..."
                      className="w-full bg-[#09090b] border border-[#27272a] rounded-md px-3 py-1.5 text-sm text-[#fafafa] placeholder-[#52525b] focus:outline-none focus:border-teal-600 transition-colors"
                    />
                    <p className="text-[#52525b] text-xs mt-1">
                      Stored locally in your browser. Never sent to third parties.
                    </p>
                  </div>
                  <div className="pt-1 border-t border-[#27272a]">
                    <p className="text-[#a1a1aa] text-xs">
                      DIALECTICA API:{" "}
                      <span className="font-mono text-[#fafafa]">
                        {process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080"}
                      </span>
                    </p>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
