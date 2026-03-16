import type { Metadata } from "next";
import { Instrument_Sans, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";

const instrumentSans = Instrument_Sans({
  subsets: ["latin"],
  variable: "--font-instrument-sans",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "DIALECTICA by TACITUS",
    template: "%s | DIALECTICA",
  },
  description:
    "The Universal Data Layer for Human Friction — Conflict intelligence platform by TACITUS.",
  icons: {
    icon: "/favicon.ico",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${instrumentSans.variable} ${jetbrainsMono.variable} bg-[#09090b] min-h-screen flex font-sans antialiased`}
      >
        {/* Fixed left sidebar */}
        <Sidebar />

        {/* Main content area — offset by sidebar width */}
        <div className="flex flex-col flex-1 min-w-0 ml-64">
          <Header />
          <main className="flex-1 overflow-auto">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
