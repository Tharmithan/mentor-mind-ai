"use client";

import dynamic from "next/dynamic";
import { GlassCard } from "@/components/ui/GlassCard";
import { ChartSkeleton } from "@/components/charts/ChartSkeleton";
import type { CoachCharts } from "@/lib/types/api";

const PerformanceLineChart = dynamic(
  () => import("@/components/charts/PerformanceLineChart").then((m) => m.PerformanceLineChart),
  { ssr: false, loading: () => <ChartSkeleton /> }
);

type ChartPoint = { label: string; value: number };

function ChartPanel({ title, subtitle, data }: { title: string; subtitle: string; data: ChartPoint[] }) {
  return (
    <GlassCard className="p-5">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-white">{title}</h3>
        <p className="text-xs text-slate-500">{subtitle}</p>
      </div>
      <PerformanceLineChart data={data} />
    </GlassCard>
  );
}

export function CoachChartsGrid({ charts }: { charts: CoachCharts }) {
  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <ChartPanel
        title="Skill Growth"
        subtitle="Average proficiency trend over 5 weeks"
        data={charts.skill_growth}
      />
      <ChartPanel
        title="Learning Progress"
        subtitle="Performance score by week"
        data={charts.learning_progress}
      />
      <ChartPanel
        title="Interview Improvement"
        subtitle="Mock interview scores over time"
        data={charts.interview_improvement}
      />
      <ChartPanel
        title="Career Readiness Trend"
        subtitle="Readiness for target role"
        data={charts.career_readiness_trend}
      />
    </div>
  );
}
