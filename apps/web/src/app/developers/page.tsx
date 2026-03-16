"use client";

import Link from "next/link";
import {
  BookOpen,
  Code2,
  Puzzle,
  FlaskConical,
  Package,
  ArrowRight,
  Terminal,
  ExternalLink,
} from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

const SNIPPET = `// Fetch all workspaces
const res = await fetch('${API_URL}/v1/workspaces', {
  headers: { 'X-API-Key': 'your-api-key' }
});
const { workspaces } = await res.json();

// Analyze a conflict
const analysis = await fetch(
  \`\${API_URL}/v1/workspaces/\${id}/analyze\`,
  {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': 'your-api-key',
    },
    body: JSON.stringify({ query: 'What are the main escalation drivers?', mode: 'escalation' }),
  }
);`;

const PORTAL_LINKS = [
  {
    label: "API Reference",
    href: "/developers/docs",
    icon: BookOpen,
    description: "Full endpoint documentation with request/response schemas",
    color: "text-blue-400",
    bg: "bg-blue-500/10",
  },
  {
    label: "Playground",
    href: "/developers/playground",
    icon: FlaskConical,
    description: "Interactive API explorer — make live requests",
    color: "text-green-400",
    bg: "bg-green-500/10",
  },
  {
    label: "Code Examples",
    href: "/developers/examples",
    icon: Code2,
    description: "Python, JavaScript, and cURL samples",
    color: "text-yellow-400",
    bg: "bg-yellow-500/10",
  },
  {
    label: "SDKs & Clients",
    href: "/developers/sdks",
    icon: Package,
    description: "Official Python and TypeScript client libraries",
    color: "text-purple-400",
    bg: "bg-purple-500/10",
  },
  {
    label: "API Keys",
    href: "/developers/keys",
    icon: Puzzle,
    description: "Set your API key for authenticated requests",
    color: "text-teal-400",
    bg: "bg-teal-500/10",
  },
];

export default function DeveloperPortalPage() {
  return (
    <div className="p-8 max-w-5xl">
      <div className="mb-10">
        <div className="flex items-center gap-2 mb-3">
          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-teal-600/20 text-teal-400 border border-teal-600/30 tracking-wider uppercase">
            Developer
          </span>
        </div>
        <h1 className="text-3xl font-bold text-[#fafafa] mb-2">Developer Portal</h1>
        <p className="text-[#a1a1aa] text-base max-w-2xl">
          Build conflict intelligence applications on top of DIALECTICA. Access the REST API, 
          explore documentation, and download client SDKs.
        </p>
      </div>

      {/* Quick access cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-12">
        {PORTAL_LINKS.map((link) => {
          const Icon = link.icon;
          return (
            <Link
              key={link.href}
              href={link.href}
              className="group bg-[#18181b] border border-[#27272a] rounded-lg p-5 hover:border-[#3f3f46] transition-colors"
            >
              <div className={`p-2 rounded-md ${link.bg} inline-flex mb-3`}>
                <Icon size={18} className={link.color} />
              </div>
              <div className="flex items-center justify-between mb-1">
                <p className="text-[#fafafa] text-sm font-semibold">{link.label}</p>
                <ArrowRight
                  size={14}
                  className="text-[#52525b] group-hover:text-[#a1a1aa] transition-colors"
                />
              </div>
              <p className="text-[#71717a] text-xs leading-relaxed">{link.description}</p>
            </Link>
          );
        })}
      </div>

      {/* Quick start snippet */}
      <div className="mb-10">
        <div className="flex items-center gap-2 mb-4">
          <Terminal size={16} className="text-[#71717a]" />
          <h2 className="text-[#fafafa] font-semibold text-sm">Quick Start</h2>
        </div>
        <div className="bg-[#09090b] border border-[#27272a] rounded-lg overflow-hidden">
          <div className="flex items-center gap-2 px-4 py-2.5 border-b border-[#27272a] bg-[#18181b]">
            <div className="w-2.5 h-2.5 rounded-full bg-[#3f3f46]" />
            <div className="w-2.5 h-2.5 rounded-full bg-[#3f3f46]" />
            <div className="w-2.5 h-2.5 rounded-full bg-[#3f3f46]" />
            <span className="text-[#52525b] text-xs ml-2 font-mono">JavaScript / TypeScript</span>
          </div>
          <pre className="p-4 text-xs font-mono text-[#a1a1aa] overflow-x-auto leading-relaxed">
            <code>{SNIPPET}</code>
          </pre>
        </div>
      </div>

      {/* API Base URL */}
      <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-5 mb-8">
        <h2 className="text-[#fafafa] font-semibold text-sm mb-3">API Base URL</h2>
        <div className="flex items-center gap-3 p-3 bg-[#09090b] border border-[#27272a] rounded-md">
          <code className="text-teal-400 text-sm font-mono flex-1">{API_URL}</code>
        </div>
        <p className="text-[#52525b] text-xs mt-2">
          Set the <code className="font-mono text-[#71717a]">NEXT_PUBLIC_API_URL</code> environment variable to override.
        </p>
      </div>

      {/* REST overview */}
      <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-5">
        <h2 className="text-[#fafafa] font-semibold text-sm mb-4">REST API Overview</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
          {[
            { label: "Authentication", value: "X-API-Key header" },
            { label: "Format", value: "JSON (application/json)" },
            { label: "Streaming", value: "SSE (text/event-stream) for /analyze" },
            { label: "Versioning", value: "/v1/ prefix on all endpoints" },
            { label: "Error Format", value: '{ "detail": "message" }' },
            { label: "Rate Limiting", value: "Per API key, configurable" },
          ].map((item) => (
            <div key={item.label} className="flex items-start gap-2">
              <span className="text-[#52525b] text-xs w-28 flex-shrink-0 pt-0.5">{item.label}</span>
              <code className="text-[#a1a1aa] text-xs font-mono">{item.value}</code>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
