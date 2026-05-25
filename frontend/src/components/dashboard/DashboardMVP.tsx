"use client";

import { useEffect, useState } from "react";
import { StatCard } from "@/components/ui/Card";
import { GlassCard } from "@/components/ui/GlassCard";
import { AnimatedSection } from "@/components/ui/AnimatedSection";
import {
  LineChartCard,
  BarChartCard,
  PieChartCard,
} from "@/components/dashboard/DashboardCharts";
import { getDashboard, type DashboardData } from "@/lib/api";
import {
  TrendingUp,
  Clock,
  AlertTriangle,
  Sparkles,
  ArrowRight,
  AlertCircle,
} from "lucide-react";

const priorityDot = {
  high: "bg-rose-400",
  medium: "bg-amber-400",
  low: "bg-emerald-400",
} as const;

const FALLBACK: DashboardData = {
  performance_score: 82,
  study_hours_week: 28.5,
  weak_subjects: [{ subject: "Data Structures", score: 62 }],
  ai_suggestions_count: 2,
  study_hours_by_day: [
    { label: "Mon", value: 2.5 },
    { label: "Tue", value: 4 },
    { label: "Wed", value: 3 },
    { label: "Thu", value: 5 },
    { label: "Fri", value: 3.5 },
    { label: "Sat", value: 6 },
    { label: "Sun", value: 4.5 },
  ],
  performance_trend: [
    { label: "W1", value: 68 },
    { label: "W2", value: 72 },
    { label: "W3", value: 75 },
    { label: "W4", value: 78 },
    { label: "W5", value: 82 },
  ],
  subject_distribution: [
    { label: "Mathematics", value: 91 },
    { label: "Programming", value: 78 },
    { label: "Data Structures", value: 62 },
  ],
  recommendations: [
    {
      id: "1",
      title: "Review Data Structures — Trees & Graphs",
      description: "Weak topic detected from last quiz (62%)",
      topic: "Data Structures",
      priority: "high",
      is_completed: false,
    },
    {
      id: "2",
      title: "Schedule mock technical interview",
      description: "Last interview score: 3.8/5 — room to improve",
      topic: "Interview",
      priority: "medium",
      is_completed: false,
    },
  ],
};

export function DashboardMVP() {
  const [data, setData] = useState<DashboardData>(FALLBACK);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDashboard()
      .then(setData)
      .catch(() => setData(FALLBACK))
      .finally(() => setLoading(false));
  }, []);

  const topWeak = data.weak_subjects[0];
  const weakLabel = topWeak
    ? `${topWeak.subject} (${Math.round(topWeak.score)}%)`
    : "None detected";
  const pendingRecs = data.recommendations.filter((r) => !r.is_completed);

  return (
    <>
      <div
        className={`stagger-children grid gap-4 sm:grid-cols-2 xl:grid-cols-4 ${loading ? "opacity-70" : ""}`}
      >
        <StatCard
          label="Performance Score"
          value={`${Math.round(data.performance_score)}%`}
          sub="Average across subjects"
          trend="up"
          icon={<TrendingUp className="h-5 w-5" />}
        />
        <StatCard
          label="Study Hours"
          value={`${data.study_hours_week}h`}
          sub="Total this week"
          trend="up"
          icon={<Clock className="h-5 w-5" />}
        />
        <StatCard
          label="Weak Subjects"
          value={data.weak_subjects.length > 0 ? String(data.weak_subjects.length) : "0"}
          sub={weakLabel}
          trend={data.weak_subjects.length > 0 ? "down" : "neutral"}
          icon={<AlertTriangle className="h-5 w-5 text-amber-400" />}
        />
        <StatCard
          label="AI Suggestions"
          value={String(data.ai_suggestions_count)}
          sub={
            data.ai_suggestions_count === 1
              ? "1 new suggestion"
              : `${data.ai_suggestions_count} new suggestions`
          }
          trend="neutral"
          icon={<Sparkles className="h-5 w-5 text-violet-300" />}
        />
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-3">
        <AnimatedSection delay={100}>
          <GlassCard className="p-6">
            <h2 className="text-lg font-semibold text-white">Performance Trend</h2>
            <p className="mt-1 text-sm text-slate-500">Weekly score progression</p>
            <div className="mt-4">
              <LineChartCard data={data.performance_trend} />
            </div>
          </GlassCard>
        </AnimatedSection>

        <AnimatedSection delay={200}>
          <GlassCard className="p-6">
            <h2 className="text-lg font-semibold text-white">Study Hours</h2>
            <p className="mt-1 text-sm text-slate-500">Daily breakdown</p>
            <div className="mt-4">
              <BarChartCard
                data={data.study_hours_by_day.map((d) => ({
                  day: d.label,
                  hours: d.value,
                }))}
              />
            </div>
          </GlassCard>
        </AnimatedSection>

        <AnimatedSection delay={300}>
          <GlassCard className="p-6">
            <h2 className="text-lg font-semibold text-white">Subject Scores</h2>
            <p className="mt-1 text-sm text-slate-500">Performance by topic</p>
            <div className="mt-4">
              <PieChartCard data={data.subject_distribution} />
            </div>
          </GlassCard>
        </AnimatedSection>
      </div>

      <AnimatedSection delay={400} className="mt-8">
        <GlassCard className="p-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">AI Suggestions</h2>
            <span className="rounded-full bg-violet-500/20 px-2.5 py-0.5 text-xs text-violet-300">
              {pendingRecs.length} active
            </span>
          </div>
          <ul className="mt-5 space-y-4">
            {pendingRecs.length === 0 ? (
              <li className="text-sm text-slate-500">You are all caught up — great work!</li>
            ) : (
              pendingRecs.map((rec) => (
                <li
                  key={rec.id}
                  className="rounded-xl border border-violet-500/10 bg-slate-900/40 p-4 transition-all duration-200 hover:border-violet-500/25"
                >
                  <div className="flex items-start gap-3">
                    <span
                      className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${
                        priorityDot[rec.priority as keyof typeof priorityDot] ??
                        priorityDot.medium
                      }`}
                    />
                    <div className="min-w-0 flex-1">
                      <p className="font-medium text-white">{rec.title}</p>
                      <p className="mt-1 flex items-start gap-1 text-sm text-slate-500">
                        <AlertCircle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
                        {rec.description}
                      </p>
                      <button
                        type="button"
                        className="mt-2 inline-flex items-center gap-1 text-sm font-medium text-violet-400 hover:text-violet-300"
                      >
                        View suggestion
                        <ArrowRight className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  </div>
                </li>
              ))
            )}
          </ul>
        </GlassCard>
      </AnimatedSection>
    </>
  );
}
