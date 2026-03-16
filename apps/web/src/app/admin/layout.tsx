"use client";

import { Shield } from "lucide-react";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 border-b border-border pb-3">
        <Shield size={20} className="text-danger" />
        <h1 className="text-lg font-bold text-text-primary">Administration</h1>
      </div>
      {children}
    </div>
  );
}
