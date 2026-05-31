"use client";

import { useCallback, useEffect, useState } from "react";
import {
  Activity,
  Loader2,
  MessageSquare,
  RefreshCw,
  ThumbsDown,
  ThumbsUp,
  TrendingUp,
} from "lucide-react";
import { getMonitoringDashboard, submitFeedback } from "@/lib/api";
import type { MonitoringDashboard } from "@/lib/types/api";
import { GlassCard } from "@/components/ui/GlassCard";

const DEMO_USER = "demo-user-001";

export function MonitoringPanel() {
  const [data, setData] = useState<MonitoringDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [comment, setComment] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const dash = await getMonitoringDashboard(DEMO_USER);
      setData(dash);
    } catch {
      setMessage("Could not load monitoring dashboard.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const sendGeneralFeedback = async (helpful: boolean) => {
    setSubmitting(true);
    setMessage(null);
    try {
      await submitFeedback({
        category: "general",
        target_id: "coach_dashboard",
        rating: helpful ? 5 : 1,
        helpful,
        comment: comment || (helpful ? "Helpful experience" : "Needs improvement"),
      });
      setComment("");
      setMessage(helpful ? "Thanks — we'll keep improving!" : "Feedback recorded. Adjusting suggestions.");
      await load();
    } catch {
      setMessage("Could not submit feedback.");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading && !data) {
    return (
      <GlassCard className="flex items-center gap-2 p-8 text-slate-400">
        <Loader2 className="h-5 w-5 animate-spin" />
        Loading monitoring dashboard…
      </GlassCard>
    );
  }

  if (!data) return null;

  const { satisfaction, model_metrics, improvement, recent_feedback } = data;

  return (
    <GlassCard className="p-6">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <Activity className="h-5 w-5 text-violet-400" />
          <div>
            <h2 className="text-lg font-semibold text-white">Monitoring & Feedback</h2>
            <p className="text-xs text-slate-500">Continuous improvement from your ratings</p>
          </div>
        </div>
        <button
          type="button"
          onClick={load}
          className="inline-flex items-center gap-1 rounded-lg border border-white/10 px-2 py-1 text-xs text-slate-400 hover:text-white"
        >
          <RefreshCw className="h-3 w-3" /> Refresh
        </button>
      </div>

      <div className="mb-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Metric
          label="Satisfaction"
          value={`${satisfaction.satisfaction_score}%`}
          sub={`${satisfaction.total_feedback} ratings · ${satisfaction.trend}`}
        />
        <Metric
          label="Avg rating"
          value={satisfaction.total_feedback ? satisfaction.avg_rating.toFixed(1) : "—"}
          sub={`${satisfaction.helpful_pct}% helpful`}
        />
        <Metric
          label="Predictions logged"
          value={String(model_metrics.total_predictions)}
          sub={model_metrics.model_version ?? "no model yet"}
        />
        <Metric
          label="Model drift"
          value={model_metrics.drift_status}
          sub={
            model_metrics.mean_absolute_error != null
              ? `MAE ${model_metrics.mean_absolute_error}`
              : "Awaiting actual scores"
          }
        />
      </div>

      <div className="mb-6 rounded-xl border border-violet-500/15 bg-violet-500/5 p-4">
        <div className="flex items-center gap-2 text-violet-300">
          <TrendingUp className="h-4 w-4" />
          <span className="text-xs font-semibold uppercase tracking-wide">Improvement loop</span>
        </div>
        <p className="mt-2 text-sm text-slate-300">{improvement.improved_recommendation_note}</p>
        <ul className="mt-3 space-y-2">
          {improvement.insights.slice(0, 3).map((ins) => (
            <li key={ins.area} className="text-xs text-slate-400">
              <span className="font-medium text-slate-300">{ins.area}:</span> {ins.action}
            </li>
          ))}
        </ul>
      </div>

      <div className="mb-4">
        <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
          Quick feedback
        </p>
        <textarea
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder="e.g. Recommendation was not useful"
          rows={2}
          className="w-full rounded-lg border border-white/10 bg-slate-900/50 px-3 py-2 text-sm text-white placeholder:text-slate-600"
        />
        <div className="mt-2 flex gap-2">
          <button
            type="button"
            disabled={submitting}
            onClick={() => sendGeneralFeedback(true)}
            className="inline-flex items-center gap-1 rounded-lg border border-emerald-500/25 bg-emerald-500/10 px-3 py-1.5 text-xs text-emerald-200 disabled:opacity-50"
          >
            <ThumbsUp className="h-3.5 w-3.5" /> Useful
          </button>
          <button
            type="button"
            disabled={submitting}
            onClick={() => sendGeneralFeedback(false)}
            className="inline-flex items-center gap-1 rounded-lg border border-rose-500/25 bg-rose-500/10 px-3 py-1.5 text-xs text-rose-200 disabled:opacity-50"
          >
            <ThumbsDown className="h-3.5 w-3.5" /> Not useful
          </button>
        </div>
      </div>

      {recent_feedback.length > 0 && (
        <div>
          <p className="mb-2 flex items-center gap-1 text-xs font-semibold uppercase tracking-wide text-slate-500">
            <MessageSquare className="h-3 w-3" /> Recent feedback
          </p>
          <div className="space-y-2">
            {recent_feedback.slice(0, 5).map((f) => (
              <div
                key={f.feedback_id}
                className="rounded-lg border border-white/5 bg-slate-900/40 px-3 py-2 text-xs"
              >
                <span className="text-violet-400">{f.category}</span>
                {" · "}
                <span className={f.helpful ? "text-emerald-400" : "text-rose-400"}>
                  {f.helpful ? "helpful" : "not useful"}
                </span>
                {f.comment && <p className="mt-1 text-slate-400">{f.comment}</p>}
              </div>
            ))}
          </div>
        </div>
      )}

      {message && <p className="mt-3 text-xs text-slate-400">{message}</p>}
    </GlassCard>
  );
}

function Metric({ label, value, sub }: { label: string; value: string; sub: string }) {
  return (
    <div className="rounded-xl border border-white/5 bg-slate-900/40 p-3">
      <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 text-lg font-semibold text-white">{value}</p>
      <p className="text-[10px] text-slate-600">{sub}</p>
    </div>
  );
}
