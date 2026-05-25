"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { href: "/dashboard", label: "Overview", icon: "◉" },
  { href: "/interview", label: "Mock Interview", icon: "◈" },
  { href: "/dashboard#planner", label: "Study Planner", icon: "◎", soon: true },
  { href: "/dashboard#assistant", label: "PDF Assistant", icon: "◇", soon: true },
  { href: "/dashboard#analytics", label: "Analytics", icon: "◆", soon: true },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden w-64 shrink-0 flex-col border-r border-violet-500/10 bg-[#030712] md:flex">
      <div className="border-b border-violet-500/10 p-6">
        <Link href="/" className="flex items-center gap-2.5">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-violet-600 to-blue-600 text-xs font-bold text-white">
            M
          </span>
          <span className="font-bold text-white">
            MentorMind <span className="text-violet-400">AI</span>
          </span>
        </Link>
      </div>
      <nav className="flex-1 space-y-1 p-4">
        {navItems.map((item) => {
          const active =
            pathname === item.href ||
            (item.href === "/interview" && pathname.startsWith("/interview"));
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition ${
                active
                  ? "bg-gradient-to-r from-violet-600/20 to-blue-600/10 text-violet-200 ring-1 ring-violet-500/20"
                  : "text-slate-400 hover:bg-white/5 hover:text-slate-200"
              }`}
            >
              <span className={active ? "text-violet-400" : "text-slate-500"}>
                {item.icon}
              </span>
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
        <div className="rounded-xl bg-gradient-to-br from-violet-600/10 to-blue-600/10 p-4 ring-1 ring-violet-500/20">
          <p className="text-xs font-medium text-violet-300">Pro tip</p>
          <p className="mt-1 text-xs text-slate-400">
            Practice interviews daily to boost confidence scores.
          </p>
        </div>
        <Link
          href="/"
          className="mt-3 block rounded-lg px-3 py-2 text-sm text-slate-500 hover:text-slate-300"
        >
          ← Back to home
        </Link>
      </div>
    </aside>
  );
}
