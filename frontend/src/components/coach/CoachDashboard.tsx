"use client";

import { useEffect, useState } from "react";
import { AlertCircle, RefreshCw } from "lucide-react";
import { getCoachOverview } from "@/lib/api";
import type { CoachOverviewResponse } from "@/lib/types/api";
import { AILoadingOverlay } from "@/components/ui/AILoadingOverlay";
import { AnimatedSection } from "@/components/ui/AnimatedSection";
import { CoachScoreCards } from "@/components/coach/CoachScoreCards";
import { CoachChartsGrid } from "@/components/coach/CoachChartsGrid";
import { SkillGapPanel } from "@/components/coach/SkillGapPanel";
import { RecommendationsPanel, WeeklyReportPanel } from "@/components/coach/CoachPanels";
import { PersonalizationPanel } from "@/components/coach/PersonalizationPanel";
import { MemoryProgressPanel } from "@/components/coach/MemoryProgressPanel";

export function CoachDashboard() {
  const [data, setData] = useState<CoachOverviewResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const sessionId =
        typeof window !== "undefined" ? localStorage.getItem("agent_session_id") : null;
      const res = await getCoachOverview({
        target_career: "AI Engineer",
        session_id: sessionId ?? undefined,
      });
      setData(res);
    } catch {
      setError("Could not load AI Coach dashboard. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  if (loading && !data) {
    return (
      <AILoadingOverlay
        loading
        messages={["Analyzing your scores…", "Running skill gap analysis…", "Building AI Coach dashboard…"]}
      />
    );
  }

  if (error && !data) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 rounded-2xl border border-red-500/20 bg-red-500/5 p-12 text-center">
        <AlertCircle className="h-10 w-10 text-red-400" />
        <p className="text-sm text-red-300">{error}</p>
        <button
          type="button"
          onClick={load}
          className="inline-flex items-center gap-2 rounded-lg bg-violet-600 px-4 py-2 text-sm text-white hover:bg-violet-500"
        >
          <RefreshCw className="h-4 w-4" /> Retry
        </button>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="space-y-8 pb-12">
      <AnimatedSection>
        <div className="relative overflow-hidden rounded-2xl border border-violet-500/20 bg-gradient-to-br from-violet-950/80 via-[#0f0a1e] to-blue-950/60 p-6 sm:p-8">
          <div className="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-violet-600/10 blur-3xl" />
          <div className="absolute -bottom-16 -left-16 h-48 w-48 rounded-full bg-blue-600/10 blur-3xl" />
          <div className="relative">
            <p className="text-xs font-semibold uppercase tracking-widest text-violet-400">
              Week 6 · AI Coach
            </p>
            <h2 className="mt-2 text-2xl font-bold text-white sm:text-3xl">
              Your Career Intelligence Hub
            </h2>
            <p className="mt-2 max-w-2xl text-sm text-slate-400">{data.profile_summary}</p>
            <p className="mt-3 inline-flex rounded-full border border-violet-500/25 bg-violet-500/10 px-3 py-1 text-xs font-medium text-violet-200">
              Target: {data.target_career}
            </p>
          </div>
        </div>
      </AnimatedSection>

      <AnimatedSection delay={0.05}>
        <CoachScoreCards scores={data.scores} />
      </AnimatedSection>

      <AnimatedSection delay={0.1}>
        <CoachChartsGrid charts={data.charts} />
      </AnimatedSection>

      <AnimatedSection delay={0.12}>
        <PersonalizationPanel />
      </AnimatedSection>

      <AnimatedSection delay={0.13}>
        <MemoryProgressPanel />
      </AnimatedSection>

      <AnimatedSection delay={0.15}>
        <SkillGapPanel skillGap={data.skill_gap} />
      </AnimatedSection>

      <AnimatedSection delay={0.2}>
        <WeeklyReportPanel report={data.weekly_report} />
      </AnimatedSection>

      <AnimatedSection delay={0.25}>
        <RecommendationsPanel recommendations={data.recommendations} />
      </AnimatedSection>
    </div>
  );
}
