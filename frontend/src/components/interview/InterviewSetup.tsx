"use client";

import { useEffect, useState } from "react";
import { Users, Code, MessageCircle, Sparkles, Loader2 } from "lucide-react";
import { GlassCard } from "@/components/ui/GlassCard";
import { getInterviewTypes } from "@/lib/api";
import type { InterviewTypeInfo } from "@/lib/types/interview";

const ICONS: Record<string, typeof Users> = {
  hr: Users,
  technical: Code,
  behavioral: MessageCircle,
};

type Props = {
  onStart: (typeId: string) => void;
  loading?: boolean;
};

export function InterviewSetup({ onStart, loading }: Props) {
  const [types, setTypes] = useState<InterviewTypeInfo[]>([]);
  const [fetching, setFetching] = useState(true);

  useEffect(() => {
    getInterviewTypes()
      .then(setTypes)
      .catch(() => {
        setTypes([
          {
            id: "hr",
            label: "HR Interview",
            description: "Introduction, strengths, motivation, and culture fit.",
            examples: ["Tell me about yourself", "Strengths & weaknesses"],
            question_count: 6,
          },
          {
            id: "technical",
            label: "Technical Interview",
            description: "DSA, AI/ML, and web development fundamentals.",
            examples: ["Data structures", "REST APIs", "ML concepts"],
            question_count: 7,
          },
          {
            id: "behavioral",
            label: "Behavioral Interview",
            description: "Teamwork, leadership, conflict (STAR method).",
            examples: ["Team projects", "Conflict resolution"],
            question_count: 6,
          },
        ]);
      })
      .finally(() => setFetching(false));
  }, []);

  if (fetching) {
    return (
      <div className="flex min-h-[320px] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-violet-400" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <GlassCard className="p-6" hover={false}>
        <div className="flex items-start gap-3">
          <Sparkles className="mt-0.5 h-5 w-5 shrink-0 text-violet-400" />
          <div>
            <h2 className="font-semibold text-white">Choose your interview type</h2>
            <p className="mt-1 text-sm text-slate-400">
              The AI coach will ask real questions, analyze your answers, and give scores +
              feedback after each one.
            </p>
          </div>
        </div>
      </GlassCard>

      <div className="grid gap-4 md:grid-cols-3">
        {types.map((t) => {
          const Icon = ICONS[t.id] ?? MessageCircle;
          return (
            <button
              key={t.id}
              onClick={() => onStart(t.id)}
              disabled={loading}
              className="group text-left transition disabled:opacity-50"
            >
              <GlassCard className="h-full p-5 transition group-hover:border-violet-500/40 group-hover:shadow-lg group-hover:shadow-violet-500/10">
                <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-violet-600/30 to-blue-600/20 ring-1 ring-violet-500/20">
                  <Icon className="h-5 w-5 text-violet-400" />
                </div>
                <h3 className="font-semibold text-white">{t.label}</h3>
                <p className="mt-1 text-xs text-slate-400">{t.description}</p>
                <ul className="mt-3 space-y-1">
                  {t.examples.map((ex) => (
                    <li key={ex} className="text-[11px] text-slate-500">
                      · {ex}
                    </li>
                  ))}
                </ul>
                <p className="mt-3 text-[10px] font-medium uppercase tracking-wide text-violet-400">
                  {t.question_count} questions in bank
                </p>
              </GlassCard>
            </button>
          );
        })}
      </div>
    </div>
  );
}
