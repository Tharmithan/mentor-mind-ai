"use client";

import { useState } from "react";
import Link from "next/link";
import { MessageCircle, X, Sparkles, LayoutDashboard, Mic, Send, Loader2 } from "lucide-react";
import { agentChat } from "@/lib/api";
import type { AgentAction, AgentContribution } from "@/lib/types/api";
import { Markdown } from "@/components/assistant/Markdown";

const QUICK_REPLIES = [
  "I have a Machine Learning exam in 14 days",
  "Which career path fits me best?",
  "Help me become an AI Engineer — full career prep",
  "Start a behavioral mock interview",
];

type Turn = {
  role: "user" | "assistant";
  content: string;
  agentLabel?: string;
  actions?: AgentAction[];
  collaboration?: boolean;
  contributions?: AgentContribution[];
};

const AGENT_COLORS: Record<string, string> = {
  career: "border-emerald-500/30 bg-emerald-500/10",
  study: "border-blue-500/30 bg-blue-500/10",
  interview: "border-amber-500/30 bg-amber-500/10",
  resume: "border-rose-500/30 bg-rose-500/10",
};

function ContributionCards({ contributions }: { contributions: AgentContribution[] }) {
  return (
    <div className="mt-2 space-y-1.5">
      {contributions.map((c) => (
        <div
          key={c.agent}
          className={`rounded-lg border px-2.5 py-1.5 ${AGENT_COLORS[c.agent] ?? "border-violet-500/20 bg-violet-500/5"}`}
        >
          <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-300">
            {c.agent_label}
          </p>
          <div className="prose-invert text-[11px] [&_*]:text-[11px]">
            <Markdown text={c.summary} />
          </div>
        </div>
      ))}
    </div>
  );
}

function ActionLinks({ actions }: { actions: AgentAction[] }) {
  return (
    <div className="mt-2 flex flex-wrap gap-2">
      {actions.map((action, i) => {
        if (action.path) {
          return (
            <Link
              key={`${action.type}-${i}`}
              href={action.path}
              className="inline-flex rounded-lg border border-violet-500/25 bg-violet-500/10 px-2.5 py-1 text-[11px] font-medium text-violet-200 hover:bg-violet-500/20"
            >
              {action.type.replace(/_/g, " ")}
            </Link>
          );
        }
        return null;
      })}
    </div>
  );
}

export function FloatingAIAssistant() {
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [turns, setTurns] = useState<Turn[]>([
    {
      role: "assistant",
      content:
        "Hi! I'm your **AI Study Tutor**. I can build exam plans, suggest daily study tasks, track learning goals, and analyze weak subjects — ask me anything!",
    },
  ]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || loading) return;

    setError(null);
    setTurns((prev) => [...prev, { role: "user", content: trimmed }]);
    setMessage("");
    setLoading(true);

    try {
      const res = await agentChat({
        message: trimmed,
        session_id: sessionId,
      });
      setSessionId(res.session_id);
      setTurns((prev) => [
        ...prev,
        {
          role: "assistant",
          content: res.answer,
          agentLabel: res.agent_label,
          actions: res.actions,
          collaboration: res.collaboration,
          contributions: res.contributions ?? undefined,
        },
      ]);
    } catch {
      setError("Couldn't reach the AI agent. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {open && (
        <div
          className="fixed bottom-24 right-4 z-50 flex w-[min(100vw-2rem,22rem)] flex-col overflow-hidden rounded-2xl border border-violet-500/25 bg-[#0f0a1e]/95 shadow-2xl shadow-violet-900/40 backdrop-blur-xl animate-fade-in-up sm:right-6"
          role="dialog"
          aria-label="AI Assistant"
        >
          <div className="flex items-center justify-between border-b border-violet-500/15 bg-gradient-to-r from-violet-600/20 to-blue-600/10 px-4 py-3">
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-violet-600/40">
                <Sparkles className="h-4 w-4 text-violet-300" />
              </div>
              <div>
                <p className="text-sm font-semibold text-white">MentorMind AI</p>
                <p className="text-xs text-violet-300/80">Career & learning copilot</p>
              </div>
            </div>
            <button
              type="button"
              onClick={() => setOpen(false)}
              className="rounded-lg p-1.5 text-slate-400 hover:bg-white/5 hover:text-white"
              aria-label="Close assistant"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          <div className="space-y-2 border-b border-violet-500/10 p-4">
            <p className="text-xs text-slate-500">Quick actions</p>
            <div className="flex flex-wrap gap-2">
              <Link
                href="/dashboard"
                onClick={() => setOpen(false)}
                className="inline-flex items-center gap-1.5 rounded-lg border border-violet-500/20 bg-violet-500/10 px-3 py-1.5 text-xs font-medium text-violet-200 hover:bg-violet-500/20"
              >
                <LayoutDashboard className="h-3.5 w-3.5" />
                Dashboard
              </Link>
              <Link
                href="/interview"
                onClick={() => setOpen(false)}
                className="inline-flex items-center gap-1.5 rounded-lg border border-violet-500/20 bg-violet-500/10 px-3 py-1.5 text-xs font-medium text-violet-200 hover:bg-violet-500/20"
              >
                <Mic className="h-3.5 w-3.5" />
                Mock Interview
              </Link>
            </div>
          </div>

          <div className="max-h-52 space-y-2 overflow-y-auto px-4 py-3">
            {turns.map((turn, i) => (
              <div
                key={i}
                className={`rounded-lg px-3 py-2 text-xs leading-relaxed ${
                  turn.role === "user"
                    ? "ml-6 bg-slate-800/80 text-slate-200"
                    : "mr-2 bg-violet-500/10 text-violet-100"
                }`}
              >
                {turn.agentLabel && turn.role === "assistant" && (
                  <p className="mb-1 text-[10px] font-semibold uppercase tracking-wide text-violet-300/70">
                    {turn.collaboration ? "🤝 " : ""}
                    {turn.agentLabel}
                  </p>
                )}
                {turn.role === "assistant" ? (
                  <div className="prose-invert text-xs [&_*]:text-xs">
                    <Markdown text={turn.content} />
                  </div>
                ) : (
                  turn.content
                )}
                {turn.contributions && turn.contributions.length > 0 && (
                  <ContributionCards contributions={turn.contributions} />
                )}
                {turn.actions && turn.actions.length > 0 && (
                  <ActionLinks actions={turn.actions} />
                )}
              </div>
            ))}
            {loading && (
              <div className="flex items-center gap-2 px-3 py-2 text-xs text-violet-300/80">
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
                Agents collaborating…
              </div>
            )}
            {error && (
              <p className="rounded-lg bg-red-500/10 px-3 py-2 text-xs text-red-300">{error}</p>
            )}
          </div>

          <div className="flex flex-wrap gap-2 px-4 pb-2">
            {QUICK_REPLIES.map((q) => (
              <button
                key={q}
                type="button"
                disabled={loading}
                onClick={() => sendMessage(q)}
                className="rounded-lg border border-violet-500/10 bg-slate-900/50 px-2.5 py-1.5 text-left text-[11px] text-slate-300 hover:border-violet-500/25 disabled:opacity-50"
              >
                {q}
              </button>
            ))}
          </div>

          <div className="flex gap-2 border-t border-violet-500/10 p-3">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage(message)}
              placeholder="Ask MentorMind…"
              disabled={loading}
              className="flex-1 rounded-xl border border-violet-500/20 bg-slate-900/60 px-3 py-2 text-sm text-white placeholder:text-slate-500 focus:border-violet-500/50 focus:outline-none disabled:opacity-60"
            />
            <button
              type="button"
              onClick={() => sendMessage(message)}
              disabled={loading || !message.trim()}
              className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-violet-600 to-blue-600 text-white hover:opacity-90 disabled:opacity-50"
              aria-label="Send message"
            >
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
            </button>
          </div>
        </div>
      )}

      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="fixed bottom-20 right-4 z-50 flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-br from-violet-600 to-blue-600 text-white shadow-lg shadow-violet-600/40 transition hover:scale-105 hover:shadow-violet-500/50 sm:right-6 md:bottom-6 animate-pulse-glow"
        aria-label={open ? "Close AI assistant" : "Open AI assistant"}
        aria-expanded={open}
      >
        {open ? <X className="h-6 w-6" /> : <MessageCircle className="h-6 w-6" />}
      </button>
    </>
  );
}
