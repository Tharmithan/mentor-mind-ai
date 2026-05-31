"use client";

import { useEffect, useState } from "react";
import {
  buildUserProfile,
  getPersonalizedUserRecommendations,
  submitFeedback,
  updateLearningPreferences,
} from "@/lib/api";
import type { PersonalizedRecommendationsResponse } from "@/lib/types/api";
import { GlassCard } from "@/components/ui/GlassCard";
import { BookOpen, Film, Gamepad2, Hammer, Loader2, Sparkles, ThumbsDown, ThumbsUp } from "lucide-react";

const STYLES = [
  { id: "video", label: "Video", icon: Film, desc: "YouTube, lectures" },
  { id: "reading", label: "Reading", icon: BookOpen, desc: "PDFs, docs, notes" },
  { id: "interactive", label: "Interactive", icon: Gamepad2, desc: "Quizzes, flashcards" },
  { id: "hands_on", label: "Hands-on", icon: Hammer, desc: "Projects, labs" },
] as const;

const DEMO_USER = "demo-user-001";

export function PersonalizationPanel() {
  const [recs, setRecs] = useState<PersonalizedRecommendationsResponse | null>(null);
  const [style, setStyle] = useState<string>("interactive");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      await buildUserProfile(DEMO_USER);
      const data = await getPersonalizedUserRecommendations(DEMO_USER);
      setRecs(data);
      setStyle(data.learning_style);
    } catch {
      setRecs(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const selectStyle = async (styleId: string) => {
    setSaving(true);
    setStyle(styleId);
    try {
      await updateLearningPreferences(DEMO_USER, { primary_style: styleId });
      const data = await getPersonalizedUserRecommendations(DEMO_USER);
      setRecs(data);
    } finally {
      setSaving(false);
    }
  };

  const rateResource = async (title: string, helpful: boolean) => {
    await submitFeedback({
      category: "recommendation",
      target_id: title,
      rating: helpful ? 5 : 1,
      helpful,
      comment: helpful ? "Useful recommendation" : "Recommendation wasn't useful",
    });
    if (!helpful) {
      const data = await getPersonalizedUserRecommendations(DEMO_USER);
      setRecs(data);
    }
  };

  if (loading) {
    return (
      <GlassCard className="flex items-center gap-3 p-6">
        <Loader2 className="h-5 w-5 animate-spin text-violet-400" />
        <span className="text-sm text-slate-400">Building your personalized profile…</span>
      </GlassCard>
    );
  }

  if (!recs) return null;

  return (
    <GlassCard className="p-6">
      <div className="mb-5 flex items-center gap-2">
        <Sparkles className="h-5 w-5 text-violet-400" />
        <div>
          <h2 className="text-lg font-semibold text-white">Personalized For You</h2>
          <p className="text-xs text-slate-500">{recs.style_rationale}</p>
        </div>
      </div>

      <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
        Learning style
      </p>
      <div className="mb-6 grid grid-cols-2 gap-2 sm:grid-cols-4">
        {STYLES.map(({ id, label, icon: Icon, desc }) => (
          <button
            key={id}
            type="button"
            disabled={saving}
            onClick={() => selectStyle(id)}
            className={`rounded-xl border p-3 text-left transition ${
              style === id
                ? "border-violet-500/50 bg-violet-500/15 ring-1 ring-violet-500/30"
                : "border-white/5 bg-slate-900/40 hover:border-violet-500/25"
            }`}
          >
            <Icon className={`mb-2 h-4 w-4 ${style === id ? "text-violet-300" : "text-slate-500"}`} />
            <p className="text-sm font-medium text-white">{label}</p>
            <p className="text-[10px] text-slate-500">{desc}</p>
          </button>
        ))}
      </div>

      <div className="mb-4 flex flex-wrap gap-2 text-xs">
        <span className="rounded-full bg-rose-500/10 px-2.5 py-1 text-rose-300">
          Weak: {recs.weak_subjects.join(", ") || "—"}
        </span>
        <span className="rounded-full bg-emerald-500/10 px-2.5 py-1 text-emerald-300">
          Strong: {recs.strong_subjects.join(", ") || "—"}
        </span>
      </div>

      <div className="space-y-2">
        {recs.resources.slice(0, 4).map((r, i) => (
          <div
            key={`${r.title}-${i}`}
            className="rounded-lg border border-white/5 bg-slate-900/40 px-4 py-3"
          >
            <div className="flex items-start justify-between gap-2">
              <div>
                <p className="text-sm font-medium text-white">{r.title}</p>
                <p className="mt-0.5 text-xs text-slate-400">{r.description}</p>
                <span className="mt-1 inline-block text-[10px] uppercase text-violet-400">
                  {r.format} · {r.subject}
                </span>
              </div>
              <div className="flex shrink-0 gap-1">
                <button
                  type="button"
                  aria-label="Useful"
                  onClick={() => rateResource(r.title, true)}
                  className="rounded p-1 text-slate-500 hover:bg-emerald-500/10 hover:text-emerald-400"
                >
                  <ThumbsUp className="h-3.5 w-3.5" />
                </button>
                <button
                  type="button"
                  aria-label="Not useful"
                  onClick={() => rateResource(r.title, false)}
                  className="rounded p-1 text-slate-500 hover:bg-rose-500/10 hover:text-rose-400"
                >
                  <ThumbsDown className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {recs.study_actions.length > 0 && (
        <ul className="mt-4 space-y-1 border-t border-white/5 pt-4 text-xs text-slate-400">
          {recs.study_actions.map((a) => (
            <li key={a}>→ {a}</li>
          ))}
        </ul>
      )}
    </GlassCard>
  );
}
