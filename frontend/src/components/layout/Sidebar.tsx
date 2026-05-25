"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { href: "/dashboard", label: "Overview", icon: "◉" },
  { href: "/dashboard#planner", label: "Study Planner", icon: "◎", soon: true },
  { href: "/dashboard#interview", label: "Mock Interview", icon: "◈", soon: true },
  { href: "/dashboard#assistant", label: "PDF Assistant", icon: "◇", soon: true },
  { href: "/dashboard#analytics", label: "Analytics", icon: "◆", soon: true },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden w-64 shrink-0 border-r border-slate-800 bg-slate-950 md:flex md:flex-col">
      <div className="border-b border-slate-800 p-6">
        <Link href="/" className="flex items-center gap-2">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-500 text-xs font-bold text-white">
            M
          </span>
          <span className="font-semibold text-white">
            MentorMind <span className="text-indigo-400">AI</span>
          </span>
        </Link>
      </div>
      <nav className="flex-1 space-y-1 p-4">
        {navItems.map((item) => {
          const active = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition ${
                active
                  ? "bg-indigo-500/15 text-indigo-300"
                  : "text-slate-400 hover:bg-slate-900 hover:text-slate-200"
              }`}
            >
              <span className="text-indigo-400">{item.icon}</span>
              {item.label}
              {item.soon && (
                <span className="ml-auto rounded bg-slate-800 px-1.5 py-0.5 text-[10px] text-slate-500">
                  Soon
                </span>
              )}
            </Link>
          );
        })}
      </nav>
      <div className="border-t border-slate-800 p-4">
        <Link
          href="/"
          className="block rounded-lg px-3 py-2 text-sm text-slate-500 hover:text-slate-300"
        >
          ← Back to home
        </Link>
      </div>
    </aside>
  );
}
