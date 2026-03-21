/**
 * Demo layout — overrides the root layout's sidebar/header by going
 * fixed full-screen with its own background.  This avoids restructuring
 * the existing route tree into route groups.
 */
export default function DemoLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="fixed inset-0 z-50 bg-background overflow-y-auto">
      {children}
    </div>
  );
}
