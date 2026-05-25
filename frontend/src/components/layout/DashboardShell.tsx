import { Sidebar } from "@/components/layout/Sidebar";
import Link from "next/link";

export function DashboardShell({
  children,
  title,
  subtitle,
}: {
  children: React.ReactNode;
  title: string;
  subtitle?: string;
}) {
  return (
    <div className="flex min-h-screen bg-[#030712] bg-mesh">
      <Sidebar />
      <div className="flex flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-violet-500/10 px-6 py-4 md:hidden">
          <span className="font-bold text-white">MentorMind AI</span>
          <Link
            href="/"
            className="text-sm text-violet-400 hover:text-violet-300"
          >
            Home
          </Link>
        </header>
        <main className="flex-1 p-6 md:p-8">
          <div className="mb-8">
            <h1 className="text-2xl font-bold text-white md:text-3xl">{title}</h1>
            {subtitle && (
              <p className="mt-1 text-slate-400">{subtitle}</p>
            )}
          </div>
          {children}
        </main>
      </div>
    </div>
  );
}
