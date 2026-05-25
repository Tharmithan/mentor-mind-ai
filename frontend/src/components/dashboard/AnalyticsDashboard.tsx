"use client";

import dynamic from "next/dynamic";
import { GlassCard } from "@/components/ui/GlassCard";
import { AnimatedSection } from "@/components/ui/AnimatedSection";
import { StatCard } from "@/components/ui/Card";
import { LineChartCard } from "@/components/dashboard/DashboardCharts";
import { AIRiskMeter } from "@/components/dashboard/AIRiskMeter";
import { ChartSkeleton } from "@/components/charts/ChartSkeleton";
import type { AnalyticsDashboard as AnalyticsData } from "@/lib/types/api";
import {
  Brain,
  Flame,
  TrendingUp,
  Calendar,
  BarChart3,
  LineChart,
} from "lucide-react";

const SubjectComparisonChart = dynamic(
  () =>
    import("@/components/charts/SubjectComparisonChart").then((m) => m.SubjectComparisonChart),
  { ssr: false, loading: () => <ChartSkeleton /> }
);

const ConfidenceTrendChart = dynamic(
  () =>
    import("@/components/charts/ConfidenceTrendChart").then((m) => m.ConfidenceTrendChart),
  { ssr: false, loading: () => <ChartSkeleton /> }
);

const riskBadge: Record<string, string> = {
  low: "text-emerald-400",
  medium: "text-amber-400",
  high: "text-rose-400",
};

export function AnalyticsDashboard({ analytics }: { analytics: AnalyticsData | null | undefined }) {
  if (!analytics) return null;

  const { cards, risk_meter, weekly_progress, subject_comparison, confidence_trends } = analytics;
  const trendSign = cards.performance_trend_delta >= 0 ? "+" : "";

  return (
    <section className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-white">Analytics Dashboard</h2>
        <p className="mt-1 text-sm text-slate-500">Recharts + Chart.js · live ML analytics</p>
      </div>

      <div className="stagger-children grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="AI Score"
          value={`${Math.round(cards.ai_score)}%`}
          sub="Model performance index"
          trend="up"
          icon={<Brain className="h-5 w-5 text-violet-400" />}
        />
        <StatCard
          label="Risk Level"
          value={cards.risk_level.toUpperCase()}
          sub="Overall student risk"
          trend={cards.risk_level === "high" ? "down" : cards.risk_level === "low" ? "up" : "neutral"}
          icon={<Flame className={`h-5 w-5 ${riskBadge[cards.risk_level] ?? "text-amber-400"}`} />}
        />
        <StatCard
          label="Performance Trend"
          value={`${trendSign}${cards.performance_trend_delta}%`}
          sub="vs last week"
          trend={cards.performance_trend_delta >= 0 ? "up" : "down"}
          icon={<TrendingUp className="h-5 w-5" />}
        />
        <StatCard
          label="Study Streak"
          value={`${cards.study_streak_days}d`}
          sub="Consecutive study days"
          trend="up"
          icon={<Calendar className="h-5 w-5 text-cyan-400" />}
        />
      </div>

      <AnimatedSection delay={50}>
        <AIRiskMeter meter={risk_meter} />
      </AnimatedSection>

      <div className="grid gap-6 lg:grid-cols-3">
        <AnimatedSection delay={100}>
          <GlassCard className="p-6">
            <div className="flex items-center gap-2">
              <LineChart className="h-4 w-4 text-violet-400" />
              <h3 className="font-semibold text-white">Weekly Progress</h3>
            </div>
            <p className="mt-1 text-xs text-slate-500">Recharts · performance over time</p>
            <div className="mt-4">
              <LineChartCard data={weekly_progress} />
            </div>
          </GlassCard>
        </AnimatedSection>

        <AnimatedSection delay={150}>
          <GlassCard className="p-6">
            <div className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4 text-indigo-400" />
              <h3 className="font-semibold text-white">Subject Comparison</h3>
            </div>
            <p className="mt-1 text-xs text-slate-500">Chart.js · scores by topic</p>
            <div className="mt-4">
              <SubjectComparisonChart data={subject_comparison} />
            </div>
          </GlassCard>
        </AnimatedSection>

        <AnimatedSection delay={200}>
          <GlassCard className="p-6">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-cyan-400" />
              <h3 className="font-semibold text-white">Confidence Trends</h3>
            </div>
            <p className="mt-1 text-xs text-slate-500">Chart.js · model certainty</p>
            <div className="mt-4">
              <ConfidenceTrendChart data={confidence_trends} />
            </div>
          </GlassCard>
        </AnimatedSection>
      </div>
    </section>
  );
}
