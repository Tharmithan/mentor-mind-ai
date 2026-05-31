"use client";

import Link from "next/link";
import { ArrowRight, CheckCircle2, AlertTriangle, Zap } from "lucide-react";
import { GlassCard } from "@/components/ui/GlassCard";
import type { SkillGapOverview } from "@/lib/types/api";

const PRIORITY_COLORS = {
  high: "bg-rose-500/15 text-rose-300 border-rose-500/25",
  medium: "bg-amber-500/15 text-amber-300 border-amber-500/25",
  low: "bg-emerald-500/15 text-emerald-300 border-emerald-500/25",
};

export function SkillGapPanel({ skillGap }: { skillGap: SkillGapOverview }) {
  return (
    <GlassCard className="p-6">
      <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-white">Skill Gap Analyzer</h2>
          <p className="mt-1 text-sm text-slate-400">
            Target role: <span className="text-violet-300">{skillGap.target_career}</span>
            {" · "}
            {skillGap.overall_readiness.toFixed(0)}% ready
          </p>
        </div>
        <Link
          href="/planner"
          className="inline-flex items-center gap-1.5 rounded-lg border border-violet-500/25 bg-violet-500/10 px-3 py-1.5 text-xs font-medium text-violet-200 hover:bg-violet-500/20"
        >
          View roadmap <ArrowRight className="h-3.5 w-3.5" />
        </Link>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-4">
          <p className="text-xs font-semibold uppercase tracking-wide text-emerald-400">
            Current Skills
          </p>
          <ul className="mt-3 space-y-2">
            {skillGap.current_skills.map((s) => (
              <li key={s} className="flex items-center gap-2 text-sm text-slate-200">
                <CheckCircle2 className="h-3.5 w-3.5 shrink-0 text-emerald-400" />
                {s}
              </li>
            ))}
          </ul>
        </div>

        <div className="flex flex-col items-center justify-center rounded-xl border border-violet-500/20 bg-violet-500/5 p-4 text-center">
          <Zap className="h-8 w-8 text-violet-400" />
          <p className="mt-2 text-2xl font-bold text-white">{skillGap.overall_readiness.toFixed(0)}%</p>
          <p className="text-xs text-slate-400">Career readiness</p>
          <p className="mt-2 text-sm font-medium text-violet-300">{skillGap.target_career}</p>
        </div>

        <div className="rounded-xl border border-rose-500/20 bg-rose-500/5 p-4">
          <p className="text-xs font-semibold uppercase tracking-wide text-rose-400">
            Missing Skills
          </p>
          <ul className="mt-3 space-y-2">
            {skillGap.missing_skills.map((s) => (
              <li key={s} className="flex items-center gap-2 text-sm text-slate-200">
                <AlertTriangle className="h-3.5 w-3.5 shrink-0 text-rose-400" />
                {s}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {skillGap.gaps.length > 0 && (
        <div className="mt-6 space-y-2">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            Detailed gaps
          </p>
          {skillGap.gaps.slice(0, 4).map((g) => (
            <div
              key={g.skill}
              className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-white/5 bg-slate-900/40 px-4 py-3"
            >
              <div>
                <span className="font-medium text-white">{g.skill}</span>
                <span className="ml-2 text-xs text-slate-500">
                  {g.current_level}% → {g.required_level}% required
                </span>
              </div>
              <span
                className={`rounded-md border px-2 py-0.5 text-[10px] font-semibold uppercase ${
                  PRIORITY_COLORS[g.priority as keyof typeof PRIORITY_COLORS] ??
                  PRIORITY_COLORS.medium
                }`}
              >
                {g.priority}
              </span>
            </div>
          ))}
        </div>
      )}
    </GlassCard>
  );
}
