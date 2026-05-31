"use client";

import { useState } from "react";
import {
  Target,
  Calendar,
  CheckCircle2,
  Circle,
  Loader2,
  Sparkles,
  ChevronRight,
} from "lucide-react";
import { GlassCard } from "@/components/ui/GlassCard";
import {
  createLearningPlan,
  generateLearningRoadmap,
  updateLearningPlanProgress,
  getLearningPlanWeekly,
} from "@/lib/api";
import type { LearningPlanResponse, LearningRoadmapResponse } from "@/lib/types/api";
import { Markdown } from "@/components/assistant/Markdown";

const PRESET_GOALS = [
  "Become an AI Engineer",
  "Become a Data Scientist",
  "Become an MLOps Engineer",
  "Become a Software Engineer",
];

export function LearningPlannerPanel() {
  const [goal, setGoal] = useState("Become an AI Engineer");
  const [hours, setHours] = useState(10);
  const [loading, setLoading] = useState(false);
  const [roadmap, setRoadmap] = useState<LearningRoadmapResponse | null>(null);
  const [plan, setPlan] = useState<LearningPlanResponse | null>(null);
  const [weeklyMd, setWeeklyMd] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const previewRoadmap = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await generateLearningRoadmap({ goal, hours_per_week: hours });
      setRoadmap(data);
      setPlan(null);
      setWeeklyMd(null);
    } catch {
      setError("Could not generate roadmap.");
    } finally {
      setLoading(false);
    }
  };

  const startPlan = async () => {
    setLoading(true);
    setError(null);
    try {
      const p = await createLearningPlan({ goal, hours_per_week: hours });
      setPlan(p);
      setRoadmap(p.roadmap);
      const w = await getLearningPlanWeekly(p.plan_id);
      setWeeklyMd(w.weekly_markdown as string);
    } catch {
      setError("Could not create plan.");
    } finally {
      setLoading(false);
    }
  };

  const completeMilestone = async (milestoneId: string) => {
    if (!plan) return;
    setLoading(true);
    try {
      const updated = await updateLearningPlanProgress(plan.plan_id, {
        milestone_id: milestoneId,
      });
      setPlan(updated);
      const w = await getLearningPlanWeekly(updated.plan_id);
      setWeeklyMd(w.weekly_markdown as string);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <GlassCard className="p-6">
        <div className="flex flex-wrap items-end gap-4">
          <div className="min-w-[200px] flex-1">
            <label className="mb-1 flex items-center gap-2 text-xs text-slate-500">
              <Target className="h-3.5 w-3.5" />
              Your goal
            </label>
            <input
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              className="w-full rounded-xl border border-violet-500/20 bg-slate-900/60 px-3 py-2 text-sm text-white"
            />
          </div>
          <div>
            <label className="mb-1 block text-xs text-slate-500">Hours/week</label>
            <input
              type="number"
              min={2}
              max={40}
              value={hours}
              onChange={(e) => setHours(Number(e.target.value))}
              className="w-20 rounded-xl border border-violet-500/20 bg-slate-900/60 px-3 py-2 text-sm text-white"
            />
          </div>
          <button
            type="button"
            onClick={previewRoadmap}
            disabled={loading}
            className="rounded-xl border border-violet-500/30 px-4 py-2 text-sm text-violet-200 hover:bg-violet-500/10 disabled:opacity-50"
          >
            Preview
          </button>
          <button
            type="button"
            onClick={startPlan}
            disabled={loading}
            className="rounded-xl bg-gradient-to-r from-violet-600 to-blue-600 px-5 py-2 text-sm font-medium text-white disabled:opacity-50"
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Start tracking"}
          </button>
        </div>
        <div className="mt-3 flex flex-wrap gap-2">
          {PRESET_GOALS.map((g) => (
            <button
              key={g}
              type="button"
              onClick={() => setGoal(g)}
              className="rounded-lg border border-violet-500/15 bg-slate-900/40 px-2.5 py-1 text-[11px] text-slate-400 hover:border-violet-500/30"
            >
              {g}
            </button>
          ))}
        </div>
        {error && <p className="mt-2 text-sm text-red-400">{error}</p>}
      </GlassCard>

      {roadmap && (
        <div className="space-y-4 animate-fade-in-up">
          <GlassCard className="p-5">
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-violet-400" />
              <h2 className="font-semibold text-white">{roadmap.career_title} Roadmap</h2>
              {plan && (
                <span className="ml-auto text-xs text-emerald-400">
                  {plan.progress_pct.toFixed(0)}% complete
                </span>
              )}
            </div>
            <div className="mt-2 text-sm text-slate-300 prose-invert">
              <Markdown text={roadmap.summary} />
            </div>
          </GlassCard>

          <div className="grid gap-4 md:grid-cols-2">
            {roadmap.months.map((m) => (
              <GlassCard key={m.month} className="p-4">
                <div className="flex items-center gap-2">
                  <Calendar className="h-4 w-4 text-violet-400" />
                  <h3 className="text-sm font-semibold text-white">
                    Month {m.month}: {m.title}
                  </h3>
                </div>
                <ul className="mt-2 space-y-1">
                  {m.topics.map((t) => (
                    <li key={t.name} className="text-sm text-violet-200">
                      • {t.name}
                    </li>
                  ))}
                </ul>
                <p className="mt-2 text-xs text-slate-500">{m.milestone}</p>
              </GlassCard>
            ))}
          </div>

          {plan && (
            <GlassCard className="p-5">
              <h3 className="mb-3 text-sm font-semibold text-violet-200">Milestones</h3>
              <ul className="space-y-2">
                {plan.milestones.map((ms) => (
                  <li key={ms.id} className="flex items-center gap-3 text-sm">
                    {ms.completed ? (
                      <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                    ) : (
                      <button
                        type="button"
                        onClick={() => completeMilestone(ms.id)}
                        className="text-slate-500 hover:text-violet-400"
                        aria-label="Mark complete"
                      >
                        <Circle className="h-4 w-4" />
                      </button>
                    )}
                    <span className={ms.completed ? "text-slate-500 line-through" : "text-slate-300"}>
                      Month {ms.month}: {ms.label}
                    </span>
                  </li>
                ))}
              </ul>
            </GlassCard>
          )}

          {weeklyMd && (
            <GlassCard className="p-5">
              <h3 className="mb-2 flex items-center gap-2 text-sm font-semibold text-violet-200">
                <ChevronRight className="h-4 w-4" />
                This week
                {plan && (
                  <span className="text-xs font-normal text-slate-500">
                    Month {plan.current_month} · Week {plan.current_week}
                  </span>
                )}
              </h3>
              <div className="text-sm text-slate-300 prose-invert">
                <Markdown text={weeklyMd} />
              </div>
            </GlassCard>
          )}
        </div>
      )}
    </div>
  );
}
