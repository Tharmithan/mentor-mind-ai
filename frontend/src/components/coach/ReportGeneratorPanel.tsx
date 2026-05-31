"use client";

import { useState } from "react";
import { Download, FileText, Loader2, Mail, Calendar, CalendarDays } from "lucide-react";
import { getWeeklyReport, getMonthlyReport, downloadReportPdf, emailReport } from "@/lib/api";
import type { WeeklyReportData, MonthlyReportData } from "@/lib/types/api";
import { GlassCard } from "@/components/ui/GlassCard";
import { Markdown } from "@/components/assistant/Markdown";

const DEMO_USER = "demo-user-001";

export function ReportGeneratorPanel() {
  const [weekly, setWeekly] = useState<WeeklyReportData | null>(null);
  const [monthly, setMonthly] = useState<MonthlyReportData | null>(null);
  const [active, setActive] = useState<"weekly" | "monthly">("weekly");
  const [loading, setLoading] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const loadWeekly = async () => {
    setLoading("weekly");
    setMessage(null);
    try {
      const data = await getWeeklyReport(DEMO_USER);
      setWeekly(data);
      setActive("weekly");
    } catch {
      setMessage("Could not generate weekly report.");
    } finally {
      setLoading(null);
    }
  };

  const loadMonthly = async () => {
    setLoading("monthly");
    setMessage(null);
    try {
      const data = await getMonthlyReport(DEMO_USER);
      setMonthly(data);
      setActive("monthly");
    } catch {
      setMessage("Could not generate monthly report.");
    } finally {
      setLoading(null);
    }
  };

  const handlePdf = async (type: "weekly" | "monthly") => {
    setLoading(`pdf-${type}`);
    setMessage(null);
    try {
      await downloadReportPdf(DEMO_USER, type);
      setMessage(`${type === "weekly" ? "Weekly" : "Monthly"} PDF downloaded.`);
    } catch {
      setMessage("PDF export failed — install fpdf2 on the backend.");
    } finally {
      setLoading(null);
    }
  };

  const handleEmail = async (type: "weekly" | "monthly") => {
    setLoading(`email-${type}`);
    setMessage(null);
    try {
      const res = await emailReport(DEMO_USER, type);
      setMessage(res.message);
    } catch {
      setMessage("Email failed — configure SMTP in backend .env");
    } finally {
      setLoading(null);
    }
  };

  const preview = active === "weekly" ? weekly?.markdown : monthly?.markdown;

  return (
    <GlassCard className="p-6">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <FileText className="h-5 w-5 text-violet-400" />
          <div>
            <h2 className="text-lg font-semibold text-white">Automated Reports</h2>
            <p className="text-xs text-slate-500">Professional weekly & monthly learning reports</p>
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            disabled={!!loading}
            onClick={loadWeekly}
            className="inline-flex items-center gap-1.5 rounded-lg border border-violet-500/25 bg-violet-500/10 px-3 py-1.5 text-xs font-medium text-violet-200 hover:bg-violet-500/20 disabled:opacity-50"
          >
            {loading === "weekly" ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Calendar className="h-3.5 w-3.5" />}
            Weekly
          </button>
          <button
            type="button"
            disabled={!!loading}
            onClick={loadMonthly}
            className="inline-flex items-center gap-1.5 rounded-lg border border-violet-500/25 bg-violet-500/10 px-3 py-1.5 text-xs font-medium text-violet-200 hover:bg-violet-500/20 disabled:opacity-50"
          >
            {loading === "monthly" ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <CalendarDays className="h-3.5 w-3.5" />}
            Monthly
          </button>
        </div>
      </div>

      {(weekly || monthly) && (
        <div className="mb-4 flex flex-wrap gap-2">
          <button
            type="button"
            disabled={!!loading}
            onClick={() => handlePdf(active)}
            className="inline-flex items-center gap-1.5 rounded-lg border border-white/10 bg-slate-900/50 px-3 py-1.5 text-xs text-slate-300 hover:border-violet-500/25 disabled:opacity-50"
          >
            {loading === `pdf-${active}` ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Download className="h-3.5 w-3.5" />}
            Download PDF
          </button>
          <button
            type="button"
            disabled={!!loading}
            onClick={() => handleEmail(active)}
            className="inline-flex items-center gap-1.5 rounded-lg border border-white/10 bg-slate-900/50 px-3 py-1.5 text-xs text-slate-300 hover:border-violet-500/25 disabled:opacity-50"
          >
            {loading === `email-${active}` ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Mail className="h-3.5 w-3.5" />}
            Email report
          </button>
        </div>
      )}

      {message && (
        <p className="mb-3 rounded-lg border border-violet-500/20 bg-violet-500/5 px-3 py-2 text-xs text-violet-200">
          {message}
        </p>
      )}

      {preview ? (
        <div className="max-h-80 overflow-y-auto rounded-xl border border-white/5 bg-slate-950/50 p-4">
          <div className="prose-invert text-sm [&_*]:text-sm">
            <Markdown text={preview} />
          </div>
        </div>
      ) : (
        <p className="text-sm text-slate-500">
          Generate a weekly or monthly report to preview learning progress, interview scores, skill growth, and recommendations.
        </p>
      )}
    </GlassCard>
  );
}
