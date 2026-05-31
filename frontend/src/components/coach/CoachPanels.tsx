"use client";

import Link from "next/link";
import { ArrowRight, Sparkles, Trophy, AlertCircle, CalendarDays } from "lucide-react";
import { GlassCard } from "@/components/ui/GlassCard";
import { Markdown } from "@/components/assistant/Markdown";
import type { CoachRecommendation, WeeklyProgressReport } from "@/lib/types/api";

const AGENT_COLORS: Record<string, string> = {
  career: "text-emerald-400",
  study: "text-blue-400",
  interview: "text-amber-400",
  resume: "text-rose-400",
};

export function RecommendationsPanel({
  recommendations,
}: {
  recommendations: CoachRecommendation[];
}) {
  return (
    <GlassCard className="p-6">
      <div className="mb-4 flex items-center gap-2">
        <Sparkles className="h-5 w-5 text-violet-400" />
        <h2 className="text-lg font-semibold text-white">AI Recommendations</h2>
      </div>
      <div className="space-y-3">
        {recommendations.map((rec) => (
          <div
            key={rec.id}
            className="group rounded-xl border border-violet-500/10 bg-slate-900/40 p-4 transition hover:border-violet-500/25"
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className={`text-[10px] font-semibold uppercase ${AGENT_COLORS[rec.agent] ?? "text-violet-400"}`}>
                  {rec.agent} agent · {rec.priority}
                </p>
                <p className="mt-1 font-medium text-white">{rec.title}</p>
                <p className="mt-1 text-sm text-slate-400">{rec.description}</p>
              </div>
              {rec.action_path && (
                <Link
                  href={rec.action_path}
                  className="shrink-0 rounded-lg p-2 text-slate-500 transition hover:bg-violet-500/10 hover:text-violet-300"
                  aria-label={`Go to ${rec.title}`}
                >
                  <ArrowRight className="h-4 w-4" />
                </Link>
              )}
            </div>
          </div>
        ))}
      </div>
    </GlassCard>
  );
}

export function WeeklyReportPanel({ report }: { report: WeeklyProgressReport }) {
  return (
    <GlassCard className="p-6">
      <div className="mb-6 flex items-center gap-2">
        <CalendarDays className="h-5 w-5 text-violet-400" />
        <div>
          <h2 className="text-lg font-semibold text-white">AI Weekly Progress Report</h2>
          <p className="text-xs text-slate-500">{report.week_label}</p>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-xl border border-emerald-500/15 bg-emerald-500/5 p-4">
          <div className="mb-3 flex items-center gap-2 text-emerald-400">
            <Trophy className="h-4 w-4" />
            <span className="text-xs font-semibold uppercase tracking-wide">Achievements</span>
          </div>
          <ul className="space-y-2">
            {report.achievements.map((a, i) => (
              <li key={i} className="text-sm text-slate-300">
                <Markdown text={a} />
              </li>
            ))}
          </ul>
        </div>

        <div className="rounded-xl border border-amber-500/15 bg-amber-500/5 p-4">
          <div className="mb-3 flex items-center gap-2 text-amber-400">
            <AlertCircle className="h-4 w-4" />
            <span className="text-xs font-semibold uppercase tracking-wide">Weaknesses</span>
          </div>
          <ul className="space-y-2">
            {report.weaknesses.map((w, i) => (
              <li key={i} className="text-sm text-slate-300">
                <Markdown text={w} />
              </li>
            ))}
          </ul>
        </div>

        <div className="rounded-xl border border-violet-500/15 bg-violet-500/5 p-4">
          <div className="mb-3 flex items-center gap-2 text-violet-400">
            <CalendarDays className="h-4 w-4" />
            <span className="text-xs font-semibold uppercase tracking-wide">Next Week&apos;s Plan</span>
          </div>
          <ul className="space-y-2">
            {report.next_week_plan.map((p, i) => (
              <li key={i} className="text-sm text-slate-300">
                <Markdown text={p} />
              </li>
            ))}
          </ul>
        </div>
      </div>
    </GlassCard>
  );
}
