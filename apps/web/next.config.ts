import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  experimental: {
    reactCompiler: false,
  },
  env: {
    INTERNAL_API_URL:
      process.env.DIALECTICA_API_URL ||
      process.env.NEXT_PUBLIC_API_URL ||
      "http://localhost:8080",
  },
  // Proxy API calls to the backend (avoids CORS in production)
  async rewrites() {
    const apiUrl =
      process.env.DIALECTICA_API_URL ||
      process.env.NEXT_PUBLIC_API_URL ||
      "http://localhost:8080";
    return [
      {
        source: "/api/v1/:path*",
        destination: `${apiUrl}/v1/:path*`,
      },
      {
        source: "/api/health",
        destination: `${apiUrl}/health`,
      },
    ];
  },
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "X-Frame-Options", value: "DENY" },
          { key: "X-XSS-Protection", value: "1; mode=block" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
        ],
      },
    ];
  },
  images: {
    remotePatterns: [],
  },
};

export default nextConfig;
