"use client";

import { useEffect, useState } from "react";
import { GlassCard } from "@/components/ui/GlassCard";
import { getAIInsights } from "@/lib/api";
import type { AIInsight, InsightsResponse } from "@/lib/types/api";
import { Brain, TrendingDown, TrendingUp, Minus } from "lucide-react";

const severityStyle = {
  positive: "border-emerald-500/20 bg-emerald-500/5",
  warning: "border-amber-500/20 bg-amber-500/5",
  info: "border-violet-500/15 bg-slate-900/40",
} as const;

function TrendIcon({ direction }: { direction?: string | null }) {
  if (direction === "up") return <TrendingUp className="h-4 w-4 text-emerald-400" />;
  if (direction === "down") return <TrendingDown className="h-4 w-4 text-amber-400" />;
  return <Minus className="h-4 w-4 text-slate-500" />;
}

function InsightRow({ insight }: { insight: AIInsight }) {
  const style = severityStyle[insight.severity as keyof typeof severityStyle] ?? severityStyle.info;
  return (
    <li className={`rounded-xl border p-4 ${style}`}>
      <div className="flex items-start gap-3">
        <TrendIcon direction={insight.trend_direction} />
        <div>
          <p className="text-sm text-slate-200">{insight.message}</p>
          <p className="mt-1 text-xs capitalize text-slate-500">
            {insight.category.replace(/_/g, " ")}
            {insight.impact_pct != null && ` · ${insight.impact_pct}% impact`}
          </p>
        </div>
      </div>
    </li>
  );
}

export function AIInsightsPanel() {
  const [data, setData] = useState<InsightsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAIInsights()
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <GlassCard className="p-6">
        <p className="text-sm text-slate-500">Analyzing your performance trends…</p>
      </GlassCard>
    );
  }

  if (!data) return null;

  const { performance_summary: summary } = data;

  return (
    <GlassCard className="p-6">
      <div className="flex items-center gap-2">
        <Brain className="h-5 w-5 text-violet-400" />
        <h2 className="text-lg font-semibold text-white">AI Insights</h2>
      </div>
      <p className="mt-1 text-sm font-medium text-violet-300">{summary.headline}</p>
      <p className="mt-1 text-sm text-slate-500">{summary.summary_text}</p>

      {data.trends.length > 0 && (
        <div className="mt-4">
          <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
            Trend analysis
          </p>
          <ul className="mt-2 space-y-2">
            {data.trends.map((ins) => (
              <InsightRow key={ins.id} insight={ins} />
            ))}
          </ul>
        </div>
      )}

      <div className="mt-5">
        <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
          Personalized & cohort insights
        </p>
        <ul className="mt-2 space-y-2">
          {data.insights
            .filter((i) => !data.trends.some((t) => t.id === i.id))
            .slice(0, 5)
            .map((ins) => (
              <InsightRow key={ins.id} insight={ins} />
            ))}
        </ul>
      </div>
    </GlassCard>
  );
}
