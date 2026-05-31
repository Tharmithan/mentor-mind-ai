"use client";

import dynamic from "next/dynamic";

const FloatingAIAssistant = dynamic(
  () =>
    import("@/components/ai/FloatingAIAssistant").then((m) => m.FloatingAIAssistant),
  { ssr: false }
);

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <>
      {children}
      <FloatingAIAssistant />
    </>
  );
}
