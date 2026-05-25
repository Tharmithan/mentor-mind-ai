"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Home,
  LayoutDashboard,
  Mic,
  Sparkles,
} from "lucide-react";

const items = [
  { href: "/", label: "Home", icon: Home },
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/interview", label: "Interview", icon: Mic },
];

export function MobileNav() {
  const pathname = usePathname();

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 border-t border-violet-500/10 bg-[#030712]/90 backdrop-blur-xl md:hidden">
      <div className="mx-auto flex max-w-lg items-center justify-around px-2 py-2 safe-area-pb">
        {items.map(({ href, label, icon: Icon }) => {
          const active =
            pathname === href ||
            (href !== "/" && pathname.startsWith(href));
          return (
            <Link
              key={href}
              href={href}
              className={`flex flex-col items-center gap-0.5 rounded-xl px-4 py-2 transition-all duration-200 ${
                active
                  ? "text-violet-400 scale-105"
                  : "text-slate-500 hover:text-slate-300"
              }`}
            >
              <Icon className={`h-5 w-5 ${active ? "drop-shadow-[0_0_8px_rgba(139,92,246,0.6)]" : ""}`} />
              <span className="text-[10px] font-medium">{label}</span>
            </Link>
          );
        })}
        <Link
          href="/dashboard"
          className="flex flex-col items-center gap-0.5 rounded-xl px-3 py-2 text-slate-500"
          aria-label="AI features"
        >
          <Sparkles className="h-5 w-5" />
          <span className="text-[10px] font-medium">AI</span>
        </Link>
      </div>
    </nav>
  );
}
