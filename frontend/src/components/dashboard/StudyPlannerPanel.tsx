"use client";

import { useEffect, useState } from "react";
import { GlassCard } from "@/components/ui/GlassCard";
import { postDailyStudyPlanner } from "@/lib/api";
import type { DailyStudyPlannerResponse } from "@/lib/types/api";
import { BookOpen, Calendar, ListOrdered, Sparkles } from "lucide-react";

const priorityBadge = {
  high: "bg-rose-500/20 text-rose-300",
  medium: "bg-amber-500/20 text-amber-300",
  low: "bg-emerald-500/20 text-emerald-300",
} as const;

export function StudyPlannerPanel() {
  const [plan, setPlan] = useState<DailyStudyPlannerResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    postDailyStudyPlanner({
      study_hours: 3,
      attendance_pct: 72,
      subject_scores: [
        { subject: "Mathematics", score: 58 },
        { subject: "Portuguese", score: 72 },
        { subject: "Data Structures", score: 62 },
        { subject: "Programming", score: 78 },
      ],
    })
      .then(setPlan)
      .catch(() => setPlan(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <GlassCard className="p-6">
        <p className="text-sm text-slate-500">Building your AI study plan…</p>
      </GlassCard>
    );
  }

  if (!plan) {
    return null;
  }

  return (
    <GlassCard className="p-6">
      <div className="flex items-center gap-2">
        <Calendar className="h-5 w-5 text-violet-400" />
        <h2 className="text-lg font-semibold text-white">AI Daily Study Planner</h2>
      </div>
      <p className="mt-1 text-sm text-slate-500">{plan.summary}</p>

      <div className="mt-5 grid gap-6 lg:grid-cols-2">
        <div>
          <div className="flex items-center gap-2 text-sm font-medium text-violet-300">
            <ListOrdered className="h-4 w-4" />
            Revision priority
          </div>
          <ol className="mt-2 list-decimal space-y-1 pl-5 text-sm text-slate-300">
            {plan.revision_priority.map((s) => (
              <li key={s}>{s}</li>
            ))}
          </ol>

          <div className="mt-4 flex items-center gap-2 text-sm font-medium text-violet-300">
            <BookOpen className="h-4 w-4" />
            Focus areas
          </div>
          <ul className="mt-2 space-y-2">
            {plan.focus_areas.map((f) => (
              <li
                key={f.subject}
                className="flex items-center justify-between rounded-lg border border-violet-500/10 bg-slate-900/40 px-3 py-2 text-sm"
              >
                <span className="text-white">
                  {f.priority_rank}. {f.subject} — {f.topic}
                </span>
                <span className="text-slate-500">{Math.round(f.score)}%</span>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <p className="text-sm font-medium text-violet-300">
            This week&apos;s timetable ({plan.weekly_study_hours}h total)
          </p>
          <ul className="mt-2 max-h-64 space-y-2 overflow-y-auto">
            {plan.timetable.map((slot, i) => (
              <li
                key={`${slot.day}-${slot.subject}-${i}`}
                className="rounded-lg border border-violet-500/10 bg-slate-900/40 px-3 py-2 text-sm"
              >
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-medium text-white">
                    {slot.day} · {slot.time_slot}
                  </span>
                  <span
                    className={`rounded px-1.5 py-0.5 text-xs ${
                      priorityBadge[slot.priority as keyof typeof priorityBadge] ??
                      priorityBadge.medium
                    }`}
                  >
                    {slot.priority}
                  </span>
                </div>
                <p className="mt-1 text-slate-400">
                  {slot.subject}: {slot.task} ({slot.duration_hours}h)
                </p>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {plan.collaborative_insights.length > 0 && (
        <div className="mt-5 rounded-xl border border-violet-500/15 bg-violet-500/5 p-4">
          <div className="flex items-center gap-2 text-sm font-medium text-violet-300">
            <Sparkles className="h-4 w-4" />
            Peers like you
          </div>
          <ul className="mt-2 space-y-1 text-sm text-slate-400">
            {plan.collaborative_insights.map((insight) => (
              <li key={insight}>• {insight}</li>
            ))}
          </ul>
        </div>
      )}
    </GlassCard>
  );
}
