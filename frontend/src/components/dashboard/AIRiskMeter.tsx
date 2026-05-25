"use client";

import { GlassCard } from "@/components/ui/GlassCard";
import type { RiskMeter } from "@/lib/types/api";
import { Activity, Brain, Flame } from "lucide-react";

function riskColor(value: number) {
  if (value >= 65) return { bar: "bg-rose-500", text: "text-rose-300", glow: "shadow-rose-500/30" };
  if (value >= 40) return { bar: "bg-amber-500", text: "text-amber-300", glow: "shadow-amber-500/30" };
  return { bar: "bg-emerald-500", text: "text-emerald-300", glow: "shadow-emerald-500/30" };
}

function RiskBar({
  label,
  value,
  icon,
}: {
  label: string;
  value: number;
  icon: React.ReactNode;
}) {
  const colors = riskColor(value);
  return (
    <div className="rounded-xl border border-violet-500/10 bg-slate-900/50 p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm font-medium text-slate-300">
          {icon}
          {label}
        </div>
        <span className={`text-lg font-bold tabular-nums ${colors.text}`}>{Math.round(value)}%</span>
      </div>
      <div className="mt-3 h-2.5 overflow-hidden rounded-full bg-slate-800">
        <div
          className={`h-full rounded-full transition-all duration-700 ${colors.bar} shadow-lg ${colors.glow}`}
          style={{ width: `${Math.min(100, value)}%` }}
        />
      </div>
      <p className="mt-2 text-xs text-slate-500">
        {value >= 65 ? "High risk — take action this week" : value >= 40 ? "Moderate — monitor closely" : "Low risk — keep habits"}
      </p>
    </div>
  );
}

const FALLBACK: RiskMeter = {
  burnout_risk: 42,
  exam_failure_risk: 28,
  low_engagement_score: 35,
};

export function AIRiskMeter({ meter }: { meter?: RiskMeter | null }) {
  const m = meter ?? FALLBACK;

  return (
    <GlassCard className="p-6">
      <div className="flex items-center gap-2">
        <Activity className="h-5 w-5 text-rose-400" />
        <h2 className="text-lg font-semibold text-white">AI Risk Meter</h2>
      </div>
      <p className="mt-1 text-sm text-slate-500">
        ML-derived risk signals — burnout, exam failure, and engagement
      </p>
      <div className="mt-5 grid gap-4 sm:grid-cols-3">
        <RiskBar
          label="Burnout risk"
          value={m.burnout_risk}
          icon={<Flame className="h-4 w-4 text-orange-400" />}
        />
        <RiskBar
          label="Exam failure risk"
          value={m.exam_failure_risk}
          icon={<Brain className="h-4 w-4 text-violet-400" />}
        />
        <RiskBar
          label="Low engagement"
          value={m.low_engagement_score}
          icon={<Activity className="h-4 w-4 text-cyan-400" />}
        />
      </div>
    </GlassCard>
  );
}
