import Link from "next/link";

export function Footer() {
  return (
    <footer className="border-t border-slate-800 bg-slate-950">
      <div className="mx-auto max-w-7xl px-6 py-12">
        <div className="flex flex-col items-center justify-between gap-6 md:flex-row">
          <div className="text-center md:text-left">
            <p className="font-semibold text-white">MentorMind AI</p>
            <p className="mt-1 text-sm text-slate-500">
              Learn smarter. Interview stronger.
            </p>
          </div>
          <div className="flex gap-6 text-sm text-slate-500">
            <Link href="/dashboard" className="hover:text-slate-300">
              Dashboard
            </Link>
            <a
              href="https://github.com"
              className="hover:text-slate-300"
              target="_blank"
              rel="noopener noreferrer"
            >
              GitHub
            </a>
          </div>
        </div>
        <p className="mt-8 text-center text-xs text-slate-600">
          © {new Date().getFullYear()} MentorMind AI. Week 1 — Foundation build.
        </p>
      </div>
    </footer>
  );
}
