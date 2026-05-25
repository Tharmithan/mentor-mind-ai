"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { GlassCard } from "@/components/ui/GlassCard";
import type { ExplainResponse } from "@/lib/types/api";
import { HelpCircle, Sparkles } from "lucide-react";

const barColor = (direction: string) =>
  direction === "negative" ? "#f43f5e" : direction === "positive" ? "#34d399" : "#8b5cf6";

export function AIExplanationPanel({ data }: { data: ExplainResponse | null }) {
  if (!data) return null;

  const chartData = data.contributions.slice(0, 6).map((c) => ({
    name: c.label,
    pct: c.contribution_pct,
    direction: c.direction,
  }));

  return (
    <GlassCard className="p-6">
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <HelpCircle className="h-5 w-5 text-cyan-400" />
          <h2 className="text-lg font-semibold text-white">Why this prediction?</h2>
        </div>
        <span className="rounded-full bg-cyan-500/15 px-2.5 py-0.5 text-xs text-cyan-300">
          {data.method.toUpperCase()}
        </span>
      </div>
      <p className="mt-1 text-sm text-slate-500">
        Explainable AI — SHAP & feature importance ({data.algorithm})
      </p>

      <p className="mt-4 rounded-xl border border-cyan-500/15 bg-cyan-500/5 px-4 py-3 text-sm text-slate-200">
        <Sparkles className="mr-1.5 inline h-4 w-4 text-cyan-400" />
        {data.summary}
      </p>

      <ul className="mt-4 space-y-2">
        {data.explanations.slice(1).map((line) => (
          <li key={line} className="flex items-start gap-2 text-sm text-slate-400">
            <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-violet-400" />
            {line}
          </li>
        ))}
      </ul>

      <div className="mt-6 h-56 w-full">
        <p className="mb-2 text-xs font-medium uppercase tracking-wider text-slate-500">
          Feature contribution %
        </p>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} layout="vertical" margin={{ left: 8, right: 16 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(139,92,246,0.1)" horizontal={false} />
            <XAxis type="number" domain={[0, 100]} tick={{ fill: "#94a3b8", fontSize: 11 }} unit="%" />
            <YAxis
              type="category"
              dataKey="name"
              width={110}
              tick={{ fill: "#94a3b8", fontSize: 11 }}
            />
            <Tooltip
              contentStyle={{
                background: "rgba(15,10,30,0.95)",
                border: "1px solid rgba(139,92,246,0.3)",
                borderRadius: 12,
              }}
              formatter={(v) => [`${Number(v ?? 0)}%`, "Contribution"]}
            />
            <Bar dataKey="pct" radius={[0, 6, 6, 0]}>
              {chartData.map((entry) => (
                <Cell key={entry.name} fill={barColor(entry.direction)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </GlassCard>
  );
}
