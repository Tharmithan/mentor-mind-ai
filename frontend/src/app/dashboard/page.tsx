import { PageHeader } from "@/components/ui/PageHeader";
import { Button } from "@/components/ui/Button";
import { StatCard } from "@/components/ui/Card";
import { GlassCard } from "@/components/ui/GlassCard";
import { AnimatedSection } from "@/components/ui/AnimatedSection";
import { ProgressRing } from "@/components/ui/ProgressRing";
import {
  StudyChart,
  PerformanceChart,
} from "@/components/dashboard/DashboardCharts";
import {
  TrendingUp,
  Mic,
  Flame,
  Clock,
  AlertCircle,
  ArrowRight,
} from "lucide-react";

const recommendations = [
  {
    priority: "high" as const,
    title: "Review Data Structures — Trees & Graphs",
    reason: "Weak topic detected from last quiz (62%)",
    action: "Start revision",
  },
  {
    priority: "medium" as const,
    title: "Schedule mock technical interview",
    reason: "Last interview score: 3.8/5 — room to improve",
    action: "Practice now",
  },
  {
    priority: "low" as const,
    title: "Maintain Mathematics momentum",
    reason: "Strong performance — 91% last assessment",
    action: "View progress",
  },
];

const priorityDot = {
  high: "bg-rose-400",
  medium: "bg-amber-400",
  low: "bg-emerald-400",
};

export default function DashboardPage() {
  return (
    <>
      <PageHeader
        title="Welcome back, Student"
        subtitle="Your AI learning command center — real-time insights at a glance"
      />

      <div className="stagger-children grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Performance Score"
          value="82%"
          sub="+5% from last week"
          trend="up"
          icon={<TrendingUp className="h-5 w-5" />}
        />
        <StatCard
          label="Interview Score"
          value="4.2 / 5"
          sub="Last 3 sessions avg"
          trend="up"
          icon={<Mic className="h-5 w-5" />}
        />
        <StatCard
          label="Study Streak"
          value="7 days"
          sub="Personal best!"
          trend="up"
          icon={<Flame className="h-5 w-5 text-orange-400" />}
        />
        <StatCard
          label="Weekly Study Hours"
          value="28.5h"
          sub="+12% vs last week"
          trend="up"
          icon={<Clock className="h-5 w-5" />}
        />
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-3">
        <AnimatedSection delay={100} className="lg:col-span-1">
          <GlassCard className="flex flex-col items-center p-6">
            <h2 className="mb-6 w-full text-left text-lg font-semibold text-white">
              Overall Performance
            </h2>
            <ProgressRing value={82} label="Score" sublabel="On track for goals" />
            <div className="mt-6 w-full">
              <PerformanceChart />
            </div>
            <div className="mt-4 w-full space-y-2 text-sm">
              {[
                { subject: "Mathematics", score: "91%", color: "text-emerald-400" },
                { subject: "Programming", score: "78%", color: "text-violet-400" },
                { subject: "Data Structures", score: "62%", color: "text-amber-400" },
              ].map((s) => (
                <div key={s.subject} className="flex justify-between text-slate-400">
                  <span>{s.subject}</span>
                  <span className={`font-medium ${s.color}`}>{s.score}</span>
                </div>
              ))}
            </div>
          </GlassCard>
        </AnimatedSection>

        <AnimatedSection delay={200} className="lg:col-span-2">
          <GlassCard className="p-6">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h2 className="text-lg font-semibold text-white">Study Analytics</h2>
              <span className="rounded-full bg-violet-500/15 px-3 py-1 text-xs text-violet-300">
                This week
              </span>
            </div>
            <div className="mt-4">
              <StudyChart />
            </div>
            <div className="mt-6 grid grid-cols-3 gap-4 border-t border-violet-500/10 pt-6">
              {[
                { label: "Focus score", value: "87%" },
                { label: "Quizzes done", value: "12" },
                { label: "Topics mastered", value: "8" },
              ].map((m) => (
                <div key={m.label}>
                  <p className="text-xs text-slate-500">{m.label}</p>
                  <p className="text-xl font-bold text-white">{m.value}</p>
                </div>
              ))}
            </div>
          </GlassCard>
        </AnimatedSection>
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        <AnimatedSection delay={300}>
          <GlassCard className="p-6">
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
                  className="rounded-xl border border-violet-500/10 bg-slate-900/40 p-4 transition-all duration-200 hover:border-violet-500/25 hover:translate-x-0.5"
                >
                  <div className="flex items-start gap-3">
                    <span
                      className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${priorityDot[rec.priority]}`}
                    />
                    <div className="min-w-0 flex-1">
                      <p className="font-medium text-white">{rec.title}</p>
                      <p className="mt-1 flex items-start gap-1 text-sm text-slate-500">
                        <AlertCircle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
                        {rec.reason}
                      </p>
                      <button
                        type="button"
                        className="mt-2 inline-flex items-center gap-1 text-sm font-medium text-violet-400 hover:text-violet-300"
                      >
                        {rec.action}
                        <ArrowRight className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </GlassCard>
        </AnimatedSection>

        <div className="space-y-6">
          <AnimatedSection delay={400}>
            <GlassCard className="bg-gradient-to-br from-violet-600/15 to-blue-600/10 p-6">
              <h2 className="text-lg font-semibold text-white">Interview Readiness</h2>
              <p className="mt-1 text-sm text-slate-400">
                Communication 4.2 · Technical 3.8 · Confidence 72%
              </p>
              <div className="mt-4 h-2.5 overflow-hidden rounded-full bg-slate-800">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-violet-500 to-blue-500 transition-all duration-700"
                  style={{ width: "84%" }}
                />
              </div>
              <p className="mt-2 text-xs text-violet-300">84% interview ready</p>
              <Button variant="gradient" href="/interview" className="mt-5 w-full sm:w-auto">
                Start Mock Interview
              </Button>
            </GlassCard>
          </AnimatedSection>

          <AnimatedSection delay={500}>
            <GlassCard className="p-6">
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
            </GlassCard>
          </AnimatedSection>
        </div>
      </div>
    </>
  );
}
