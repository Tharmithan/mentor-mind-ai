"use client";

import { useEffect, useState } from "react";
import { Activity, Database, Mail, Server, Users } from "lucide-react";
import { getAdminOverviewDemo } from "@/lib/api";
import type { AdminOverviewResponse } from "@/lib/types/api";
import { GlassCard } from "@/components/ui/GlassCard";
import { PageHeader } from "@/components/ui/PageHeader";

export function AdminDashboard() {
  const [data, setData] = useState<AdminOverviewResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getAdminOverviewDemo()
      .then(setData)
      .catch(() => setError("Could not load admin overview. Is the backend running?"));
  }, []);

  if (error) {
    return (
      <div className="rounded-xl border border-red-500/20 bg-red-500/5 p-8 text-center text-red-300">
        {error}
      </div>
    );
  }

  if (!data) {
    return <div className="animate-pulse text-slate-400">Loading admin dashboard…</div>;
  }

  const cards = [
    { label: "Users", value: data.total_users, icon: Users },
    { label: "Predictions", value: data.total_predictions, icon: Activity },
    { label: "Feedback", value: data.total_feedback, icon: Mail },
    { label: "RAG Docs", value: data.vector_documents, icon: Database },
  ];

  return (
    <div className="space-y-8">
      <PageHeader
        title="Admin Dashboard"
        subtitle="Monitor users, models, and platform health"
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {cards.map(({ label, value, icon: Icon }) => (
          <GlassCard key={label} className="p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs uppercase tracking-wider text-slate-400">{label}</p>
                <p className="mt-1 text-3xl font-bold text-white">{value}</p>
              </div>
              <Icon className="h-8 w-8 text-violet-400/80" />
            </div>
          </GlassCard>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <GlassCard className="p-6">
          <h3 className="flex items-center gap-2 text-lg font-semibold text-white">
            <Server className="h-5 w-5 text-violet-400" />
            System Status
          </h3>
          <ul className="mt-4 space-y-2 text-sm">
            {Object.entries(data.system_status).map(([k, v]) => (
              <li key={k} className="flex justify-between text-slate-300">
                <span className="capitalize">{k.replace("_", " ")}</span>
                <span className="text-emerald-400">{v}</span>
              </li>
            ))}
          </ul>
          <p className="mt-4 text-sm text-slate-400">
            Model: {data.production_model_version ?? "n/a"} ·{" "}
            {data.models_loaded ? "loaded" : "not loaded"}
          </p>
          {data.avg_satisfaction != null && (
            <p className="mt-1 text-sm text-slate-400">
              Avg satisfaction: {data.avg_satisfaction.toFixed(1)} / 5
            </p>
          )}
        </GlassCard>

        <GlassCard className="p-6">
          <h3 className="text-lg font-semibold text-white">Recent Users</h3>
          <ul className="mt-4 divide-y divide-violet-500/10">
            {data.recent_users.map((u) => (
              <li key={u.id} className="flex items-center justify-between py-3 text-sm">
                <div>
                  <p className="font-medium text-slate-200">{u.full_name}</p>
                  <p className="text-slate-500">{u.email}</p>
                </div>
                <span className="rounded-full bg-violet-500/10 px-2 py-0.5 text-xs text-violet-300">
                  {u.role}
                </span>
              </li>
            ))}
          </ul>
        </GlassCard>
      </div>
    </div>
  );
}
