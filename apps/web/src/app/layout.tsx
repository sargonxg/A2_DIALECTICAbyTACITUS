import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";

export const metadata: Metadata = {
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
      <head>
        <script dangerouslySetInnerHTML={{ __html: `window.__DIALECTICA_CONFIG__=${JSON.stringify({ apiUrl })}` }} />
      </head>
      <body className="min-h-screen bg-background">
        <Providers>
          <div className="flex h-screen overflow-hidden">
            <Sidebar />
            <div className="flex flex-col flex-1 overflow-hidden">
              <Header />
              <main className="flex-1 overflow-y-auto p-6">{children}</main>
            </div>
          </div>
        </Providers>
      </body>
    </html>
  );
}
