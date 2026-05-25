import Link from "next/link";

export function Footer() {
  return (
    <footer className="border-t border-violet-500/10 bg-[#030712]">
      <div className="mx-auto max-w-7xl px-6 py-12">
        <div className="flex flex-col items-center justify-between gap-6 md:flex-row">
          <div className="text-center md:text-left">
            <p className="font-bold text-white">
              MentorMind <span className="gradient-text">AI</span>
            </p>
            <p className="mt-1 text-sm text-slate-500">
              Learn smarter. Interview stronger.
            </p>
          </div>
          <div className="flex flex-wrap justify-center gap-6 text-sm text-slate-500">
            <Link href="/dashboard" className="hover:text-violet-300 transition">
              Dashboard
            </Link>
            <Link href="/interview" className="hover:text-violet-300 transition">
              Mock Interview
            </Link>
            <a
              href="https://github.com/Tharmithan/mentor-mind-ai"
              className="hover:text-violet-300 transition"
              target="_blank"
              rel="noopener noreferrer"
            >
              GitHub
            </a>
          </div>
        </div>
        <p className="mt-8 text-center text-xs text-slate-600">
          © {new Date().getFullYear()} MentorMind AI · Week 1 Day 2 — UI/UX Design
        </p>
      </div>
    </footer>
  );
}
