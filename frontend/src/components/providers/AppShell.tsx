"use client";

import { FloatingAIAssistant } from "@/components/ai/FloatingAIAssistant";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <>
      {children}
      <FloatingAIAssistant />
    </>
  );
}
