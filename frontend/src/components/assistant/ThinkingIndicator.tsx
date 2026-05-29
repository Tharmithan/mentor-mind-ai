"use client";

import { useEffect, useState } from "react";
import { Sparkles } from "lucide-react";

const PHRASES = [
  "Analyzing lecture materials…",
  "Searching your notes…",
  "Connecting concepts…",
  "Composing an answer…",
];

export function ThinkingIndicator() {
  const [phrase, setPhrase] = useState(0);

  useEffect(() => {
    const id = setInterval(() => setPhrase((p) => (p + 1) % PHRASES.length), 1400);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="flex items-center gap-2 rounded-2xl rounded-tl-sm bg-white/5 px-4 py-3 text-sm text-slate-400">
      <Sparkles className="h-4 w-4 animate-pulse text-violet-400" />
      <span>{PHRASES[phrase]}</span>
      <span className="flex gap-1">
        <Dot delay="0ms" />
        <Dot delay="150ms" />
        <Dot delay="300ms" />
      </span>
    </div>
  );
}

function Dot({ delay }: { delay: string }) {
  return (
    <span
      className="h-1.5 w-1.5 animate-bounce rounded-full bg-violet-400"
      style={{ animationDelay: delay }}
    />
  );
}
