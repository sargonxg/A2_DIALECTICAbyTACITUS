"use client";

import { Users } from "lucide-react";

const MOCK_USERS = [
  { id: "1", name: "Admin User", email: "admin@tacitus.ai", role: "admin", tenant: "default" },
  { id: "2", name: "Analyst A", email: "analyst@tacitus.ai", role: "analyst", tenant: "default" },
];

export default function UsersPage() {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-text-primary flex items-center gap-2"><Users size={20} /> Users</h2>
      <div className="card">
        <table className="w-full text-sm">
          <thead><tr className="text-text-secondary text-left"><th className="pb-2">Name</th><th className="pb-2">Email</th><th className="pb-2">Role</th><th className="pb-2">Tenant</th></tr></thead>
          <tbody>
            {MOCK_USERS.map((u) => (
              <tr key={u.id} className="border-t border-border">
                <td className="py-2 text-text-primary">{u.name}</td>
                <td className="py-2 text-text-secondary">{u.email}</td>
                <td className="py-2"><span className="badge bg-accent/10 text-accent">{u.role}</span></td>
                <td className="py-2 text-text-secondary">{u.tenant}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
