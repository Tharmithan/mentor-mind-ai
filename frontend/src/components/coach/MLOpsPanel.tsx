"use client";

import { useCallback, useEffect, useState } from "react";
import {
  Box,
  GitBranch,
  Loader2,
  Play,
  Rocket,
  Scale,
  Server,
} from "lucide-react";
import {
  compareMLOpsExperiments,
  getMLOpsExperiments,
  getMLOpsModels,
  getMLOpsStatus,
  promoteMLOpsModel,
  runMLOpsExperiment,
} from "@/lib/api";
import type {
  ExperimentComparison,
  MLOpsStatus,
  ModelVersion,
  ExperimentRun,
} from "@/lib/types/api";
import { GlassCard } from "@/components/ui/GlassCard";

export function MLOpsPanel() {
  const [status, setStatus] = useState<MLOpsStatus | null>(null);
  const [models, setModels] = useState<ModelVersion[]>([]);
  const [experiments, setExperiments] = useState<ExperimentRun[]>([]);
  const [comparison, setComparison] = useState<ExperimentComparison | null>(null);
  const [loading, setLoading] = useState(true);
  const [action, setAction] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [s, m, e, c] = await Promise.all([
        getMLOpsStatus(),
        getMLOpsModels(),
        getMLOpsExperiments(),
        compareMLOpsExperiments(),
      ]);
      setStatus(s);
      setModels(m);
      setExperiments(e);
      setComparison(c);
    } catch {
      setMessage("Could not load MLOps pipeline. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const handleRunExperiment = async () => {
    setAction("run");
    setMessage(null);
    try {
      const res = await runMLOpsExperiment({ algorithm: "both", log_mlflow: true });
      setMessage(res.note ?? "Experiment logged.");
      await load();
    } catch {
      setMessage("Experiment run failed.");
    } finally {
      setAction(null);
    }
  };

  const handlePromote = async (version: string) => {
    setAction(`promote-${version}`);
    setMessage(null);
    try {
      await promoteMLOpsModel(version);
      setMessage(`Model ${version} promoted to production.`);
      await load();
    } catch {
      setMessage(`Could not promote ${version}.`);
    } finally {
      setAction(null);
    }
  };

  if (loading && !status) {
    return (
      <GlassCard className="flex items-center justify-center gap-2 p-8 text-slate-400">
        <Loader2 className="h-5 w-5 animate-spin" />
        Loading MLOps pipeline…
      </GlassCard>
    );
  }

  return (
    <GlassCard className="p-6">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <Server className="h-5 w-5 text-violet-400" />
          <div>
            <h2 className="text-lg font-semibold text-white">MLOps Pipeline</h2>
            <p className="text-xs text-slate-500">
              Model versioning · experiment tracking · deployment
            </p>
          </div>
        </div>
        <button
          type="button"
          disabled={!!action}
          onClick={handleRunExperiment}
          className="inline-flex items-center gap-1.5 rounded-lg border border-violet-500/25 bg-violet-500/10 px-3 py-1.5 text-xs font-medium text-violet-200 hover:bg-violet-500/20 disabled:opacity-50"
        >
          {action === "run" ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          ) : (
            <Play className="h-3.5 w-3.5" />
          )}
          Log Experiment
        </button>
      </div>

      {status && (
        <div className="mb-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <Stat label="Production" value={status.production_version ?? "none"} icon={Rocket} />
          <Stat label="Versions" value={String(status.total_versions)} icon={Box} />
          <Stat label="Experiments" value={String(status.total_experiments)} icon={Scale} />
          <Stat
            label="MLflow"
            value={status.mlflow_enabled ? "enabled" : "JSON fallback"}
            icon={GitBranch}
          />
        </div>
      )}

      {comparison && comparison.experiments.length > 0 && (
        <div className="mb-6 rounded-xl border border-emerald-500/15 bg-emerald-500/5 p-4">
          <p className="text-xs font-semibold uppercase tracking-wide text-emerald-400">
            Experiment Comparison
          </p>
          <p className="mt-2 text-sm text-slate-300">{comparison.recommendation}</p>
          <p className="mt-1 text-xs text-slate-500">
            Best regression: {comparison.best_regression} · Best classification:{" "}
            {comparison.best_classification}
          </p>
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        <div>
          <h3 className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
            Model Registry
          </h3>
          <div className="space-y-2">
            {models.map((m) => (
              <div
                key={m.version}
                className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-white/5 bg-slate-900/40 px-3 py-2"
              >
                <div>
                  <p className="text-sm font-medium text-white">
                    {m.version}{" "}
                    <span
                      className={
                        m.status === "production"
                          ? "text-emerald-400"
                          : "text-slate-500"
                      }
                    >
                      ({m.status})
                    </span>
                  </p>
                  <p className="text-xs text-slate-500">
                    {m.algorithm} · R² {fmt(m.metrics.r2)} · F1 {fmt(m.metrics.f1)}
                  </p>
                </div>
                {m.status !== "production" && (
                  <button
                    type="button"
                    disabled={!!action}
                    onClick={() => handlePromote(m.version)}
                    className="rounded-md border border-violet-500/20 px-2 py-1 text-[10px] font-medium text-violet-200 hover:bg-violet-500/10 disabled:opacity-50"
                  >
                    {action === `promote-${m.version}` ? "…" : "Promote"}
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>

        <div>
          <h3 className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
            Training Logs
          </h3>
          <div className="space-y-2">
            {experiments.map((e) => (
              <div
                key={e.experiment_id}
                className="rounded-lg border border-white/5 bg-slate-900/40 px-3 py-2"
              >
                <p className="text-sm font-medium text-white">{e.run_name}</p>
                <p className="text-xs text-slate-500">
                  {e.algorithm} · R² {fmt(e.metrics.r2)} · F1 {fmt(e.metrics.f1)}
                </p>
                <p className="text-[10px] text-slate-600">{e.started_at}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {message && (
        <p className="mt-4 text-xs text-slate-400">{message}</p>
      )}
    </GlassCard>
  );
}

function Stat({
  label,
  value,
  icon: Icon,
}: {
  label: string;
  value: string;
  icon: React.ComponentType<{ className?: string }>;
}) {
  return (
    <div className="rounded-xl border border-white/5 bg-slate-900/40 p-3">
      <div className="flex items-center gap-2 text-slate-500">
        <Icon className="h-3.5 w-3.5" />
        <span className="text-[10px] font-semibold uppercase tracking-wide">{label}</span>
      </div>
      <p className="mt-1 text-sm font-semibold text-white">{value}</p>
    </div>
  );
}

function fmt(v: number | null | undefined): string {
  if (v == null) return "—";
  return v.toFixed(4);
}
