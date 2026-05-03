import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";
import AppFrame from "@/components/layout/AppFrame";

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || "https://dialectica.tacitus.me"),
  title: {
    default: "DIALECTICA by TACITUS",
    template: "%s | DIALECTICA",
  },
  description: "Transform any conflict into a computable knowledge graph grounded in 30+ academic frameworks.",
  openGraph: {
    type: "website",
    siteName: "DIALECTICA by TACITUS",
    title: "DIALECTICA — Make Conflict Computable",
    description: "From workplace disputes to geopolitical crises — structured intelligence in seconds.",
    images: [{ url: "/og-image.png", width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    title: "DIALECTICA by TACITUS",
    description: "Transform any conflict into a computable knowledge graph.",
    images: ["/og-image.png"],
  },
  robots: { index: true, follow: true },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const apiUrl = process.env.DIALECTICA_API_URL || "";
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-background">
        {/* Inject runtime config before any client JS executes */}
        <script
          dangerouslySetInnerHTML={{
            __html: `window.__DIALECTICA_CONFIG__=${JSON.stringify({ apiUrl })}`,
          }}
        />
        <Providers>
          <AppFrame>{children}</AppFrame>
        </Providers>
      </body>
    </html>
  );
}
