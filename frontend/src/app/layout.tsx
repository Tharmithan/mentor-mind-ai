import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { AppShell } from "@/components/providers/AppShell";
import { ThemeProvider } from "@/components/providers/ThemeProvider";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "MentorMind AI — Your Personal AI Mentor",
  description:
    "Analyze performance, improve skills, and prepare for your future using AI-powered insights for learning, interviews, and career growth.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} h-full dark`} suppressHydrationWarning>
      <body className="min-h-full antialiased">
        <ThemeProvider>
          <AppShell>{children}</AppShell>
        </ThemeProvider>
      </body>
    </html>
  );
}
