import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";

const features = [
  {
    title: "Performance Prediction",
    description:
      "ML models analyze study patterns and predict outcomes so you can focus where it matters.",
    icon: "📊",
  },
  {
    title: "Personalized Study Planner",
    description:
      "Weak-topic detection and revision plans tailored to your learning style.",
    icon: "📚",
  },
  {
    title: "AI Mock Interview",
    description:
      "Practice with AI-generated questions, voice interaction, and real-time scoring.",
    icon: "🎤",
  },
  {
    title: "Emotion & Confidence",
    description:
      "Webcam-based stress and confidence analysis during study and interview sessions.",
    icon: "🧠",
  },
  {
    title: "Career Recommendations",
    description:
      "Data-driven career path suggestions based on your skills and performance.",
    icon: "🚀",
  },
  {
    title: "RAG PDF Assistant",
    description:
      "Upload course PDFs and ask questions with semantic search and cited answers.",
    icon: "📄",
  },
];

export default function Home() {
  return (
    <div className="flex min-h-full flex-col bg-slate-950">
      <Navbar />

      <main className="flex-1">
        {/* Hero */}
        <section className="relative overflow-hidden px-6 pb-24 pt-20">
          <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-900/30 via-slate-950 to-slate-950" />
          <div className="relative mx-auto max-w-4xl text-center">
            <p className="mb-4 inline-block rounded-full border border-indigo-500/30 bg-indigo-500/10 px-4 py-1 text-sm text-indigo-300">
              AI Personalized Learning & Interview Coach
            </p>
            <h1 className="text-4xl font-bold tracking-tight text-white sm:text-6xl">
              Learn smarter.
              <br />
              <span className="bg-gradient-to-r from-indigo-400 to-emerald-400 bg-clip-text text-transparent">
                Interview stronger.
              </span>
            </h1>
            <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-400">
              MentorMind AI helps students improve performance, prepare for
              interviews, build confidence, and get personalized study
              recommendations — all in one platform.
            </p>
            <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
              <Button variant="primary" href="/dashboard">
                Get Started
              </Button>
              <Button variant="secondary" href="/dashboard">
                View Dashboard
              </Button>
            </div>
          </div>
        </section>

        {/* Features */}
        <section id="features" className="border-t border-slate-800 px-6 py-20">
          <div className="mx-auto max-w-7xl">
            <h2 className="text-center text-3xl font-bold text-white">
              Everything you need to excel
            </h2>
            <p className="mx-auto mt-3 max-w-xl text-center text-slate-400">
              Six AI-powered modules designed for modern student success.
            </p>
            <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {features.map((f) => (
                <Card
                  key={f.title}
                  title={f.title}
                  description={f.description}
                  icon={<span className="text-xl">{f.icon}</span>}
                />
              ))}
            </div>
          </div>
        </section>

        {/* How it works */}
        <section
          id="how-it-works"
          className="border-t border-slate-800 bg-slate-900/30 px-6 py-20"
        >
          <div className="mx-auto max-w-3xl text-center">
            <h2 className="text-3xl font-bold text-white">How it works</h2>
            <ol className="mt-10 space-y-6 text-left text-slate-300">
              <li className="flex gap-4">
                <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-indigo-500 text-sm font-bold text-white">
                  1
                </span>
                <span>
                  <strong className="text-white">Track</strong> — Log study
                  sessions, quizzes, and interview practice.
                </span>
              </li>
              <li className="flex gap-4">
                <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-indigo-500 text-sm font-bold text-white">
                  2
                </span>
                <span>
                  <strong className="text-white">Analyze</strong> — ML models
                  predict performance and detect weak topics.
                </span>
              </li>
              <li className="flex gap-4">
                <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-indigo-500 text-sm font-bold text-white">
                  3
                </span>
                <span>
                  <strong className="text-white">Improve</strong> — Get study
                  plans, mock interviews, and AI coaching.
                </span>
              </li>
            </ol>
          </div>
        </section>

        {/* CTA */}
        <section className="px-6 py-20">
          <div className="mx-auto max-w-3xl rounded-2xl border border-indigo-500/30 bg-gradient-to-br from-indigo-950/80 to-slate-900 p-10 text-center">
            <h2 className="text-2xl font-bold text-white">
              Ready to start your AI learning journey?
            </h2>
            <p className="mt-3 text-slate-400">
              Week 1 foundation is live. Auth, ML models, and interviews coming
              in upcoming phases.
            </p>
            <div className="mt-8">
              <Button variant="primary" href="/dashboard">
                Open Dashboard
              </Button>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
