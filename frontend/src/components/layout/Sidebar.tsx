"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Mic,
  BookOpen,
  FileText,
  FileSearch,
  BarChart3,
  ArrowLeft,
  Sparkles,
  type LucideIcon,
  Brain,
  Shield,
} from "lucide-react";
import { ThemeToggle } from "@/components/ui/ThemeToggle";

const navItems: {
  href: string;
  label: string;
  icon: LucideIcon;
  soon?: boolean;
}[] = [
  { href: "/coach", label: "AI Coach", icon: Brain },
  { href: "/dashboard", label: "Overview", icon: LayoutDashboard },
  { href: "/interview", label: "Mock Interview", icon: Mic },
  { href: "/assistant", label: "AI Study Assistant", icon: FileText },
  { href: "/resume", label: "Resume Analyzer", icon: FileSearch },
  { href: "/planner", label: "Learning Planner", icon: BookOpen },
  { href: "/dashboard#analytics", label: "Analytics", icon: BarChart3 },
  { href: "/admin", label: "Admin", icon: Shield },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden w-64 shrink-0 flex-col border-r border-violet-500/10 bg-background/95 backdrop-blur-xl md:flex">
      <div className="border-b border-violet-500/10 p-6">
        <Link href="/" className="flex items-center gap-2.5 transition hover:opacity-90">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-violet-600 to-blue-600 shadow-lg shadow-violet-500/25">
            <Sparkles className="h-4 w-4 text-white" />
          </span>
          <span className="font-bold text-white">
            MentorMind <span className="text-violet-400">AI</span>
          </span>
        </Link>
      </div>
      <nav className="flex-1 space-y-1 p-4">
        {navItems.map((item) => {
          const Icon = item.icon;
          const active =
            pathname === item.href ||
            (item.href === "/coach" && pathname.startsWith("/coach")) ||
            (item.href === "/interview" && pathname.startsWith("/interview")) ||
            (item.href === "/resume" && pathname.startsWith("/resume")) ||
            (item.href === "/planner" && pathname.startsWith("/planner")) ||
            (item.href === "/admin" && pathname.startsWith("/admin"));
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-200 ${
                active
                  ? "bg-gradient-to-r from-violet-600/20 to-blue-600/10 text-violet-200 ring-1 ring-violet-500/20 shadow-sm shadow-violet-500/10"
                  : "text-slate-400 hover:translate-x-0.5 hover:bg-white/5 hover:text-slate-200"
              }`}
            >
              <Icon className={`h-4 w-4 shrink-0 ${active ? "text-violet-400" : "text-slate-500"}`} />
              {item.label}
              {item.soon && (
                <span className="ml-auto rounded-md bg-slate-800 px-1.5 py-0.5 text-[10px] text-slate-500">
                  Soon
                </span>
              )}
            </Link>
          );
        })}
      </nav>
      <div className="border-t border-violet-500/10 p-4">
        <div className="glass rounded-xl p-4">
          <p className="text-xs font-medium text-violet-300">Pro tip</p>
          <p className="mt-1 text-xs text-slate-400">
            Practice interviews daily to boost confidence scores.
          </p>
        </div>
        <Link
          href="/"
          className="mt-3 flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-slate-500 transition hover:text-violet-300"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to home
        </Link>
        <div className="mt-3">
          <ThemeToggle />
        </div>
      </div>
    </aside>
  );
}
