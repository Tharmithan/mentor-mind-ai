"use client";

import { useState } from "react";
import {
  FileText,
  ListChecks,
  Layers,
  Baby,
  GraduationCap,
  Loader2,
  Sparkles,
} from "lucide-react";
import { GlassCard } from "@/components/ui/GlassCard";
import {
  explainSimply,
  generateFlashcards,
  generateQuiz,
  generateRevision,
  summarizeDocument,
} from "@/lib/api";
import type {
  ExplainSimpleResponse,
  FlashcardResponse,
  QuizResponse,
  RevisionResponse,
  SummaryResponse,
} from "@/lib/types/api";

type ToolId = "summary" | "quiz" | "flashcards" | "explain" | "revision";

const TOOLS: { id: ToolId; label: string; icon: typeof FileText; desc: string }[] = [
  { id: "summary", label: "Summarize", icon: FileText, desc: "Key points of your notes" },
  { id: "quiz", label: "Quiz", icon: ListChecks, desc: "Auto-generated MCQs" },
  { id: "flashcards", label: "Flashcards", icon: Layers, desc: "Revision cards" },
  { id: "explain", label: "Explain simply", icon: Baby, desc: "Beginner-friendly" },
  { id: "revision", label: "Exam Revision", icon: GraduationCap, desc: "Last-minute sheet" },
];

type Result =
  | { kind: "summary"; data: SummaryResponse }
  | { kind: "quiz"; data: QuizResponse }
  | { kind: "flashcards"; data: FlashcardResponse }
  | { kind: "explain"; data: ExplainSimpleResponse }
  | { kind: "revision"; data: RevisionResponse };

export function StudyToolsPanel({
  activeDoc,
  hasDocs,
}: {
  activeDoc: string | null;
  hasDocs: boolean;
}) {
  const [tool, setTool] = useState<ToolId>("summary");
  const [concept, setConcept] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<Result | null>(null);

  async function run() {
    setError(null);
    setResult(null);
    setLoading(true);
    try {
      const body = { document_id: activeDoc, count: 5 };
      if (tool === "summary") setResult({ kind: "summary", data: await summarizeDocument(body) });
      else if (tool === "quiz") setResult({ kind: "quiz", data: await generateQuiz(body) });
      else if (tool === "flashcards")
        setResult({ kind: "flashcards", data: await generateFlashcards(body) });
      else if (tool === "revision")
        setResult({ kind: "revision", data: await generateRevision(body) });
      else if (tool === "explain") {
        if (!concept.trim()) {
          setError("Type a concept to explain.");
          return;
        }
        setResult({ kind: "explain", data: await explainSimply(concept.trim(), activeDoc) });
      }
    } catch (e) {
      setError(
        e && typeof e === "object" && "message" in e
          ? String((e as { message: unknown }).message)
          : "Something went wrong."
      );
    } finally {
      setLoading(false);
    }
  }

  const needsDoc = tool !== "explain";

  return (
    <GlassCard className="flex h-[calc(100vh-16rem)] min-h-[480px] flex-col p-5" hover={false}>
      {/* Tool selector */}
      <div className="flex flex-wrap gap-2">
        {TOOLS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => {
              setTool(id);
              setResult(null);
              setError(null);
            }}
            className={`inline-flex items-center gap-1.5 rounded-xl px-3 py-2 text-xs font-semibold transition ${
              tool === id
                ? "bg-gradient-to-r from-violet-600 to-blue-600 text-white shadow-lg shadow-violet-500/25"
                : "border border-violet-500/20 bg-violet-950/30 text-slate-300 hover:bg-violet-900/30"
            }`}
          >
            <Icon className="h-3.5 w-3.5" />
            {label}
          </button>
        ))}
      </div>

      {/* Controls */}
      <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center">
        {tool === "explain" && (
          <input
            value={concept}
            onChange={(e) => setConcept(e.target.value)}
            placeholder="Concept to explain… e.g. \u201cNeural networks\u201d"
            className="flex-1 rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm text-slate-100 placeholder:text-slate-500 focus:border-violet-500/40 focus:outline-none"
          />
        )}
        <button
          onClick={run}
          disabled={loading || (needsDoc && !hasDocs)}
          className="inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-violet-600 to-blue-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-violet-500/25 transition hover:from-violet-500 hover:to-blue-500 disabled:opacity-40"
        >
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
          {loading ? "Generating…" : "Generate"}
        </button>
      </div>

      {needsDoc && !hasDocs && (
        <p className="mt-3 text-xs text-amber-400/80">
          Upload a document first to use this tool.
        </p>
      )}
      {needsDoc && hasDocs && (
        <p className="mt-2 text-xs text-slate-500">
          Source: {activeDoc ? "selected document" : "all documents"}
        </p>
      )}
      {error && <p className="mt-3 text-xs text-red-400">{error}</p>}

      {/* Result */}
      <div className="mt-4 flex-1 overflow-y-auto">
        {result?.kind === "summary" && <SummaryView data={result.data} />}
        {result?.kind === "quiz" && <QuizView data={result.data} />}
        {result?.kind === "flashcards" && <FlashcardsView data={result.data} />}
        {result?.kind === "explain" && <ExplainView data={result.data} />}
        {result?.kind === "revision" && <RevisionView data={result.data} />}
        {!result && !loading && (
          <div className="flex h-full items-center justify-center text-center text-sm text-slate-500">
            Pick a tool and hit Generate.
          </div>
        )}
      </div>
    </GlassCard>
  );
}

function LlmBadge({ used }: { used: boolean }) {
  return (
    <span
      className={`rounded-md px-2 py-0.5 text-[10px] font-medium ${
        used ? "bg-emerald-500/15 text-emerald-300" : "bg-slate-700/50 text-slate-400"
      }`}
    >
      {used ? "AI-generated" : "Extractive (no LLM key)"}
    </span>
  );
}

function SummaryView({ data }: { data: SummaryResponse }) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-white">{data.title}</h3>
        <LlmBadge used={data.used_llm} />
      </div>
      <p className="text-sm leading-relaxed text-slate-300">{data.summary}</p>
      <ul className="space-y-1.5">
        {data.key_points.map((p, i) => (
          <li key={i} className="flex gap-2 text-sm text-slate-300">
            <span className="text-violet-400">•</span>
            {p}
          </li>
        ))}
      </ul>
    </div>
  );
}

function QuizView({ data }: { data: QuizResponse }) {
  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <LlmBadge used={data.used_llm} />
      </div>
      {data.questions.map((q, i) => (
        <QuizItem key={i} index={i} question={q} />
      ))}
    </div>
  );
}

function QuizItem({
  index,
  question,
}: {
  index: number;
  question: QuizResponse["questions"][number];
}) {
  const [picked, setPicked] = useState<number | null>(null);
  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-4">
      <p className="mb-3 text-sm font-medium text-slate-100">
        {index + 1}. {question.question}
      </p>
      <div className="space-y-2">
        {question.options.map((opt, oi) => {
          const isCorrect = oi === question.answer_index;
          const show = picked !== null;
          return (
            <button
              key={oi}
              onClick={() => setPicked(oi)}
              disabled={show}
              className={`flex w-full items-center gap-2 rounded-lg border px-3 py-2 text-left text-xs transition ${
                show && isCorrect
                  ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-200"
                  : show && picked === oi
                    ? "border-red-500/40 bg-red-500/10 text-red-200"
                    : "border-white/10 text-slate-300 hover:bg-white/5"
              }`}
            >
              <span className="font-semibold">{String.fromCharCode(65 + oi)}.</span>
              {opt}
            </button>
          );
        })}
      </div>
      {picked !== null && question.explanation && (
        <p className="mt-2 text-[11px] text-slate-400">{question.explanation}</p>
      )}
    </div>
  );
}

function FlashcardsView({ data }: { data: FlashcardResponse }) {
  return (
    <div className="space-y-3">
      <div className="flex justify-end">
        <LlmBadge used={data.used_llm} />
      </div>
      <div className="grid gap-3 sm:grid-cols-2">
        {data.flashcards.map((c, i) => (
          <FlashcardItem key={i} front={c.front} back={c.back} />
        ))}
      </div>
    </div>
  );
}

function FlashcardItem({ front, back }: { front: string; back: string }) {
  const [flipped, setFlipped] = useState(false);
  return (
    <button
      onClick={() => setFlipped((f) => !f)}
      className="min-h-[110px] rounded-xl border border-violet-500/20 bg-violet-950/30 p-4 text-left transition hover:border-violet-500/40"
    >
      <p className="text-[10px] uppercase tracking-wide text-violet-400">
        {flipped ? "Answer" : "Question"} · tap to flip
      </p>
      <p className="mt-1.5 text-sm text-slate-200">{flipped ? back : front}</p>
    </button>
  );
}

function ExplainView({ data }: { data: ExplainSimpleResponse }) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-white">{data.concept}</h3>
        <LlmBadge used={data.used_llm} />
      </div>
      <p className="text-sm leading-relaxed text-slate-300">{data.explanation}</p>
      {data.analogy && (
        <div className="rounded-xl border border-blue-500/20 bg-blue-950/20 p-3">
          <p className="text-[10px] uppercase tracking-wide text-blue-300">Think of it like…</p>
          <p className="mt-1 text-sm text-slate-300">{data.analogy}</p>
        </div>
      )}
    </div>
  );
}

function RevisionView({ data }: { data: RevisionResponse }) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-white">{data.title}</h3>
        <LlmBadge used={data.used_llm} />
      </div>
      <Section title="Quick notes" items={data.quick_notes} />
      {data.key_formulas.length > 0 && (
        <div>
          <p className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-violet-300">
            Key formulas
          </p>
          <div className="flex flex-wrap gap-2">
            {data.key_formulas.map((f, i) => (
              <code
                key={i}
                className="rounded-md border border-white/10 bg-black/30 px-2 py-1 text-xs text-emerald-300"
              >
                {f}
              </code>
            ))}
          </div>
        </div>
      )}
      <Section title="Must know" items={data.must_know} accent />
    </div>
  );
}

function Section({
  title,
  items,
  accent,
}: {
  title: string;
  items: string[];
  accent?: boolean;
}) {
  if (items.length === 0) return null;
  return (
    <div>
      <p className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-violet-300">{title}</p>
      <ul className="space-y-1.5">
        {items.map((it, i) => (
          <li key={i} className="flex gap-2 text-sm text-slate-300">
            <span className={accent ? "text-amber-400" : "text-violet-400"}>•</span>
            {it}
          </li>
        ))}
      </ul>
    </div>
  );
}
