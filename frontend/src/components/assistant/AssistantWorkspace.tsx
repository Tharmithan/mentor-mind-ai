"use client";

import dynamic from "next/dynamic";
import { useEffect, useState } from "react";
import { MessageSquare, Wand2 } from "lucide-react";
import { deleteDocument, listDocuments, uploadDocument } from "@/lib/api";
import type { DocumentMeta } from "@/lib/types/api";
import { cachedFetch, invalidateCached } from "@/lib/queryCache";
import { DocumentsPanel } from "@/components/assistant/DocumentsPanel";
import { ChartSkeleton } from "@/components/charts/ChartSkeleton";

const ChatPanel = dynamic(() => import("./ChatPanel").then((m) => m.ChatPanel), {
  ssr: false,
  loading: () => <ChartSkeleton className="h-96" />,
});
const StudyToolsPanel = dynamic(() => import("./StudyToolsPanel").then((m) => m.StudyToolsPanel), {
  ssr: false,
  loading: () => <ChartSkeleton className="h-96" />,
});

type Tab = "chat" | "tools";

export function AssistantWorkspace() {
  const [documents, setDocuments] = useState<DocumentMeta[]>([]);
  const [activeDoc, setActiveDoc] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [tab, setTab] = useState<Tab>("chat");
  const [uploadError, setUploadError] = useState<string | null>(null);

  useEffect(() => {
    refresh();
  }, []);

  async function refresh() {
    try {
      const data = await cachedFetch("documents-list", listDocuments, 30_000);
      setDocuments(data.documents);
    } catch {
      /* backend offline — keep UI usable */
    }
  }

  async function handleUpload(file: File) {
    setUploading(true);
    setUploadError(null);
    try {
      const res = await uploadDocument(file);
      invalidateCached("documents-list");
      await refresh();
      setActiveDoc(res.document.document_id);
    } catch (e) {
      setUploadError(
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
      invalidateCached("documents-list");
      if (activeDoc === id) setActiveDoc(null);
      await refresh();
    } catch {
      /* ignore */
    }
  }

  const hasDocs = documents.length > 0;

  return (
    <div className="grid gap-5 lg:grid-cols-[300px_1fr]">
      <div className="space-y-3">
        <DocumentsPanel
          documents={documents}
          activeDoc={activeDoc}
          uploading={uploading}
          onSelect={setActiveDoc}
          onUpload={handleUpload}
          onDelete={handleDelete}
        />
        {uploadError && <p className="text-xs text-red-400">{uploadError}</p>}
      </div>

      <div>
        <div className="mb-4 inline-flex rounded-xl border border-white/10 bg-white/5 p-1">
          <TabButton active={tab === "chat"} onClick={() => setTab("chat")} icon={MessageSquare}>
            Chat
          </TabButton>
          <TabButton active={tab === "tools"} onClick={() => setTab("tools")} icon={Wand2}>
            Study Tools
          </TabButton>
        </div>

        {tab === "chat" ? (
          <ChatPanel activeDoc={activeDoc} hasDocs={hasDocs} />
        ) : (
          <StudyToolsPanel activeDoc={activeDoc} hasDocs={hasDocs} />
        )}
      </div>
    </div>
  );
}

function TabButton({
  active,
  onClick,
  icon: Icon,
  children,
}: {
  active: boolean;
  onClick: () => void;
  icon: typeof MessageSquare;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className={`inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold transition ${
        active
          ? "bg-gradient-to-r from-violet-600 to-blue-600 text-white shadow-lg shadow-violet-500/25"
          : "text-slate-400 hover:text-slate-200"
      }`}
    >
      <Icon className="h-4 w-4" />
      {children}
    </button>
  );
}
