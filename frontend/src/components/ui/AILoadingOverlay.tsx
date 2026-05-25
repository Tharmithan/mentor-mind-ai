"use client";

import { useEffect, useState } from "react";
import { Brain } from "lucide-react";

const DEFAULT_MESSAGES = [
  "Analyzing performance…",
  "Generating AI insights…",
  "Preparing your dashboard…",
];

export function AILoadingOverlay({
  loading,
  messages = DEFAULT_MESSAGES,
}: {
  loading: boolean;
  messages?: string[];
}) {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    if (!loading) return;
    const id = setInterval(() => {
      setIndex((i) => (i + 1) % messages.length);
    }, 2200);
    return () => clearInterval(id);
  }, [loading, messages.length]);

  if (!loading) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-[#030712]/85 backdrop-blur-sm"
      role="status"
      aria-live="polite"
      aria-label="Loading dashboard"
    >
      <div className="glass mx-4 max-w-sm rounded-2xl px-8 py-10 text-center animate-fade-in">
        <div className="relative mx-auto mb-6 flex h-16 w-16 items-center justify-center">
          <span className="absolute inset-0 rounded-full bg-violet-500/20 animate-ping" />
          <span className="absolute inset-0 rounded-full border border-violet-500/40 animate-pulse-glow" />
          <div className="relative flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-br from-violet-600 to-blue-600">
            <Brain className="h-7 w-7 text-white" />
          </div>
        </div>
        <p className="text-lg font-semibold text-white">{messages[index]}</p>
        <div className="mt-4 flex justify-center gap-1.5">
          {[0, 1, 2].map((i) => (
            <span
              key={i}
              className="h-2 w-2 rounded-full bg-violet-400 animate-pulse"
              style={{ animationDelay: `${i * 200}ms` }}
            />
          ))}
        </div>
        <p className="mt-4 text-xs text-slate-500">Powered by MentorMind AI</p>
      </div>
    </div>
  );
}
