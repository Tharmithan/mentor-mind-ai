"use client";

import { useEffect, useRef, useState } from "react";
import {
  Bot,
  User,
  Send,
  Upload,
  FileText,
  Trash2,
  Loader2,
  Sparkles,
  BookOpen,
  ListChecks,
  Lightbulb,
  ChevronDown,
} from "lucide-react";
import { GlassCard } from "@/components/ui/GlassCard";
import {
  chatWithDocuments,
  deleteDocument,
  listDocuments,
  uploadDocument,
} from "@/lib/api";
import type {
  ChatMessage,
  DocumentMeta,
  SearchResult,
} from "@/lib/types/api";

type ChatTurn = ChatMessage & {
  sources?: SearchResult[];
  usedLlm?: boolean;
};

type Mode = "explain" | "summarize" | "example";

const MODES: { id: Mode; label: string; icon: typeof BookOpen }[] = [
  { id: "explain", label: "Explain", icon: BookOpen },
  { id: "summarize", label: "Summarize", icon: ListChecks },
  { id: "example", label: "Examples", icon: Lightbulb },
];

const WELCOME: ChatTurn = {
  role: "assistant",
  content:
    "Hi! I'm your AI study tutor. Upload your lecture notes or a PDF, then ask me anything — I'll answer from your material, explain concepts, summarize topics, and give examples.",
};

export function ChatAssistant() {
  const [documents, setDocuments] = useState<DocumentMeta[]>([]);
  const [activeDoc, setActiveDoc] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatTurn[]>([WELCOME]);
  const [input, setInput] = useState("");
  const [uploading, setUploading] = useState(false);
  const [thinking, setThinking] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fileRef = useRef<HTMLInputElement>(null);
  const threadRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    refreshDocuments();
  }, []);

  useEffect(() => {
    threadRef.current?.scrollTo({ top: threadRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, thinking]);

  async function refreshDocuments() {
    try {
      const data = await listDocuments();
      setDocuments(data.documents);
    } catch {
      /* backend offline — keep UI usable */
    }
  }

  async function handleUpload(file: File) {
    setUploading(true);
    setError(null);
    try {
      const res = await uploadDocument(file);
      await refreshDocuments();
      setActiveDoc(res.document.document_id);
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content: `Got it — I processed **${res.document.filename}** into ${res.document.num_chunks} searchable chunks${
            res.document.indexed ? " and indexed them for semantic search" : ""
          }. Ask me anything about it!`,
        },
      ]);
    } catch (e) {
      setError(
        e && typeof e === "object" && "message" in e
          ? String((e as { message: unknown }).message)
          : "Upload failed."
      );
    } finally {
      setUploading(false);
    }
  }

  async function handleDelete(id: string) {
    try {
      await deleteDocument(id);
      if (activeDoc === id) setActiveDoc(null);
      await refreshDocuments();
    } catch {
      /* ignore */
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
        history,
      });
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content: res.answer,
          sources: res.sources,
          usedLlm: res.used_llm,
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
      setError(
        e && typeof e === "object" && "message" in e
          ? String((e as { message: unknown }).message)
          : "Request failed."
      );
    } finally {
      setThinking(false);
    }
  }

  const hasDocs = documents.length > 0;

  return (
    <div className="grid gap-5 lg:grid-cols-[300px_1fr]">
      {/* Sidebar: documents */}
      <div className="space-y-4">
        <GlassCard className="p-4" hover={false}>
          <input
            ref={fileRef}
            type="file"
            accept=".pdf,.txt,.md"
            className="hidden"
            onChange={(e) => {
              const f = e.target.files?.[0];
              if (f) handleUpload(f);
              e.target.value = "";
            }}
          />
          <button
            onClick={() => fileRef.current?.click()}
            disabled={uploading}
            className="flex w-full flex-col items-center gap-2 rounded-xl border border-dashed border-violet-500/30 bg-violet-950/20 px-4 py-6 text-center transition hover:border-violet-500/50 hover:bg-violet-900/20 disabled:opacity-60"
          >
            {uploading ? (
              <Loader2 className="h-6 w-6 animate-spin text-violet-400" />
            ) : (
              <Upload className="h-6 w-6 text-violet-400" />
            )}
            <span className="text-sm font-semibold text-slate-100">
              {uploading ? "Processing…" : "Upload notes"}
            </span>
            <span className="text-xs text-slate-500">PDF, TXT or MD · max 25 MB</span>
          </button>
        </GlassCard>

        <GlassCard className="p-4" hover={false}>
          <p className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
            <FileText className="h-3.5 w-3.5" /> Your documents
          </p>
          {!hasDocs && (
            <p className="text-xs text-slate-500">No documents yet. Upload notes to begin.</p>
          )}
          <div className="space-y-2">
            {hasDocs && (
              <button
                onClick={() => setActiveDoc(null)}
                className={`flex w-full items-center justify-between rounded-lg px-3 py-2 text-left text-xs transition ${
                  activeDoc === null
                    ? "bg-violet-600/20 text-violet-200 ring-1 ring-violet-500/30"
                    : "text-slate-400 hover:bg-white/5"
                }`}
              >
                <span className="flex items-center gap-2">
                  <Sparkles className="h-3.5 w-3.5" /> All documents
                </span>
              </button>
            )}
            {documents.map((doc) => (
              <div
                key={doc.document_id}
                className={`group flex items-center justify-between gap-2 rounded-lg px-3 py-2 text-left text-xs transition ${
                  activeDoc === doc.document_id
                    ? "bg-violet-600/20 text-violet-200 ring-1 ring-violet-500/30"
                    : "text-slate-300 hover:bg-white/5"
                }`}
              >
                <button
                  onClick={() => setActiveDoc(doc.document_id)}
                  className="flex min-w-0 flex-1 flex-col"
                >
                  <span className="truncate font-medium">{doc.filename}</span>
                  <span className="text-[10px] text-slate-500">
                    {doc.num_chunks} chunks · {doc.num_pages} pages
                  </span>
                </button>
                <button
                  onClick={() => handleDelete(doc.document_id)}
                  className="opacity-0 transition group-hover:opacity-100 hover:text-red-400"
                  aria-label="Delete document"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>
            ))}
          </div>
        </GlassCard>
      </div>

      {/* Chat panel */}
      <GlassCard className="flex h-[calc(100vh-13rem)] min-h-[520px] flex-col" hover={false}>
        <div
          ref={threadRef}
          className="flex-1 space-y-4 overflow-y-auto p-5"
        >
          {messages.map((m, i) => (
            <MessageBubble key={i} turn={m} />
          ))}
          {thinking && (
            <div className="flex items-start gap-3">
              <Avatar role="assistant" />
              <div className="flex items-center gap-2 rounded-2xl rounded-tl-sm bg-white/5 px-4 py-3 text-sm text-slate-400">
                <Loader2 className="h-4 w-4 animate-spin text-violet-400" />
                Searching your notes…
              </div>
            </div>
          )}
        </div>

        {/* Quick modes */}
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

        {/* Composer */}
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
            placeholder={hasDocs ? "Ask about your notes… e.g. \u201cExplain recursion\u201d" : "Upload notes, then ask a question…"}
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
    </div>
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

function MessageBubble({ turn }: { turn: ChatTurn }) {
  const isUser = turn.role === "user";
  return (
    <div className={`flex items-start gap-3 ${isUser ? "flex-row-reverse" : ""}`}>
      <Avatar role={turn.role} />
      <div className={`max-w-[80%] ${isUser ? "items-end text-right" : ""}`}>
        <div
          className={`whitespace-pre-wrap rounded-2xl px-4 py-3 text-sm leading-relaxed ${
            isUser
              ? "rounded-tr-sm bg-violet-600 text-white"
              : "rounded-tl-sm bg-white/5 text-slate-200"
          }`}
        >
          {turn.content}
        </div>
        {turn.role === "assistant" && turn.usedLlm === false && (
          <p className="mt-1 text-[10px] text-slate-500">
            Extractive answer (no LLM key configured)
          </p>
        )}
        {turn.sources && turn.sources.length > 0 && <Sources sources={turn.sources} />}
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
            <div
              key={s.chunk_id}
              className="rounded-lg border border-white/5 bg-black/20 p-2.5 text-left"
            >
              <div className="mb-1 flex items-center justify-between text-[10px] text-slate-500">
                <span className="truncate">
                  {s.filename}
                  {s.page ? ` · p.${s.page}` : ""}
                </span>
                <span className="text-violet-400">
                  {Math.round(s.similarity * 100)}% match
                </span>
              </div>
              <p className="line-clamp-3 text-[11px] text-slate-400">{s.text}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
