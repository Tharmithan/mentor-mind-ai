import { DashboardShell } from "@/components/layout/DashboardShell";
import { Button } from "@/components/ui/Button";
import { StatCard } from "@/components/ui/Card";
import { ProgressRing } from "@/components/ui/ProgressRing";

const weekData = [
  { day: "Mon", hours: 2.5, height: 45 },
  { day: "Tue", hours: 4, height: 72 },
  { day: "Wed", hours: 3, height: 54 },
  { day: "Thu", hours: 5, height: 90 },
  { day: "Fri", hours: 3.5, height: 63 },
  { day: "Sat", hours: 6, height: 100 },
  { day: "Sun", hours: 4.5, height: 75 },
];

const recommendations = [
  {
    priority: "high",
    title: "Review Data Structures — Trees & Graphs",
    reason: "Weak topic detected from last quiz (62%)",
    action: "Start revision",
  },
  {
    priority: "medium",
    title: "Schedule mock technical interview",
    reason: "Last interview score: 3.8/5 — room to improve",
    action: "Practice now",
  },
  {
    priority: "low",
    title: "Maintain Mathematics momentum",
    reason: "Strong performance — 91% last assessment",
    action: "View progress",
  },
];

export default function DashboardPage() {
  return (
    <DashboardShell
      title="Welcome back, Student"
      subtitle="Your AI learning command center — real-time insights at a glance"
    >
      {/* Top stats */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Performance Score"
          value="82%"
          sub="+5% from last week"
          trend="up"
          icon={
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
          }
        />
        <StatCard
          label="Interview Score"
          value="4.2 / 5"
          sub="Last 3 sessions avg"
          trend="up"
          icon={
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
          }
        />
        <StatCard
          label="Study Streak"
          value="7 days"
          sub="Personal best!"
          trend="up"
          icon={<span className="text-lg">🔥</span>}
        />
        <StatCard
          label="Weekly Study Hours"
          value="28.5h"
          sub="+12% vs last week"
          trend="up"
          icon={
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
        />
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-3">
        {/* Performance ring */}
        <div className="glass rounded-2xl p-6 flex flex-col items-center justify-center lg:col-span-1">
          <h2 className="mb-6 w-full text-left text-lg font-semibold text-white">
            Overall Performance
          </h2>
          <ProgressRing value={82} label="Score" sublabel="On track for goals" />
          <div className="mt-6 w-full space-y-2 text-sm">
            <div className="flex justify-between text-slate-400">
              <span>Mathematics</span>
              <span className="text-emerald-400 font-medium">91%</span>
            </div>
            <div className="flex justify-between text-slate-400">
              <span>Programming</span>
              <span className="text-violet-400 font-medium">78%</span>
            </div>
            <div className="flex justify-between text-slate-400">
              <span>Data Structures</span>
              <span className="text-amber-400 font-medium">62%</span>
            </div>
          </div>
        </div>

        {/* Study analytics */}
        <div className="glass rounded-2xl p-6 lg:col-span-2">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">Study Analytics</h2>
            <span className="text-xs text-slate-500">This week</span>
          </div>
          <div className="mt-6 flex h-48 items-end justify-between gap-2 sm:gap-4">
            {weekData.map((d) => (
              <div key={d.day} className="flex flex-1 flex-col items-center gap-2">
                <span className="text-[10px] text-slate-500">{d.hours}h</span>
                <div
                  className="w-full max-w-[48px] rounded-t-lg bg-gradient-to-t from-violet-600 to-blue-500 opacity-90 transition hover:opacity-100"
                  style={{ height: `${d.height}%` }}
                />
                <span className="text-xs text-slate-400">{d.day}</span>
              </div>
            ))}
          </div>
          <div className="mt-6 grid grid-cols-3 gap-4 border-t border-violet-500/10 pt-6">
            <div>
              <p className="text-xs text-slate-500">Focus score</p>
              <p className="text-xl font-bold text-white">87%</p>
            </div>
            <div>
              <p className="text-xs text-slate-500">Quizzes done</p>
              <p className="text-xl font-bold text-white">12</p>
            </div>
            <div>
              <p className="text-xs text-slate-500">Topics mastered</p>
              <p className="text-xl font-bold text-white">8</p>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        {/* AI Recommendations */}
        <div className="glass rounded-2xl p-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">AI Recommendations</h2>
            <span className="rounded-full bg-violet-500/20 px-2.5 py-0.5 text-xs text-violet-300">
              3 new
            </span>
          </div>
          <ul className="mt-5 space-y-4">
            {recommendations.map((rec) => (
              <li
                key={rec.title}
                className="rounded-xl border border-violet-500/10 bg-slate-900/40 p-4 transition hover:border-violet-500/25"
              >
                <div className="flex items-start gap-3">
                  <span
                    className={`mt-0.5 h-2 w-2 shrink-0 rounded-full ${
                      rec.priority === "high"
                        ? "bg-rose-400"
                        : rec.priority === "medium"
                          ? "bg-amber-400"
                          : "bg-emerald-400"
                    }`}
                  />
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-white">{rec.title}</p>
                    <p className="mt-1 text-sm text-slate-500">{rec.reason}</p>
                    <button
                      type="button"
                      className="mt-2 text-sm font-medium text-violet-400 hover:text-violet-300"
                    >
                      {rec.action} →
                    </button>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>

        {/* Interview + quick actions */}
        <div className="space-y-6">
          <div className="glass rounded-2xl p-6 bg-gradient-to-br from-violet-600/10 to-blue-600/5">
            <h2 className="text-lg font-semibold text-white">Interview Readiness</h2>
            <p className="mt-1 text-sm text-slate-400">
              Communication 4.2 · Technical 3.8 · Confidence 72%
            </p>
            <div className="mt-4 h-2 overflow-hidden rounded-full bg-slate-800">
              <div
                className="h-full rounded-full bg-gradient-to-r from-violet-500 to-blue-500"
                style={{ width: "84%" }}
              />
            </div>
            <p className="mt-2 text-xs text-violet-300">84% interview ready</p>
            <Button variant="gradient" href="/interview" className="mt-5 w-full sm:w-auto">
              Start Mock Interview
            </Button>
          </div>

          <div className="glass rounded-2xl p-6">
            <h2 className="text-lg font-semibold text-white">Quick Actions</h2>
            <div className="mt-4 flex flex-wrap gap-3">
              <Button variant="secondary" href="/dashboard#planner">
                Study Planner
              </Button>
              <Button variant="secondary" href="/dashboard#assistant">
                PDF Assistant
              </Button>
              <Button variant="ghost" href="/">
                Landing Page
              </Button>
            </div>
          </div>
        </div>
      </div>
    </DashboardShell>
  );
}
