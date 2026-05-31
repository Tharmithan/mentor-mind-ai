"use client";

import {
  BookOpen,
  Briefcase,
  FileText,
  Mic,
  Sparkles,
  Target,
  TrendingUp,
} from "lucide-react";
import type { CoachScoreCard } from "@/lib/types/api";

const ICONS: Record<string, React.ReactNode> = {
  "Learning Score": <BookOpen className="h-4 w-4" />,
  "Interview Score": <Mic className="h-4 w-4" />,
  "Career Readiness": <Target className="h-4 w-4" />,
  "Resume Score": <FileText className="h-4 w-4" />,
  "AI Recommendations": <Sparkles className="h-4 w-4" />,
};

const GRADIENTS = [
  "from-violet-600/30 to-blue-600/20",
  "from-amber-500/25 to-orange-600/15",
  "from-emerald-500/25 to-teal-600/15",
  "from-rose-500/25 to-pink-600/15",
  "from-indigo-500/25 to-purple-600/15",
];

function ScoreRing({ score, isCount }: { score: number; isCount: boolean }) {
  const pct = isCount ? Math.min(score * 15, 100) : score;
  const circumference = 2 * Math.PI * 36;
  const offset = circumference - (pct / 100) * circumference;

  return (
    <div className="relative flex h-20 w-20 items-center justify-center">
      <svg className="-rotate-90" width="80" height="80">
        <circle cx="40" cy="40" r="36" fill="none" stroke="rgba(139,92,246,0.12)" strokeWidth="6" />
        <circle
          cx="40"
          cy="40"
          r="36"
          fill="none"
          stroke="url(#coachGrad)"
          strokeWidth="6"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="transition-all duration-700"
        />
        <defs>
          <linearGradient id="coachGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#8b5cf6" />
            <stop offset="100%" stopColor="#3b82f6" />
          </linearGradient>
        </defs>
      </svg>
      <span className="absolute text-lg font-bold text-white">
        {isCount ? Math.round(score) : `${Math.round(score)}%`}
      </span>
    </div>
  );
}

export function CoachScoreCards({ scores }: { scores: CoachScoreCard[] }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
      {scores.map((card, i) => {
        const isCount = card.label === "AI Recommendations";
        const trendUp = card.trend === "up";
        const trendDown = card.trend === "down";

        return (
          <div
            key={card.label}
            className={`group relative overflow-hidden rounded-2xl border border-violet-500/15 bg-gradient-to-br ${GRADIENTS[i % GRADIENTS.length]} p-5 backdrop-blur-xl transition hover:border-violet-500/30 hover:shadow-lg hover:shadow-violet-500/10`}
          >
            <div className="absolute -right-4 -top-4 h-24 w-24 rounded-full bg-violet-500/5 blur-2xl" />
            <div className="flex items-start justify-between">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-white/5 text-violet-300 ring-1 ring-white/10">
                {ICONS[card.label] ?? <Briefcase className="h-4 w-4" />}
              </div>
              {!isCount && card.delta !== 0 && (
                <span
                  className={`flex items-center gap-0.5 text-xs font-medium ${
                    trendUp ? "text-emerald-400" : trendDown ? "text-rose-400" : "text-slate-400"
                  }`}
                >
                  <TrendingUp className={`h-3 w-3 ${trendDown ? "rotate-180" : ""}`} />
                  {trendUp ? "+" : ""}
                  {card.delta}
                </span>
              )}
            </div>
            <div className="mt-4 flex items-center gap-4">
              <ScoreRing score={card.score} isCount={isCount} />
              <div className="min-w-0 flex-1">
                <p className="text-sm font-semibold text-white">{card.label}</p>
                <p className="mt-1 text-xs text-slate-400">{card.subtitle}</p>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
