"use client";

import { useEffect, useRef, useState } from "react";
import {
  Bot,
  Send,
  Video,
  Loader2,
  ChevronRight,
  Trophy,
  RotateCcw,
} from "lucide-react";
import { GlassCard } from "@/components/ui/GlassCard";
import { ConfidenceMeter } from "@/components/ui/ConfidenceMeter";
import { AnimatedSection } from "@/components/ui/AnimatedSection";
import { InterviewSetup } from "@/components/interview/InterviewSetup";
import { VoiceRecorder } from "@/components/interview/VoiceRecorder";
import { startInterview, submitInterviewAnswer } from "@/lib/api";
import type {
  InterviewQuestion,
  InterviewSummary,
  TurnFeedback,
} from "@/lib/types/interview";

type Phase = "setup" | "question" | "analyzing" | "feedback" | "complete";

const TYPE_LABELS: Record<string, string> = {
  hr: "HR Interview",
  technical: "Technical Interview",
  behavioral: "Behavioral Interview",
};

export function InterviewCoach() {
  const [phase, setPhase] = useState<Phase>("setup");
  const [starting, setStarting] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [interviewType, setInterviewType] = useState("");
  const [questionIndex, setQuestionIndex] = useState(0);
  const [totalQuestions, setTotalQuestions] = useState(5);
  const [currentQuestion, setCurrentQuestion] = useState<InterviewQuestion | null>(null);
  const [lastFeedback, setLastFeedback] = useState<TurnFeedback | null>(null);
  const [summary, setSummary] = useState<InterviewSummary | null>(null);
  const [input, setInput] = useState("");
  const [liveTranscript, setLiveTranscript] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pendingQuestion, setPendingQuestion] = useState<InterviewQuestion | null>(null);

  const [micOn, setMicOn] = useState(false);
  const [cameraOn, setCameraOn] = useState(false);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  const liveConfidence = lastFeedback?.scores?.confidence
    ?? (lastFeedback?.confidence_score
      ? Math.round(lastFeedback.confidence_score * 10)
      : 72);

  useEffect(() => {
    let stream: MediaStream | null = null;
    async function startCamera() {
      if (!cameraOn || phase === "setup") return;
      try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
        if (videoRef.current) videoRef.current.srcObject = stream;
        setCameraError(null);
      } catch {
        setCameraError("Camera access denied.");
        setCameraOn(false);
      }
    }
    startCamera();
    return () => stream?.getTracks().forEach((t) => t.stop());
  }, [cameraOn, phase]);

  async function handleStart(typeId: string) {
    setStarting(true);
    setError(null);
    try {
      const res = await startInterview(typeId, 5);
      setSessionId(res.session_id);
      setInterviewType(res.interview_type);
      setTotalQuestions(res.total_questions);
      setQuestionIndex(1);
      setCurrentQuestion(res.current_question);
      setPhase("question");
      setLastFeedback(null);
      setSummary(null);
    } catch {
      setError("Could not start interview — is the backend running?");
    } finally {
      setStarting(false);
    }
  }

  async function handleSubmit() {
    if (!input.trim() || !sessionId || phase !== "question") return;
    const answer = input.trim();
    setInput("");
    setPhase("analyzing");
    setError(null);
    try {
      const res = await submitInterviewAnswer(sessionId, answer);
      setLastFeedback(res.turn);
      if (res.completed && res.summary) {
        setSummary(res.summary);
        setPhase("complete");
        setCurrentQuestion(null);
        setPendingQuestion(null);
      } else if (res.next_question) {
        setPendingQuestion(res.next_question);
        setPhase("feedback");
      }
    } catch {
      setError("Failed to submit answer.");
      setPhase("question");
    }
  }

  function continueToNext() {
    if (pendingQuestion) {
      setCurrentQuestion(pendingQuestion);
      setPendingQuestion(null);
      setQuestionIndex((i) => i + 1);
      setPhase("question");
    }
  }

  function reset() {
    setPhase("setup");
    setSessionId(null);
    setCurrentQuestion(null);
    setLastFeedback(null);
    setSummary(null);
    setPendingQuestion(null);
    setInput("");
    setError(null);
  }

  if (phase === "setup") {
    return (
      <>
        <InterviewSetup onStart={handleStart} loading={starting} />
        {error && <p className="mt-4 text-sm text-red-400">{error}</p>}
      </>
    );
  }

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      <AnimatedSection className="space-y-4 lg:col-span-1">
        <GlassCard className="overflow-hidden p-0" hover={false}>
          <div className="relative aspect-[4/3] bg-slate-900">
            {cameraOn && !cameraError ? (
              <video ref={videoRef} autoPlay playsInline muted className="h-full w-full object-cover" />
            ) : (
              <div className="flex h-full flex-col items-center justify-center gap-2 p-4 text-center">
                <Video className="h-10 w-10 text-violet-400/60" />
                <p className="text-xs text-slate-500">{cameraError ?? "Optional webcam preview"}</p>
              </div>
            )}
            <div className="absolute bottom-3 left-0 right-0 flex justify-center gap-3">
              <button
                type="button"
                onClick={() => setCameraOn(!cameraOn)}
                className={`flex h-10 w-10 items-center justify-center rounded-full ${
                  cameraOn ? "bg-violet-600 text-white" : "bg-slate-800/90 text-slate-400"
                }`}
              >
                <Video className="h-4 w-4" />
              </button>
              <VoiceRecorder
                active={micOn}
                onActiveChange={setMicOn}
                onLiveTranscript={setLiveTranscript}
                onTranscript={(text) => {
                  setInput((prev) => (prev ? `${prev} ${text}` : text).trim());
                  setLiveTranscript("");
                }}
              />
            </div>
          </div>
        </GlassCard>

        <GlassCard className="p-5" hover={false}>
          <ConfidenceMeter value={liveConfidence} label="Confidence" />
          {lastFeedback?.scores && (
            <div className="mt-4 grid grid-cols-2 gap-2 text-center">
              <ScorePill label="Communication" value={lastFeedback.scores.communication} pct />
              <ScorePill label="Technical" value={lastFeedback.scores.technical_score} pct />
            </div>
          )}
        </GlassCard>

        <button
          onClick={reset}
          className="flex w-full items-center justify-center gap-2 rounded-xl border border-white/10 py-2 text-xs text-slate-400 hover:bg-white/5"
        >
          <RotateCcw className="h-3.5 w-3.5" />
          End & choose new type
        </button>
      </AnimatedSection>

      <AnimatedSection delay={100} className="lg:col-span-2">
        <GlassCard className="flex min-h-[520px] flex-col overflow-hidden p-0" hover={false}>
          <div className="flex items-center justify-between border-b border-violet-500/10 px-5 py-4">
            <div>
              <h2 className="font-semibold text-white">AI Interviewer</h2>
              <p className="text-xs text-slate-500">
                {TYPE_LABELS[interviewType] ?? interviewType}
                {phase !== "complete" && ` · Q ${questionIndex}/${totalQuestions}`}
              </p>
            </div>
            {phase !== "complete" && (
              <span className="flex items-center gap-1.5 rounded-full bg-emerald-500/10 px-3 py-1 text-xs text-emerald-400 ring-1 ring-emerald-500/20">
                <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-400" />
                Live
              </span>
            )}
          </div>

          <div className="flex-1 space-y-4 overflow-y-auto p-5">
            {phase === "complete" && summary && (
              <CompleteSummary summary={summary} onRestart={reset} />
            )}

            {phase !== "complete" && currentQuestion && (
              <div className="flex gap-3">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-violet-500/20">
                  <Bot className="h-4 w-4 text-violet-400" />
                </div>
                <div className="max-w-[90%] rounded-2xl rounded-tl-sm bg-violet-500/10 px-4 py-3 ring-1 ring-violet-500/20">
                  <p className="text-sm font-medium text-violet-300">
                    {currentQuestion.category} · {currentQuestion.difficulty}
                  </p>
                  <p className="mt-1 text-sm text-slate-100">{currentQuestion.text}</p>
                  <p className="mt-2 text-[11px] text-slate-500">Tip: {currentQuestion.tips}</p>
                </div>
              </div>
            )}

            {phase === "analyzing" && (
              <div className="flex items-center gap-3 pl-11">
                <Loader2 className="h-5 w-5 animate-spin text-violet-400" />
                <p className="text-sm text-slate-400">Analyzing your answer…</p>
              </div>
            )}

            {phase === "feedback" && lastFeedback && (
              <FeedbackCard feedback={lastFeedback} onContinue={continueToNext} />
            )}
          </div>

          {phase === "question" && micOn && liveTranscript && (
            <div className="border-t border-emerald-500/10 bg-emerald-950/20 px-5 py-2">
              <p className="text-[10px] font-medium uppercase tracking-wide text-emerald-400">
                Live transcription
              </p>
              <p className="text-sm text-slate-200">{liveTranscript}</p>
            </div>
          )}

          {phase === "question" && (
            <div className="border-t border-violet-500/10 p-4">
              <div className="flex gap-3">
                <input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
                  placeholder="Type or use the mic for live transcription…"
                  className="flex-1 rounded-xl border border-violet-500/20 bg-slate-900/80 px-4 py-3 text-sm text-white placeholder:text-slate-500 focus:border-violet-500/50 focus:outline-none"
                />
                <button
                  onClick={handleSubmit}
                  disabled={!input.trim()}
                  className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-violet-600 to-blue-600 px-5 py-3 text-sm font-semibold text-white disabled:opacity-40"
                >
                  <Send className="h-4 w-4" />
                  Submit
                </button>
              </div>
            </div>
          )}
          {error && <p className="px-5 pb-3 text-xs text-red-400">{error}</p>}
        </GlassCard>
      </AnimatedSection>
    </div>
  );
}

function ScorePill({
  label,
  value,
  pct = false,
}: {
  label: string;
  value: number;
  pct?: boolean;
}) {
  return (
    <div className="rounded-lg bg-white/5 px-2 py-2">
      <p className="text-[10px] text-slate-500">{label}</p>
      <p className="text-sm font-bold text-white">
        {pct ? `${Math.round(value)}%` : value.toFixed(1)}
      </p>
    </div>
  );
}

function FeedbackCard({
  feedback,
  onContinue,
}: {
  feedback: TurnFeedback;
  onContinue: () => void;
}) {
  const scores = feedback.scores;
  const ideal = feedback.ideal_comparison;

  return (
    <div className="rounded-xl border border-emerald-500/20 bg-emerald-950/20 p-4">
      <p className="text-xs font-semibold uppercase tracking-wide text-emerald-400">
        {scores ? `Overall ${scores.overall}%` : `Score ${feedback.overall_score}/10`}
        {feedback.used_llm && (
          <span className="ml-2 rounded bg-violet-500/20 px-1.5 py-0.5 text-[10px] text-violet-300">
            AI eval
          </span>
        )}
      </p>
      {scores && (
        <div className="mt-3 grid grid-cols-3 gap-2 text-center text-[10px]">
          <Metric label="Communication" value={scores.communication} />
          <Metric label="Technical" value={scores.technical_score} />
          <Metric label="Confidence" value={scores.confidence} />
          <Metric label="Relevance" value={scores.relevance} />
          <Metric label="Grammar" value={scores.grammar} />
          <Metric label="Keywords" value={scores.keyword_match} />
        </div>
      )}
      <p className="mt-2 text-sm text-slate-200">{feedback.feedback_summary}</p>
      {ideal && (
        <div className="mt-4 rounded-lg border border-violet-500/20 bg-violet-950/30 p-3">
          <p className="text-[10px] font-semibold uppercase text-violet-400">
            Ideal answer comparison · {ideal.similarity_pct}% similar
          </p>
          <p className="mt-1 text-xs text-slate-300">{ideal.expert_answer}</p>
          {ideal.matched_keywords.length > 0 && (
            <p className="mt-2 text-[10px] text-emerald-400/90">
              Matched: {ideal.matched_keywords.join(", ")}
            </p>
          )}
          {ideal.missing_keywords.length > 0 && (
            <p className="mt-1 text-[10px] text-amber-400/80">
              Add: {ideal.missing_keywords.join(", ")}
            </p>
          )}
        </div>
      )}
      {feedback.strengths.length > 0 && (
        <ul className="mt-3 space-y-1">
          {feedback.strengths.map((s, i) => (
            <li key={i} className="text-xs text-emerald-300/90">
              + {s}
            </li>
          ))}
        </ul>
      )}
      {feedback.improvements.length > 0 && (
        <ul className="mt-2 space-y-1">
          {feedback.improvements.map((s, i) => (
            <li key={i} className="text-xs text-amber-300/80">
              → {s}
            </li>
          ))}
        </ul>
      )}
      <button
        onClick={onContinue}
        className="mt-4 inline-flex items-center gap-2 rounded-lg bg-violet-600 px-4 py-2 text-sm font-semibold text-white hover:bg-violet-500"
      >
        Next question
        <ChevronRight className="h-4 w-4" />
      </button>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-md bg-white/5 px-1 py-1.5">
      <p className="text-slate-500">{label}</p>
      <p className="font-bold text-white">{value}%</p>
    </div>
  );
}

function CompleteSummary({
  summary,
  onRestart,
}: {
  summary: InterviewSummary;
  onRestart: () => void;
}) {
  return (
    <div className="rounded-xl border border-violet-500/30 bg-violet-950/30 p-6 text-center">
      <Trophy className="mx-auto h-10 w-10 text-amber-400" />
      <h3 className="mt-3 text-lg font-bold text-white">Interview complete</h3>
      <p className="mt-1 text-3xl font-bold text-violet-300">{summary.overall_score}/10</p>
      <p className="text-sm text-slate-400">
        {summary.questions_answered} questions · Communication {summary.communication_score} ·
        Technical {summary.technical_score}
      </p>
      <button
        onClick={onRestart}
        className="mt-6 inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-violet-600 to-blue-600 px-6 py-2.5 text-sm font-semibold text-white"
      >
        <RotateCcw className="h-4 w-4" />
        Practice again
      </button>
    </div>
  );
}
