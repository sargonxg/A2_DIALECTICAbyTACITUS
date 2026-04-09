/**
 * Runtime configuration for DIALECTICA frontend.
 *
 * Priority order:
 * 1. window.__DIALECTICA_CONFIG__.apiUrl — injected by server-rendered layout.tsx
 *    (set from DIALECTICA_API_URL env var at request time)
 * 2. NEXT_PUBLIC_API_URL — build-time fallback (legacy, CI/CD compat)
 * 3. http://localhost:8080 — local development default
 */
export function getApiUrl(): string {
  if (
    typeof window !== "undefined" &&
    (window as unknown as { __DIALECTICA_CONFIG__?: { apiUrl?: string } })
      .__DIALECTICA_CONFIG__?.apiUrl
  ) {
    return (
      window as unknown as { __DIALECTICA_CONFIG__: { apiUrl: string } }
    ).__DIALECTICA_CONFIG__.apiUrl;
  }
  return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";
}
