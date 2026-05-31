"use client";

import { useEffect, useState } from "react";
import { Lightbulb, RefreshCw } from "lucide-react";
import { GlassCard } from "@/components/ui/GlassCard";
import { getDailyTip, type DailyTip } from "@/lib/api";
import { cachedFetch } from "@/lib/queryCache";

const FALLBACK: DailyTip = {
  tip: "Review one weak topic before learning something new — small daily wins compound into big results.",
  category: "study",
  focus_topic: null,
};

export function DailyAITip({ compact = false }: { compact?: boolean }) {
  const [tip, setTip] = useState<DailyTip>(FALLBACK);
  const [loading, setLoading] = useState(true);

  const load = () => {
    setLoading(true);
    cachedFetch("daily-tip", getDailyTip, 24 * 60_000)
      .then(setTip)
      .catch(() => setTip(FALLBACK))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  if (compact) {
    return (
      <p className="text-sm leading-relaxed text-slate-400">
        <Lightbulb className="mr-1.5 inline h-4 w-4 text-amber-400" />
        <span className="text-violet-300/90 font-medium">Daily tip: </span>
        {loading ? "Generating insight…" : tip.tip}
      </p>
    );
  }

  return (
    <GlassCard className="relative overflow-hidden p-5">
      <div className="pointer-events-none absolute -right-8 -top-8 h-32 w-32 rounded-full bg-amber-500/10 blur-2xl" />
      <div className="relative flex items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-amber-500/15 text-amber-400">
            <Lightbulb className="h-5 w-5" />
          </div>
          <div>
            <p className="text-xs font-medium uppercase tracking-wider text-amber-400/90">
              Daily AI Tip
              {tip.focus_topic && (
                <span className="ml-2 normal-case text-violet-300">
                  · {tip.focus_topic}
                </span>
              )}
            </p>
            <p className="mt-2 text-sm leading-relaxed text-slate-300">
              {loading ? (
                <span className="animate-pulse text-slate-500">Generating AI insight…</span>
              ) : (
                tip.tip
              )}
            </p>
          </div>
        </div>
        <button
          type="button"
          onClick={load}
          disabled={loading}
          className="shrink-0 rounded-lg p-2 text-slate-500 hover:bg-white/5 hover:text-violet-300 disabled:opacity-50"
          aria-label="Refresh daily tip"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
        </button>
      </div>
    </GlassCard>
  );
}
