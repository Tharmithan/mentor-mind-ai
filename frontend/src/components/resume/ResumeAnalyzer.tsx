"use client";

import { useCallback, useState } from "react";
import {
  Upload,
  FileText,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Loader2,
  Sparkles,
  Target,
} from "lucide-react";
import { GlassCard } from "@/components/ui/GlassCard";
import { uploadResume, analyzeResumeText } from "@/lib/api";
import type { ResumeAnalysisResponse } from "@/lib/types/api";
import { Markdown } from "@/components/assistant/Markdown";

const TARGET_ROLES = [
  { value: "", label: "General tech" },
  { value: "ai_engineer", label: "AI Engineer" },
  { value: "data_scientist", label: "Data Scientist" },
  { value: "mlops", label: "MLOps Engineer" },
  { value: "software_engineer", label: "Software Engineer" },
];

function ScoreRing({ score, grade }: { score: number; grade: string }) {
  const color =
    score >= 85 ? "text-emerald-400" : score >= 70 ? "text-violet-400" : score >= 55 ? "text-amber-400" : "text-red-400";
  return (
    <div className="relative flex h-32 w-32 items-center justify-center">
      <svg className="absolute h-full w-full -rotate-90" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="42" fill="none" stroke="currentColor" strokeWidth="8" className="text-slate-800" />
        <circle
          cx="50"
          cy="50"
          r="42"
          fill="none"
          stroke="currentColor"
          strokeWidth="8"
          strokeLinecap="round"
          className={color}
          strokeDasharray={`${score * 2.64} 264`}
        />
      </svg>
      <div className="text-center">
        <p className={`text-3xl font-bold ${color}`}>{grade}</p>
        <p className="text-xs text-slate-400">{score.toFixed(0)} ATS</p>
      </div>
    </div>
  );
}

export function ResumeAnalyzer() {
  const [targetRole, setTargetRole] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ResumeAnalysisResponse | null>(null);
  const [pasteMode, setPasteMode] = useState(false);
  const [pasteText, setPasteText] = useState("");

  const analyzeFile = useCallback(
    async (file: File) => {
      setLoading(true);
      setError(null);
      try {
        const data = await uploadResume(file, targetRole || undefined);
        setResult(data);
      } catch {
        setError("Upload failed. Use a text-based PDF under 10 MB.");
      } finally {
        setLoading(false);
      }
    },
    [targetRole]
  );

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) analyzeFile(file);
  };

  const analyzePaste = async () => {
    if (pasteText.trim().length < 50) {
      setError("Paste at least 50 characters of resume text.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await analyzeResumeText(pasteText, targetRole || undefined);
      setResult(data);
    } catch {
      setError("Analysis failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      {!result && (
        <>
          <GlassCard className="p-6">
            <div className="mb-4 flex flex-wrap items-center gap-3">
              <Target className="h-5 w-5 text-violet-400" />
              <label className="text-sm text-slate-400">Target role</label>
              <select
                value={targetRole}
                onChange={(e) => setTargetRole(e.target.value)}
                className="rounded-lg border border-violet-500/20 bg-slate-900/60 px-3 py-1.5 text-sm text-white"
              >
                {TARGET_ROLES.map((r) => (
                  <option key={r.value} value={r.value}>
                    {r.label}
                  </option>
                ))}
              </select>
              <button
                type="button"
                onClick={() => setPasteMode(!pasteMode)}
                className="ml-auto text-xs text-violet-300 hover:underline"
              >
                {pasteMode ? "Upload PDF instead" : "Paste text instead"}
              </button>
            </div>

            {pasteMode ? (
              <div className="space-y-3">
                <textarea
                  value={pasteText}
                  onChange={(e) => setPasteText(e.target.value)}
                  placeholder="Paste your resume text here…"
                  rows={12}
                  className="w-full rounded-xl border border-violet-500/20 bg-slate-900/60 p-4 text-sm text-white placeholder:text-slate-500"
                />
                <button
                  type="button"
                  onClick={analyzePaste}
                  disabled={loading}
                  className="rounded-xl bg-gradient-to-r from-violet-600 to-blue-600 px-6 py-2.5 text-sm font-medium text-white disabled:opacity-50"
                >
                  {loading ? "Analyzing…" : "Analyze resume"}
                </button>
              </div>
            ) : (
              <div
                onDrop={onDrop}
                onDragOver={(e) => e.preventDefault()}
                className="flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-violet-500/30 bg-violet-500/5 px-6 py-14 transition hover:border-violet-500/50"
              >
                {loading ? (
                  <Loader2 className="h-10 w-10 animate-spin text-violet-400" />
                ) : (
                  <>
                    <Upload className="mb-3 h-10 w-10 text-violet-400" />
                    <p className="text-sm font-medium text-white">Drop your resume PDF here</p>
                    <p className="mt-1 text-xs text-slate-500">PDF, TXT, or MD · max 10 MB</p>
                    <label className="mt-4 cursor-pointer rounded-xl bg-violet-600/80 px-5 py-2 text-sm font-medium text-white hover:bg-violet-600">
                      Choose file
                      <input
                        type="file"
                        accept=".pdf,.txt,.md"
                        className="hidden"
                        onChange={(e) => {
                          const f = e.target.files?.[0];
                          if (f) analyzeFile(f);
                        }}
                      />
                    </label>
                  </>
                )}
              </div>
            )}
            {error && <p className="mt-3 text-sm text-red-400">{error}</p>}
          </GlassCard>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {[
              { title: "Missing skills", desc: "Gap analysis vs target role" },
              { title: "ATS score", desc: "Recruiter system compatibility" },
              { title: "Formatting", desc: "Structure & length checks" },
              { title: "AI feedback", desc: "Actionable improvements" },
            ].map((item) => (
              <GlassCard key={item.title} className="p-4">
                <p className="text-sm font-medium text-violet-200">{item.title}</p>
                <p className="mt-1 text-xs text-slate-500">{item.desc}</p>
              </GlassCard>
            ))}
          </div>
        </>
      )}

      {result && (
        <div className="space-y-5 animate-fade-in-up">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <div className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-violet-400" />
                <h2 className="text-lg font-semibold text-white">Analysis complete</h2>
              </div>
              <p className="mt-1 text-sm text-slate-400">{result.filename ?? "Pasted resume"}</p>
            </div>
            <button
              type="button"
              onClick={() => setResult(null)}
              className="text-sm text-violet-300 hover:underline"
            >
              Analyze another
            </button>
          </div>

          <GlassCard className="flex flex-col items-center gap-6 p-6 sm:flex-row sm:items-start">
            <ScoreRing score={result.ats_score} grade={result.ats_grade} />
            <div className="flex-1 text-center sm:text-left">
              <p className="text-base font-medium text-white">{result.headline}</p>
              <div className="mt-2 text-sm text-slate-300 prose-invert">
                <Markdown text={result.summary} />
              </div>
              <p className="mt-2 text-xs text-slate-500">
                {result.word_count} words · ~{result.page_estimate} page(s)
                {result.used_llm && " · AI-enhanced feedback"}
              </p>
            </div>
          </GlassCard>

          <GlassCard className="p-5">
            <h3 className="mb-3 text-sm font-semibold text-violet-200">AI recommendations</h3>
            <ul className="space-y-2">
              {result.feedback.map((f, i) => (
                <li
                  key={i}
                  className={`flex gap-2 rounded-lg px-3 py-2 text-sm ${
                    f.priority === "high"
                      ? "bg-red-500/10 text-red-100"
                      : f.priority === "medium"
                        ? "bg-amber-500/10 text-amber-100"
                        : "bg-slate-800/50 text-slate-300"
                  }`}
                >
                  <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 opacity-70" />
                  <Markdown text={f.message} />
                </li>
              ))}
            </ul>
          </GlassCard>

          <div className="grid gap-4 lg:grid-cols-2">
            <GlassCard className="p-5">
              <h3 className="mb-3 text-sm font-semibold text-violet-200">Missing skills</h3>
              {result.missing_skills.length === 0 ? (
                <p className="text-sm text-slate-400">No major skill gaps detected.</p>
              ) : (
                <ul className="space-y-2">
                  {result.missing_skills.map((m) => (
                    <li key={m.skill} className="text-sm">
                      <span className="font-medium text-white">{m.skill}</span>
                      <span className="ml-2 text-xs text-slate-500">({m.importance})</span>
                      <p className="text-xs text-slate-400">{m.suggestion}</p>
                    </li>
                  ))}
                </ul>
              )}
            </GlassCard>

            <GlassCard className="p-5">
              <h3 className="mb-3 text-sm font-semibold text-violet-200">ATS checks</h3>
              <ul className="space-y-2">
                {result.ats_checks.map((c) => (
                  <li key={c.label} className="flex items-start gap-2 text-sm">
                    {c.passed ? (
                      <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-400" />
                    ) : (
                      <XCircle className="h-4 w-4 shrink-0 text-amber-400" />
                    )}
                    <div>
                      <span className="text-slate-200">{c.label}</span>
                      <p className="text-xs text-slate-500">{c.detail}</p>
                    </div>
                  </li>
                ))}
              </ul>
            </GlassCard>
          </div>

          {result.weak_bullets.length > 0 && (
            <GlassCard className="p-5">
              <h3 className="mb-3 text-sm font-semibold text-violet-200">Weak descriptions</h3>
              <ul className="space-y-3">
                {result.weak_bullets.map((w, i) => (
                  <li key={i} className="rounded-lg border border-violet-500/10 bg-slate-900/40 p-3 text-sm">
                    <p className="text-xs text-amber-400/90">{w.issue}</p>
                    <p className="mt-1 text-slate-400 italic">&ldquo;{w.text}&rdquo;</p>
                    <p className="mt-1 text-slate-300">{w.suggestion}</p>
                  </li>
                ))}
              </ul>
            </GlassCard>
          )}

          {result.formatting_issues.length > 0 && (
            <GlassCard className="p-5">
              <h3 className="mb-2 flex items-center gap-2 text-sm font-semibold text-violet-200">
                <FileText className="h-4 w-4" />
                Formatting
              </h3>
              <ul className="list-inside list-disc space-y-1 text-sm text-slate-400">
                {result.formatting_issues.map((issue, i) => (
                  <li key={i}>{issue.replace(/\*\*/g, "")}</li>
                ))}
              </ul>
            </GlassCard>
          )}
        </div>
      )}
    </div>
  );
}
