"use client";

import { useEffect, useState } from "react";
import { Brain, Loader2, TrendingDown, TrendingUp } from "lucide-react";
import { getMemoryProgress } from "@/lib/api";
import type { MemoryProgressResponse } from "@/lib/types/api";
import { GlassCard } from "@/components/ui/GlassCard";
import { Markdown } from "@/components/assistant/Markdown";

const DEMO_USER = "demo-user-001";

export function MemoryProgressPanel() {
  const [data, setData] = useState<MemoryProgressResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMemoryProgress(DEMO_USER)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <GlassCard className="flex items-center gap-3 p-6">
        <Loader2 className="h-5 w-5 animate-spin text-violet-400" />
        <span className="text-sm text-slate-400">Loading long-term memory…</span>
      </GlassCard>
    );
  }

  if (!data) return null;

  return (
    <GlassCard className="p-6">
      <div className="mb-4 flex items-center gap-2">
        <Brain className="h-5 w-5 text-violet-400" />
        <div>
          <h2 className="text-lg font-semibold text-white">Long-Term Memory</h2>
          <p className="text-xs text-slate-500">
            Compared to {data.month_comparison} · {data.snapshots_count} snapshots
          </p>
        </div>
      </div>

      <div className="mb-5 rounded-xl border border-violet-500/20 bg-violet-500/5 p-4">
        <p className="text-sm text-slate-200">
          <Markdown text={data.narrative} />
        </p>
      </div>

      <div className="space-y-2">
        {data.deltas.slice(0, 5).map((d) => (
          <div
            key={d.subject}
            className="flex items-center justify-between rounded-lg border border-white/5 bg-slate-900/40 px-4 py-3"
          >
            <div>
              <p className="text-sm font-medium text-white">{d.subject}</p>
              <p className="text-xs text-slate-500">
                {d.previous_score}% → {d.current_score}%
              </p>
            </div>
            <div className="flex items-center gap-2">
              {d.delta >= 0 ? (
                <TrendingUp className="h-4 w-4 text-emerald-400" />
              ) : (
                <TrendingDown className="h-4 w-4 text-rose-400" />
              )}
              <span
                className={`text-sm font-semibold ${
                  d.delta >= 0 ? "text-emerald-400" : "text-rose-400"
                }`}
              >
                {d.delta >= 0 ? "+" : ""}
                {d.delta_pct.toFixed(0)}%
              </span>
            </div>
          </div>
        ))}
      </div>
    </GlassCard>
  );
}
