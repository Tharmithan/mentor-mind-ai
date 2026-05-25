import Link from "next/link";
import { Button } from "@/components/ui/Button";

export function Navbar() {
  return (
    <header className="sticky top-0 z-50 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md">
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <Link href="/" className="flex items-center gap-2">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-500 text-sm font-bold text-white">
            M
          </span>
          <span className="text-lg font-semibold text-white">
            MentorMind <span className="text-indigo-400">AI</span>
          </span>
        </Link>

        <div className="hidden items-center gap-8 text-sm text-slate-400 md:flex">
          <a href="#features" className="hover:text-white transition-colors">
            Features
          </a>
          <a href="#how-it-works" className="hover:text-white transition-colors">
            How it works
          </a>
          <Link href="/dashboard" className="hover:text-white transition-colors">
            Dashboard
          </Link>
        </div>

        <div className="flex items-center gap-3">
          <Button variant="ghost" href="/dashboard">
            Sign in
          </Button>
          <Button variant="primary" href="/dashboard">
            Get Started
          </Button>
        </div>
      </nav>
    </header>
  );
}
