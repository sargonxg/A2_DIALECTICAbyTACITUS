"use client";

import { Package } from "lucide-react";

const SDKS = [
  { lang: "Python", install: "pip install dialectica", badge: "PyPI", color: "#3572A5" },
  { lang: "JavaScript", install: "npm install @tacitus/dialectica", badge: "npm", color: "#f7df1e" },
];

export default function SDKsPage() {
  return (
    <div className="max-w-3xl space-y-6">
      <h1 className="text-2xl font-bold text-text-primary flex items-center gap-2"><Package size={24} /> SDKs</h1>
      <p className="text-text-secondary">Official client libraries for the DIALECTICA API.</p>

      {SDKS.map((sdk) => (
        <div key={sdk.lang} className="card space-y-3">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full" style={{ backgroundColor: sdk.color }} />
            <h3 className="font-semibold text-text-primary">{sdk.lang}</h3>
          </div>
          <pre className="bg-background rounded p-3 text-sm font-mono text-accent">{sdk.install}</pre>
          <pre className="bg-background rounded p-3 text-sm font-mono text-text-primary">{sdk.lang === "Python"
? `from dialectica import Client

client = Client(api_key="your-key")
workspaces = client.workspaces.list()
print(workspaces)`
: `import { Dialectica } from '@tacitus/dialectica';

const client = new Dialectica({ apiKey: 'your-key' });
const workspaces = await client.workspaces.list();
console.log(workspaces);`}</pre>
        </div>
      ))}
    </div>
  );
}
