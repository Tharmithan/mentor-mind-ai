"use client";

import { useState } from "react";
import Link from "next/link";
import { MessageCircle, X, Sparkles, LayoutDashboard, Mic, Send } from "lucide-react";

const QUICK_REPLIES = [
  "How can I improve my weakest subject?",
  "What should I practice for interviews?",
  "How do I use the dashboard?",
];

export function FloatingAIAssistant() {
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState("");
  const [reply, setReply] = useState<string | null>(null);

  const handleSend = () => {
    const trimmed = message.trim();
    if (!trimmed) return;
    setReply(
      "Thanks! Full AI chat arrives in Week 2. For now, check your Dashboard for personalized insights and try a Mock Interview."
    );
    setMessage("");
  };

  return (
    <>
      {open && (
        <div
          className="fixed bottom-24 right-4 z-50 w-[min(100vw-2rem,22rem)] overflow-hidden rounded-2xl border border-violet-500/25 bg-[#0f0a1e]/95 shadow-2xl shadow-violet-900/40 backdrop-blur-xl animate-fade-in-up sm:right-6"
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
                <p className="text-xs text-violet-300/80">Your learning coach</p>
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

          <div className="space-y-2 p-4">
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

          <div className="max-h-32 space-y-2 overflow-y-auto px-4 pb-2">
            {QUICK_REPLIES.map((q) => (
              <button
                key={q}
                type="button"
                onClick={() => {
                  setMessage(q);
                  setReply(
                    "Great question! Open your Dashboard for performance insights, or start a Mock Interview to practice."
                  );
                }}
                className="block w-full rounded-lg border border-violet-500/10 bg-slate-900/50 px-3 py-2 text-left text-xs text-slate-300 hover:border-violet-500/25"
              >
                {q}
              </button>
            ))}
            {reply && (
              <p className="rounded-lg bg-violet-500/10 px-3 py-2 text-xs leading-relaxed text-violet-100">
                {reply}
              </p>
            )}
          </div>

          <div className="flex gap-2 border-t border-violet-500/10 p-3">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              placeholder="Ask MentorMind…"
              className="flex-1 rounded-xl border border-violet-500/20 bg-slate-900/60 px-3 py-2 text-sm text-white placeholder:text-slate-500 focus:border-violet-500/50 focus:outline-none"
            />
            <button
              type="button"
              onClick={handleSend}
              className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-violet-600 to-blue-600 text-white hover:opacity-90"
              aria-label="Send message"
            >
              <Send className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}

      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="fixed bottom-6 right-4 z-50 flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-br from-violet-600 to-blue-600 text-white shadow-lg shadow-violet-600/40 transition hover:scale-105 hover:shadow-violet-500/50 sm:right-6 animate-pulse-glow"
        aria-label={open ? "Close AI assistant" : "Open AI assistant"}
        aria-expanded={open}
      >
        {open ? <X className="h-6 w-6" /> : <MessageCircle className="h-6 w-6" />}
      </button>
    </>
  );
}
