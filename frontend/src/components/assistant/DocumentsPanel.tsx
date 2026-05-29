"use client";

import { useRef } from "react";
import { Upload, FileText, Trash2, Loader2, Sparkles } from "lucide-react";
import { GlassCard } from "@/components/ui/GlassCard";
import type { DocumentMeta } from "@/lib/types/api";

type Props = {
  documents: DocumentMeta[];
  activeDoc: string | null;
  uploading: boolean;
  onSelect: (id: string | null) => void;
  onUpload: (file: File) => void;
  onDelete: (id: string) => void;
};

export function DocumentsPanel({
  documents,
  activeDoc,
  uploading,
  onSelect,
  onUpload,
  onDelete,
}: Props) {
  const fileRef = useRef<HTMLInputElement>(null);
  const hasDocs = documents.length > 0;

  return (
    <div className="space-y-4">
      <GlassCard className="p-4" hover={false}>
        <input
          ref={fileRef}
          type="file"
          accept=".pdf,.txt,.md"
          className="hidden"
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) onUpload(f);
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
              onClick={() => onSelect(null)}
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
                onClick={() => onSelect(doc.document_id)}
                className="flex min-w-0 flex-1 flex-col"
              >
                <span className="truncate font-medium">{doc.filename}</span>
                <span className="text-[10px] text-slate-500">
                  {doc.num_chunks} chunks · {doc.num_pages} pages
                </span>
              </button>
              <button
                onClick={() => onDelete(doc.document_id)}
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
  );
}
