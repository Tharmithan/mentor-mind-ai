import Link from "next/link";
import { Button } from "@/components/ui/Button";

export function Navbar() {
  return (
    <header className="sticky top-0 z-50 border-b border-violet-500/10 bg-[#030712]/80 backdrop-blur-xl">
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <Link href="/" className="flex items-center gap-2.5">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-violet-600 to-blue-600 text-sm font-bold text-white shadow-lg shadow-violet-500/30">
            M
          </span>
          <span className="text-lg font-bold text-white">
            MentorMind <span className="gradient-text">AI</span>
          </span>
        </Link>

        <div className="hidden items-center gap-8 text-sm text-slate-400 md:flex">
          <a href="#features" className="transition hover:text-violet-300">
            Features
          </a>
          <a href="#ai-capabilities" className="transition hover:text-violet-300">
            AI Power
          </a>
          <a href="#testimonials" className="transition hover:text-violet-300">
            Reviews
          </a>
          <Link href="/dashboard" className="transition hover:text-violet-300">
            Dashboard
          </Link>
        </div>

        <div className="flex items-center gap-3">
          <Button variant="ghost" href="/dashboard" className="hidden sm:inline-flex">
            Sign in
          </Button>
          <Button variant="gradient" href="/dashboard">
            Get Started
          </Button>
        </div>
      </nav>
    </header>
  );
}
