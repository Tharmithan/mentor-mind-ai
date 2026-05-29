"use client";

import { useEffect, useRef, useState } from "react";
import {
  Bot,
  User,
  Send,
  BookOpen,
  ListChecks,
  Lightbulb,
  ChevronDown,
  BrainCircuit,
  RotateCcw,
  Sparkles,
} from "lucide-react";
import { GlassCard } from "@/components/ui/GlassCard";
import { chatWithDocuments, createChatSession, deleteChatSession } from "@/lib/api";
import type { ChatMessage, SearchResult } from "@/lib/types/api";
import { Markdown } from "@/components/assistant/Markdown";
import { ThinkingIndicator } from "@/components/assistant/ThinkingIndicator";

type ChatTurn = ChatMessage & {
  sources?: SearchResult[];
  usedLlm?: boolean;
  animate?: boolean;
};

type Mode = "explain" | "summarize" | "example";

const MODES: { id: Mode; label: string; icon: typeof BookOpen }[] = [
  { id: "explain", label: "Explain", icon: BookOpen },
  { id: "summarize", label: "Summarize", icon: ListChecks },
  { id: "example", label: "Examples", icon: Lightbulb },
];

const SUGGESTIONS = [
  "Summarize this PDF",
  "Generate a quiz on the key topics",
  "Explain the difficult topics simply",
  "What are the most important points?",
];

const WELCOME: ChatTurn = {
  role: "assistant",
  content:
    "Hi! I'm your AI study tutor. Pick a document (or **All documents**) and ask me anything — I'll answer from your material, explain concepts, summarize topics, and give examples.",
};

export function ChatPanel({
  activeDoc,
  hasDocs,
}: {
  activeDoc: string | null;
  hasDocs: boolean;
}) {
  const [messages, setMessages] = useState<ChatTurn[]>([WELCOME]);
  const [input, setInput] = useState("");
  const [thinking, setThinking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [streamChars, setStreamChars] = useState(0);
  const threadRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    createChatSession()
      .then((s) => setSessionId(s.session_id))
      .catch(() => {});
  }, []);

  useEffect(() => {
    threadRef.current?.scrollTo({ top: threadRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, thinking, streamChars]);

  // Typewriter reveal for the latest assistant message.
  useEffect(() => {
    const lastIdx = messages.length - 1;
    const last = messages[lastIdx];
    if (!last || last.role !== "assistant" || !last.animate) return;
    if (streamChars < last.content.length) {
      const id = setTimeout(
        () => setStreamChars((c) => Math.min(last.content.length, c + 4)),
        12
      );
      return () => clearTimeout(id);
    }
    setMessages((m) => m.map((x, i) => (i === lastIdx ? { ...x, animate: false } : x)));
  }, [streamChars, messages]);

  async function newChat() {
    if (sessionId) deleteChatSession(sessionId).catch(() => {});
    setMessages([WELCOME]);
    setInput("");
    setError(null);
    setSessionId(null);
    try {
      const s = await createChatSession();
      setSessionId(s.session_id);
    } catch {
      /* offline — continue without memory */
    }
  }

  async function send(question: string, mode?: Mode) {
    const q = question.trim();
    if (!q || thinking) return;
    setError(null);
    setInput("");

    const history: ChatMessage[] = messages
      .filter((m) => m !== WELCOME)
      .map((m) => ({ role: m.role, content: m.content }));

    setMessages((m) => [...m, { role: "user", content: q }]);
    setThinking(true);
    try {
      const res = await chatWithDocuments({
        question: q,
        top_k: 4,
        document_id: activeDoc,
        mode: mode ?? null,
        session_id: sessionId,
        history,
      });
      if (res.session_id && res.session_id !== sessionId) setSessionId(res.session_id);
      setStreamChars(0);
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content: res.answer,
          sources: res.sources,
          usedLlm: res.used_llm,
          animate: true,
        },
      ]);
    } catch (e) {
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content:
            "Sorry, I couldn't reach the tutor service. Make sure the backend is running, then try again.",
        },
      ]);
      setError(errorMessage(e));
    } finally {
      setThinking(false);
    }
  }

  const fresh = messages.length === 1;

  return (
    <GlassCard className="flex h-[calc(100vh-16rem)] min-h-[480px] flex-col" hover={false}>
      <div className="flex items-center justify-between border-b border-white/5 px-5 py-3">
        <span className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-400">
          <BrainCircuit
            className={`h-3.5 w-3.5 ${sessionId ? "text-emerald-400" : "text-slate-600"}`}
          />
          {sessionId ? "Memory on — I remember this chat" : "Memory off"}
        </span>
        <button
          onClick={newChat}
          className="inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs font-medium text-slate-400 transition hover:bg-white/5 hover:text-slate-200"
        >
          <RotateCcw className="h-3.5 w-3.5" />
          New chat
        </button>
      </div>

      <div ref={threadRef} className="flex-1 space-y-4 overflow-y-auto p-5">
        {messages.map((m, i) => {
          const isLast = i === messages.length - 1;
          const animating = isLast && m.role === "assistant" && !!m.animate;
          return (
            <MessageBubble key={i} turn={m} visibleChars={animating ? streamChars : undefined} />
          );
        })}

        {thinking && (
          <div className="flex items-start gap-3">
            <Avatar role="assistant" />
            <ThinkingIndicator />
          </div>
        )}

        {fresh && (
          <div className="pl-11">
            <p className="mb-2 text-xs font-medium text-slate-500">Try asking…</p>
            <div className="flex flex-wrap gap-2">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => send(s)}
                  className="inline-flex items-center gap-1.5 rounded-full border border-violet-500/20 bg-violet-950/30 px-3 py-1.5 text-xs text-slate-300 transition hover:border-violet-500/40 hover:bg-violet-900/30"
                >
                  <Sparkles className="h-3 w-3 text-violet-400" />
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="flex flex-wrap gap-2 border-t border-white/5 px-5 pt-3">
        {MODES.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => input.trim() && send(input, id)}
            disabled={thinking || !input.trim()}
            className="inline-flex items-center gap-1.5 rounded-full border border-violet-500/20 bg-violet-950/30 px-3 py-1.5 text-xs font-medium text-slate-300 transition hover:bg-violet-900/30 disabled:opacity-40"
          >
            <Icon className="h-3.5 w-3.5 text-violet-400" />
            {label}
          </button>
        ))}
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          send(input);
        }}
        className="flex items-center gap-2 p-4"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={
            hasDocs
              ? "Ask about your notes… e.g. \u201cExplain recursion\u201d"
              : "Upload notes, then ask a question…"
          }
          className="flex-1 rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-100 placeholder:text-slate-500 focus:border-violet-500/40 focus:outline-none focus:ring-1 focus:ring-violet-500/30"
        />
        <button
          type="submit"
          disabled={thinking || !input.trim()}
          className="inline-flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-r from-violet-600 to-blue-600 text-white shadow-lg shadow-violet-500/25 transition hover:from-violet-500 hover:to-blue-500 disabled:opacity-40"
          aria-label="Send"
        >
          <Send className="h-4 w-4" />
        </button>
      </form>
      {error && <p className="px-5 pb-3 text-xs text-red-400">{error}</p>}
    </GlassCard>
  );
}

function Avatar({ role }: { role: ChatMessage["role"] }) {
  if (role === "user") {
    return (
      <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-slate-700">
        <User className="h-4 w-4 text-slate-200" />
      </span>
    );
  }
  return (
    <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-violet-600 to-blue-600 shadow-lg shadow-violet-500/25">
      <Bot className="h-4 w-4 text-white" />
    </span>
  );
}

function MessageBubble({ turn, visibleChars }: { turn: ChatTurn; visibleChars?: number }) {
  const isUser = turn.role === "user";
  const animating = visibleChars !== undefined;
  const content = animating ? turn.content.slice(0, visibleChars) : turn.content;

  return (
    <div className={`flex items-start gap-3 ${isUser ? "flex-row-reverse" : ""}`}>
      <Avatar role={turn.role} />
      <div className={`max-w-[80%] ${isUser ? "items-end text-right" : ""}`}>
        <div
          className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${
            isUser
              ? "whitespace-pre-wrap rounded-tr-sm bg-violet-600 text-white"
              : "rounded-tl-sm bg-white/5 text-slate-200"
          }`}
        >
          {isUser ? content : <Markdown text={content} />}
          {animating && (
            <span className="ml-0.5 inline-block h-3.5 w-1.5 animate-pulse rounded-sm bg-violet-400 align-middle" />
          )}
        </div>
        {!animating && turn.role === "assistant" && turn.usedLlm === false && (
          <p className="mt-1 text-[10px] text-slate-500">Extractive answer (no LLM key configured)</p>
        )}
        {!animating && turn.sources && turn.sources.length > 0 && <Sources sources={turn.sources} />}
      </div>
    </div>
  );
}

function Sources({ sources }: { sources: SearchResult[] }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="mt-2">
      <button
        onClick={() => setOpen((o) => !o)}
        className="inline-flex items-center gap-1 text-[11px] font-medium text-violet-400 hover:text-violet-300"
      >
        <ChevronDown className={`h-3 w-3 transition ${open ? "rotate-180" : ""}`} />
        {sources.length} source{sources.length > 1 ? "s" : ""} from your notes
      </button>
      {open && (
        <div className="mt-2 space-y-2">
          {sources.map((s) => (
            <div key={s.chunk_id} className="rounded-lg border border-white/5 bg-black/20 p-2.5 text-left">
              <div className="mb-1 flex items-center justify-between text-[10px] text-slate-500">
                <span className="truncate">
                  {s.filename}
                  {s.page ? ` · p.${s.page}` : ""}
                </span>
                <span className="text-violet-400">{Math.round(s.similarity * 100)}% match</span>
              </div>
              <p className="line-clamp-3 text-[11px] text-slate-400">{s.text}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function errorMessage(e: unknown): string {
  if (e && typeof e === "object" && "message" in e) {
    return String((e as { message: unknown }).message);
  }
  return "Request failed.";
}
