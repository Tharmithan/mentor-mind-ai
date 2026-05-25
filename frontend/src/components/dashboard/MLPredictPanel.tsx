"use client";

import { useState } from "react";
import { GlassCard } from "@/components/ui/GlassCard";
import { explainPrediction, type ExplainResponse, type PredictRequest, type PredictResponse } from "@/lib/api";
import { AIExplanationPanel } from "@/components/dashboard/AIExplanationPanel";
import { Brain, Loader2, Sparkles } from "lucide-react";

export function MLPredictPanel() {
  const [studyHours, setStudyHours] = useState(5);
  const [attendance, setAttendance] = useState(82);
  const [sleepHours, setSleepHours] = useState(7);
  const [result, setResult] = useState<PredictResponse | null>(null);
  const [explanation, setExplanation] = useState<ExplainResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handlePredict = async () => {
    setLoading(true);
    setError(null);
    setExplanation(null);
    try {
      const payload: PredictRequest = {
        study_hours: studyHours,
        attendance,
        sleep_hours: sleepHours,
      };
      const data = await explainPrediction(payload);
      setResult(data.prediction);
      setExplanation(data);
    } catch {
      setError("Could not reach ML API. Start backend on port 8000.");
    } finally {
      setLoading(false);
    }
  };

  const predictionColor =
    result?.prediction === "High Performance"
      ? "text-emerald-400"
      : result?.prediction === "Medium Performance"
        ? "text-violet-300"
        : "text-rose-400";

  return (
    <GlassCard className="p-6">
      <div className="flex items-center gap-2">
        <Brain className="h-5 w-5 text-violet-400" />
        <h2 className="text-lg font-semibold text-white">AI Performance Predictor</h2>
      </div>
      <p className="mt-1 text-sm text-slate-500">
        Live ML API — study hours, attendance, sleep → prediction
      </p>

      <div className="mt-4 grid gap-3 sm:grid-cols-3">
        <label className="block text-sm">
          <span className="text-slate-400">Study hours</span>
          <input
            type="number"
            min={0}
            max={24}
            step={0.5}
            value={studyHours}
            onChange={(e) => setStudyHours(Number(e.target.value))}
            className="mt-1 w-full rounded-lg border border-violet-500/20 bg-slate-900/60 px-3 py-2 text-white"
          />
        </label>
        <label className="block text-sm">
          <span className="text-slate-400">Attendance %</span>
          <input
            type="number"
            min={0}
            max={100}
            value={attendance}
            onChange={(e) => setAttendance(Number(e.target.value))}
            className="mt-1 w-full rounded-lg border border-violet-500/20 bg-slate-900/60 px-3 py-2 text-white"
          />
        </label>
        <label className="block text-sm">
          <span className="text-slate-400">Sleep hours</span>
          <input
            type="number"
            min={0}
            max={12}
            step={0.5}
            value={sleepHours}
            onChange={(e) => setSleepHours(Number(e.target.value))}
            className="mt-1 w-full rounded-lg border border-violet-500/20 bg-slate-900/60 px-3 py-2 text-white"
          />
        </label>
      </div>

      <button
        type="button"
        onClick={handlePredict}
        disabled={loading}
        className="mt-4 inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-violet-600 to-blue-600 px-5 py-2.5 text-sm font-medium text-white hover:opacity-90 disabled:opacity-50"
      >
        {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
        Get AI Prediction
      </button>

      {error && <p className="mt-3 text-sm text-rose-400">{error}</p>}

      {result && (
        <div className="mt-5 rounded-xl border border-violet-500/20 bg-violet-500/10 p-4">
          <p className={`text-2xl font-bold ${predictionColor}`}>{result.prediction}</p>
          <p className="mt-1 text-sm text-slate-400">
            Confidence: <span className="font-semibold text-white">{result.confidence}%</span>
            {" · "}Score: {result.predicted_score}%
          </p>
          <p className="mt-2 text-sm text-slate-500">{result.recommendation}</p>
          <p className="mt-2 text-xs text-violet-400/80">Model: {result.model_version}</p>
        </div>
      )}

      {explanation && (
        <div className="mt-6">
          <AIExplanationPanel data={explanation} />
        </div>
      )}
    </GlassCard>
  );
}
