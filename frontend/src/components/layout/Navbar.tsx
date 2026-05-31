"use client";

import Link from "next/link";
import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { ThemeToggle } from "@/components/ui/ThemeToggle";
import { Menu, Sparkles, X } from "lucide-react";

const links = [
  { href: "#features", label: "Features" },
  { href: "#ai-capabilities", label: "AI Power" },
  { href: "#testimonials", label: "Reviews" },
];

export function Navbar() {
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 border-b border-violet-500/10 bg-background/80 backdrop-blur-xl">
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6">
        <Link href="/" className="flex items-center gap-2.5 transition hover:opacity-90">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-violet-600 to-blue-600 shadow-lg shadow-violet-500/30">
            <Sparkles className="h-5 w-5 text-white" />
          </span>
          <span className="text-lg font-bold text-white">
            MentorMind <span className="gradient-text">AI</span>
          </span>
        </Link>

        <div className="hidden items-center gap-8 text-sm text-slate-400 lg:flex">
          {links.map((l) => (
            <a key={l.href} href={l.href} className="transition hover:text-violet-300">
              {l.label}
            </a>
          ))}
          <Link href="/dashboard" className="transition hover:text-violet-300">
            Dashboard
          </Link>
        </div>

        <div className="flex items-center gap-2 sm:gap-3">
          <ThemeToggle compact />
          <button
            type="button"
            onClick={() => setOpen(!open)}
            className="flex h-10 w-10 items-center justify-center rounded-xl border border-violet-500/20 bg-violet-950/30 text-slate-300 lg:hidden"
            aria-label="Toggle menu"
          >
            {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
          <Button variant="ghost" href="/dashboard" className="hidden sm:inline-flex">
            Sign in
          </Button>
          <Button variant="gradient" href="/dashboard">
            Get Started
          </Button>
        </div>
      </nav>
      {open && (
        <div className="border-t border-violet-500/10 px-4 py-3 lg:hidden animate-fade-in">
          <div className="flex flex-col gap-1">
            {links.map((l) => (
              <a
                key={l.href}
                href={l.href}
                onClick={() => setOpen(false)}
                className="rounded-lg px-3 py-2 text-sm text-slate-300 hover:bg-white/5"
              >
                {l.label}
              </a>
            ))}
            <Link
              href="/dashboard"
              onClick={() => setOpen(false)}
              className="rounded-lg px-3 py-2 text-sm text-slate-300 hover:bg-white/5"
            >
              Dashboard
            </Link>
          </div>
        </div>
      )}
    </header>
  );
}
