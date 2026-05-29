"use client";

import { Fragment, type ReactNode } from "react";

/**
 * Lightweight, dependency-free Markdown renderer for chat answers.
 * Supports: headings, bold/italic, inline code, fenced code blocks,
 * unordered/ordered lists, links, and paragraphs.
 */
export function Markdown({ text }: { text: string }) {
  return <div className="space-y-2">{renderBlocks(text)}</div>;
}

const FENCE_RE = /```(\w*)\n?([\s\S]*?)```/g;

function renderBlocks(text: string): ReactNode[] {
  const out: ReactNode[] = [];
  let last = 0;
  let key = 0;
  let m: RegExpExecArray | null;

  FENCE_RE.lastIndex = 0;
  while ((m = FENCE_RE.exec(text)) !== null) {
    if (m.index > last) {
      out.push(...renderTextBlocks(text.slice(last, m.index), () => key++));
    }
    out.push(<CodeBlock key={`code-${key++}`} lang={m[1]} code={m[2].replace(/\n$/, "")} />);
    last = m.index + m[0].length;
  }
  if (last < text.length) {
    out.push(...renderTextBlocks(text.slice(last), () => key++));
  }
  return out;
}

function renderTextBlocks(block: string, nextKey: () => number): ReactNode[] {
  const lines = block.split("\n");
  const out: ReactNode[] = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    if (line.trim() === "") {
      i++;
      continue;
    }

    // Headings
    const heading = /^(#{1,6})\s+(.*)$/.exec(line);
    if (heading) {
      const level = heading[1].length;
      const sizes = ["text-lg", "text-base", "text-sm", "text-sm", "text-sm", "text-sm"];
      out.push(
        <p key={`h-${nextKey()}`} className={`font-bold text-white ${sizes[level - 1]}`}>
          {parseInline(heading[2])}
        </p>
      );
      i++;
      continue;
    }

    // Unordered list
    if (/^\s*[-*]\s+/.test(line)) {
      const items: string[] = [];
      while (i < lines.length && /^\s*[-*]\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^\s*[-*]\s+/, ""));
        i++;
      }
      out.push(
        <ul key={`ul-${nextKey()}`} className="space-y-1 pl-1">
          {items.map((it, idx) => (
            <li key={idx} className="flex gap-2">
              <span className="text-violet-400">•</span>
              <span>{parseInline(it)}</span>
            </li>
          ))}
        </ul>
      );
      continue;
    }

    // Ordered list
    if (/^\s*\d+\.\s+/.test(line)) {
      const items: string[] = [];
      while (i < lines.length && /^\s*\d+\.\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^\s*\d+\.\s+/, ""));
        i++;
      }
      out.push(
        <ol key={`ol-${nextKey()}`} className="space-y-1 pl-1">
          {items.map((it, idx) => (
            <li key={idx} className="flex gap-2">
              <span className="font-semibold text-violet-400">{idx + 1}.</span>
              <span>{parseInline(it)}</span>
            </li>
          ))}
        </ol>
      );
      continue;
    }

    // Paragraph (merge consecutive non-empty, non-special lines)
    const para: string[] = [];
    while (
      i < lines.length &&
      lines[i].trim() !== "" &&
      !/^(#{1,6})\s+/.test(lines[i]) &&
      !/^\s*[-*]\s+/.test(lines[i]) &&
      !/^\s*\d+\.\s+/.test(lines[i])
    ) {
      para.push(lines[i]);
      i++;
    }
    out.push(
      <p key={`p-${nextKey()}`} className="leading-relaxed">
        {parseInline(para.join(" "))}
      </p>
    );
  }

  return out;
}

const INLINE_RE = /(`[^`]+`)|(\*\*[^*]+\*\*)|(\*[^*]+\*)|(\[[^\]]+\]\([^)]+\))/g;

function parseInline(text: string): ReactNode[] {
  const out: ReactNode[] = [];
  let last = 0;
  let key = 0;
  let m: RegExpExecArray | null;

  INLINE_RE.lastIndex = 0;
  while ((m = INLINE_RE.exec(text)) !== null) {
    if (m.index > last) out.push(<Fragment key={key++}>{text.slice(last, m.index)}</Fragment>);
    const tok = m[0];
    if (tok.startsWith("`")) {
      out.push(
        <code
          key={key++}
          className="rounded bg-black/40 px-1.5 py-0.5 font-mono text-[0.85em] text-emerald-300"
        >
          {tok.slice(1, -1)}
        </code>
      );
    } else if (tok.startsWith("**")) {
      out.push(
        <strong key={key++} className="font-semibold text-white">
          {tok.slice(2, -2)}
        </strong>
      );
    } else if (tok.startsWith("*")) {
      out.push(
        <em key={key++} className="italic">
          {tok.slice(1, -1)}
        </em>
      );
    } else {
      const link = /\[([^\]]+)\]\(([^)]+)\)/.exec(tok);
      if (link) {
        out.push(
          <a
            key={key++}
            href={link[2]}
            target="_blank"
            rel="noreferrer"
            className="text-violet-400 underline hover:text-violet-300"
          >
            {link[1]}
          </a>
        );
      }
    }
    last = m.index + tok.length;
  }
  if (last < text.length) out.push(<Fragment key={key++}>{text.slice(last)}</Fragment>);
  return out;
}

function CodeBlock({ lang, code }: { lang: string; code: string }) {
  return (
    <div className="overflow-hidden rounded-lg border border-white/10 bg-black/50">
      {lang && (
        <div className="border-b border-white/5 px-3 py-1 text-[10px] uppercase tracking-wide text-slate-500">
          {lang}
        </div>
      )}
      <pre className="overflow-x-auto p-3 text-[12px] leading-relaxed">
        <code className="font-mono text-slate-200">{code}</code>
      </pre>
    </div>
  );
}
