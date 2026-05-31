"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import {
  Brain,
  Home,
  LayoutDashboard,
  Mic,
  MoreHorizontal,
  FileText,
  BookOpen,
  FileSearch,
  Shield,
  X,
} from "lucide-react";

const primaryItems = [
  { href: "/", label: "Home", icon: Home },
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/coach", label: "Coach", icon: Brain },
  { href: "/interview", label: "Interview", icon: Mic },
];

const moreItems = [
  { href: "/assistant", label: "AI Tutor", icon: FileText },
  { href: "/resume", label: "Resume", icon: FileSearch },
  { href: "/planner", label: "Planner", icon: BookOpen },
  { href: "/admin", label: "Admin", icon: Shield },
];

export function MobileNav() {
  const pathname = usePathname();
  const [moreOpen, setMoreOpen] = useState(false);

  const isActive = (href: string) =>
    pathname === href || (href !== "/" && pathname.startsWith(href));

  const moreActive = moreItems.some((i) => isActive(i.href));

  return (
    <>
      {moreOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/40 md:hidden"
          onClick={() => setMoreOpen(false)}
          aria-hidden
        />
      )}
      {moreOpen && (
        <div className="fixed bottom-[4.25rem] left-4 right-4 z-50 rounded-2xl border border-violet-500/20 bg-background/95 p-3 shadow-xl backdrop-blur-xl md:hidden safe-area-pb">
          <div className="mb-2 flex items-center justify-between px-1">
            <span className="text-xs font-semibold uppercase tracking-wider text-violet-400">
              More
            </span>
            <button type="button" onClick={() => setMoreOpen(false)} aria-label="Close">
              <X className="h-4 w-4 text-slate-400" />
            </button>
          </div>
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
            {moreItems.map(({ href, label, icon: Icon }) => (
              <Link
                key={href}
                href={href}
                onClick={() => setMoreOpen(false)}
                className={`flex flex-col items-center gap-1 rounded-xl px-2 py-3 text-center transition ${
                  isActive(href)
                    ? "bg-violet-600/20 text-violet-300"
                    : "text-slate-400 hover:bg-white/5"
                }`}
              >
                <Icon className="h-5 w-5" />
                <span className="text-[10px] font-medium">{label}</span>
              </Link>
            ))}
          </div>
        </div>
      )}

      <nav className="fixed bottom-0 left-0 right-0 z-50 border-t border-violet-500/10 bg-background/90 backdrop-blur-xl md:hidden">
        <div className="mx-auto flex max-w-lg items-center justify-around px-1 py-2 safe-area-pb">
          {primaryItems.map(({ href, label, icon: Icon }) => {
            const active = isActive(href);
            return (
              <Link
                key={href}
                href={href}
                className={`flex min-w-[4rem] flex-col items-center gap-0.5 rounded-xl px-2 py-2 transition-all duration-200 ${
                  active ? "text-violet-400 scale-105" : "text-slate-500 hover:text-slate-300"
                }`}
              >
                <Icon
                  className={`h-5 w-5 ${active ? "drop-shadow-[0_0_8px_rgba(139,92,246,0.6)]" : ""}`}
                />
                <span className="text-[10px] font-medium">{label}</span>
              </Link>
            );
          })}
          <button
            type="button"
            onClick={() => setMoreOpen((v) => !v)}
            className={`flex min-w-[4rem] flex-col items-center gap-0.5 rounded-xl px-2 py-2 transition ${
              moreActive || moreOpen ? "text-violet-400" : "text-slate-500 hover:text-slate-300"
            }`}
          >
            <MoreHorizontal className="h-5 w-5" />
            <span className="text-[10px] font-medium">More</span>
          </button>
        </div>
      </nav>
    </>
  );
}
