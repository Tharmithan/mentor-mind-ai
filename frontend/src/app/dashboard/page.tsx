import { Sidebar } from "@/components/layout/Sidebar";
import { Button } from "@/components/ui/Button";
import { StatCard } from "@/components/ui/Card";

export default function DashboardPage() {
  return (
    <div className="flex min-h-screen bg-slate-950">
      <Sidebar />

      <div className="flex flex-1 flex-col">
        {/* Mobile header */}
        <header className="flex items-center justify-between border-b border-slate-800 px-6 py-4 md:hidden">
          <span className="font-semibold text-white">MentorMind AI</span>
          <Button variant="ghost" href="/">
            Home
          </Button>
        </header>

        <main className="flex-1 p-6 md:p-8">
          <div className="mb-8">
            <h1 className="text-2xl font-bold text-white md:text-3xl">
              Welcome back, Student
            </h1>
            <p className="mt-1 text-slate-400">
              Your AI learning command center — Week 1 preview
            </p>
          </div>

          {/* Stats */}
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard label="Study Streak" value="7 days" sub="+2 from last week" />
            <StatCard label="Total XP" value="1,240" sub="Level 5 learner" />
            <StatCard label="Performance Score" value="82%" sub="On track" />
            <StatCard label="Interview Avg" value="4.2 / 5" sub="Last 3 sessions" />
          </div>

          {/* Quick actions */}
          <div className="mt-8 rounded-xl border border-slate-800 bg-slate-900/50 p-6">
            <h2 className="text-lg font-semibold text-white">Quick Actions</h2>
            <p className="mt-1 text-sm text-slate-400">
              Core modules launch in Phases 2–8. Explore the shell UI now.
            </p>
            <div className="mt-4 flex flex-wrap gap-3">
              <Button variant="primary" href="/dashboard#interview">
                Start Mock Interview
              </Button>
              <Button variant="secondary" href="/dashboard#planner">
                Open Study Planner
              </Button>
              <Button variant="secondary" href="/dashboard#assistant">
                PDF Assistant
              </Button>
            </div>
          </div>

          {/* Activity placeholder */}
          <div className="mt-8 grid gap-6 lg:grid-cols-2">
            <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
              <h2 className="text-lg font-semibold text-white">
                Weekly Activity
              </h2>
              <div className="mt-6 flex h-40 items-end justify-between gap-2">
                {[40, 65, 45, 80, 55, 90, 70].map((h, i) => (
                  <div
                    key={i}
                    className="flex-1 rounded-t bg-indigo-500/60"
                    style={{ height: `${h}%` }}
                  />
                ))}
              </div>
              <p className="mt-4 text-xs text-slate-500">
                Placeholder chart — real analytics in Phase 9
              </p>
            </div>

            <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
              <h2 className="text-lg font-semibold text-white">AI Insights</h2>
              <ul className="mt-4 space-y-3 text-sm text-slate-300">
                <li className="flex gap-2">
                  <span className="text-emerald-400">●</span>
                  Strong in Mathematics — keep momentum
                </li>
                <li className="flex gap-2">
                  <span className="text-amber-400">●</span>
                  Review Data Structures — weak topic detected
                </li>
                <li className="flex gap-2">
                  <span className="text-indigo-400">●</span>
                  Schedule a mock interview this week
                </li>
              </ul>
            </div>
          </div>

          {/* Upcoming modules */}
          <div className="mt-8 rounded-xl border border-dashed border-slate-700 p-6 text-center">
            <p className="text-sm text-slate-500">
              Authentication (Phase 2) · ML Models (Phase 4) · RAG (Phase 8)
            </p>
          </div>
        </main>
      </div>
    </div>
  );
}
