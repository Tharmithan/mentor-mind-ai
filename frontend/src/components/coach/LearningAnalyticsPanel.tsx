"use client";

import dynamic from "next/dynamic";
import { useEffect, useState } from "react";
import {
  Activity,
  AlertTriangle,
  BarChart3,
  Clock,
  Loader2,
  TrendingUp,
  Zap,
} from "lucide-react";
import { getLearningAnalytics } from "@/lib/api";
import type { LearningAnalyticsDashboard } from "@/lib/types/api";
import { GlassCard } from "@/components/ui/GlassCard";
import { ChartSkeleton } from "@/components/charts/ChartSkeleton";
import { Markdown } from "@/components/assistant/Markdown";

const PerformanceLineChart = dynamic(
  () => import("@/components/charts/PerformanceLineChart").then((m) => m.PerformanceLineChart),
  { ssr: false, loading: () => <ChartSkeleton /> }
);

const StudyAnalyticsChart = dynamic(
  () => import("@/components/charts/StudyAnalyticsChart").then((m) => m.StudyAnalyticsChart),
  { ssr: false, loading: () => <ChartSkeleton /> }
);

const DEMO_USER = "demo-user-001";

const MASTERY_COLORS: Record<string, string> = {
  mastered: "text-emerald-400 bg-emerald-500/10 border-emerald-500/25",
  proficient: "text-blue-400 bg-blue-500/10 border-blue-500/25",
  developing: "text-amber-400 bg-amber-500/10 border-amber-500/25",
  beginner: "text-slate-400 bg-slate-500/10 border-slate-500/25",
};

const INSIGHT_ICONS: Record<string, typeof Zap> = {
  study_time: Clock,
  productivity: Zap,
  weakness: AlertTriangle,
  burnout: Activity,
  growth: TrendingUp,
};

export function LearningAnalyticsPanel() {
  const [data, setData] = useState<LearningAnalyticsDashboard | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getLearningAnalytics(DEMO_USER)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <GlassCard className="flex items-center gap-3 p-6">
        <Loader2 className="h-5 w-5 animate-spin text-violet-400" />
        <span className="text-sm text-slate-400">Analyzing learning patterns…</span>
      </GlassCard>
    );
  }

  if (!data) return null;

  return (
    <GlassCard className="p-6">
      <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
        <div className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5 text-violet-400" />
          <div>
            <h2 className="text-lg font-semibold text-white">AI Learning Analytics</h2>
            <p className="text-xs text-slate-500">
              <Markdown text={data.summary} />
            </p>
          </div>
        </div>
        <div className="flex gap-3">
          <ScorePill label="Efficiency" value={data.learning_efficiency} suffix="%" />
          <ScorePill label="Productivity" value={data.productivity_score} suffix="/100" />
        </div>
      </div>

      <div className="mb-6 grid gap-4 lg:grid-cols-2">
        <div className="rounded-xl border border-violet-500/10 bg-slate-900/30 p-4">
          <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
            Weekly growth
          </p>
          <PerformanceLineChart data={data.weekly_growth} />
        </div>
        <div className="rounded-xl border border-violet-500/10 bg-slate-900/30 p-4">
          <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
            Study hours by day
          </p>
          <StudyAnalyticsChart
            data={data.study_hours_by_day.map((d) => ({ day: d.label, hours: d.value }))}
          />
        </div>
      </div>

      <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
        Subject mastery
      </p>
      <div className="mb-6 grid gap-2 sm:grid-cols-2">
        {data.subject_mastery.map((m) => (
          <div
            key={m.subject}
            className="flex items-center justify-between rounded-lg border border-white/5 bg-slate-900/40 px-4 py-3"
          >
            <div>
              <p className="text-sm font-medium text-white">{m.subject}</p>
              <span
                className={`mt-1 inline-block rounded border px-2 py-0.5 text-[10px] font-semibold uppercase ${
                  MASTERY_COLORS[m.mastery_level] ?? MASTERY_COLORS.beginner
                }`}
              >
                {m.mastery_level}
              </span>
            </div>
            <div className="text-right">
              <p className="text-lg font-bold text-white">{m.score}%</p>
              <p
                className={`text-xs ${
                  m.trend === "up"
                    ? "text-emerald-400"
                    : m.trend === "down"
                      ? "text-rose-400"
                      : "text-slate-500"
                }`}
              >
                {m.trend === "up" ? "↑" : m.trend === "down" ? "↓" : "→"} {m.delta >= 0 ? "+" : ""}
                {m.delta}
              </p>
            </div>
          </div>
        ))}
      </div>

      <div className="mb-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <PatternCard
          label="Best study time"
          value={data.patterns.best_study_time}
          sub={data.patterns.best_study_days.join(", ")}
        />
        <PatternCard
          label="Burnout risk"
          value={data.patterns.burnout_level}
          sub={`${data.patterns.burnout_risk}% index`}
          warn={data.patterns.burnout_level !== "low"}
        />
        <PatternCard
          label="Weak areas"
          value={String(data.patterns.weak_learning_areas.length)}
          sub={data.patterns.weak_learning_areas.slice(0, 2).join(", ") || "None"}
        />
        <PatternCard
          label="Progress trend"
          value={`${data.progress_trends.at(-1)?.value ?? 0}%`}
          sub={`Δ ${data.progress_trends.length} weeks`}
        />
      </div>

      <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
        AI insights
      </p>
      <div className="space-y-2">
        {data.insights.map((insight, i) => {
          const Icon = INSIGHT_ICONS[insight.category] ?? Zap;
          const border =
            insight.severity === "warning"
              ? "border-amber-500/20 bg-amber-500/5"
              : insight.severity === "success"
                ? "border-emerald-500/20 bg-emerald-500/5"
                : "border-violet-500/10 bg-slate-900/40";
          return (
            <div key={i} className={`flex gap-3 rounded-xl border p-4 ${border}`}>
              <Icon className="mt-0.5 h-4 w-4 shrink-0 text-violet-400" />
              <div>
                <p className="text-sm font-medium text-white">{insight.title}</p>
                <div className="mt-1 text-xs text-slate-400">
                  <Markdown text={insight.description} />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </GlassCard>
  );
}

function ScorePill({
  label,
  value,
  suffix,
}: {
  label: string;
  value: number;
  suffix: string;
}) {
  return (
    <div className="rounded-xl border border-violet-500/20 bg-violet-500/10 px-4 py-2 text-center">
      <p className="text-[10px] uppercase tracking-wide text-violet-300">{label}</p>
      <p className="text-xl font-bold text-white">
        {Math.round(value)}
        <span className="text-sm font-normal text-slate-400">{suffix}</span>
      </p>
    </div>
  );
}

function PatternCard({
  label,
  value,
  sub,
  warn,
}: {
  label: string;
  value: string;
  sub: string;
  warn?: boolean;
}) {
  return (
    <div
      className={`rounded-xl border p-3 ${
        warn ? "border-amber-500/20 bg-amber-500/5" : "border-white/5 bg-slate-900/40"
      }`}
    >
      <p className="text-[10px] uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 text-sm font-semibold capitalize text-white">{value}</p>
      <p className="mt-0.5 truncate text-[11px] text-slate-500">{sub}</p>
    </div>
  );
}
