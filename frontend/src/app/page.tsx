import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { SectionHeader } from "@/components/ui/SectionHeader";

const features = [
  {
    title: "Performance Prediction",
    description:
      "ML models analyze study patterns and predict outcomes so you focus where it matters most.",
    icon: (
      <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
    ),
  },
  {
    title: "Personalized Study Planner",
    description:
      "Weak-topic detection and smart revision schedules tailored to your learning pace.",
    icon: (
      <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
      </svg>
    ),
  },
  {
    title: "AI Mock Interview",
    description:
      "Practice with AI-generated questions, voice interaction, and real-time scoring.",
    icon: (
      <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
      </svg>
    ),
  },
  {
    title: "Emotion & Confidence",
    description:
      "Webcam-based stress and confidence analysis during study and interview sessions.",
    icon: (
      <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
  },
  {
    title: "Career Recommendations",
    description:
      "Data-driven career path suggestions based on your skills and performance trends.",
    icon: (
      <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
      </svg>
    ),
  },
  {
    title: "RAG PDF Assistant",
    description:
      "Upload course PDFs and get instant answers with semantic search and citations.",
    icon: (
      <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    ),
  },
];

const aiCapabilities = [
  { label: "ML Performance Models", value: "XGBoost · LightGBM" },
  { label: "Emotion Detection", value: "FER2013 · MediaPipe" },
  { label: "Interview AI", value: "LLM + Speech-to-Text" },
  { label: "RAG Engine", value: "Embeddings + pgvector" },
];

const testimonials = [
  {
    quote:
      "MentorMind helped me identify weak topics before my finals. The dashboard feels like a real SaaS product.",
    name: "Priya S.",
    role: "CS Student, SLIIT",
    rating: 5,
  },
  {
    quote:
      "The mock interview with confidence tracking is a game-changer. I felt much more prepared for my internship interviews.",
    name: "Arun K.",
    role: "Software Engineering Intern",
    rating: 5,
  },
  {
    quote:
      "Finally an AI learning platform that looks professional enough to put on my portfolio and resume.",
    name: "Nisha M.",
    role: "Final Year IT Student",
    rating: 5,
  },
];

export default function Home() {
  return (
    <div className="flex min-h-full flex-col bg-[#030712]">
      <Navbar />

      <main className="flex-1">
        {/* Hero */}
        <section className="relative overflow-hidden px-6 pb-28 pt-16 sm:pt-24">
          <div className="pointer-events-none absolute inset-0 bg-mesh" />
          <div className="pointer-events-none absolute left-1/2 top-0 h-[500px] w-[800px] -translate-x-1/2 rounded-full bg-violet-600/20 blur-[120px]" />
          <div className="relative mx-auto max-w-5xl text-center">
            <p className="mb-6 inline-flex items-center gap-2 rounded-full border border-violet-500/30 bg-violet-500/10 px-4 py-1.5 text-sm text-violet-300">
              <span className="h-2 w-2 rounded-full bg-violet-400 animate-pulse" />
              AI-Powered Learning Platform
            </p>
            <h1 className="text-4xl font-bold leading-tight tracking-tight text-white sm:text-6xl lg:text-7xl">
              Learn smarter.
              <br />
              <span className="gradient-text">Interview stronger.</span>
            </h1>
            <p className="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-slate-400 sm:text-xl">
              The all-in-one AI coach for students — performance prediction,
              personalized study plans, mock interviews, and confidence analytics.
            </p>
            <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
              <Button variant="gradient" href="/dashboard">
                Start Free — Get Started
              </Button>
              <Button variant="secondary" href="/interview">
                Try Mock Interview
              </Button>
            </div>
            <div className="mt-16 grid grid-cols-3 gap-6 border-t border-violet-500/10 pt-12 sm:max-w-lg sm:mx-auto">
              {[
                { stat: "10K+", label: "Study hours tracked" },
                { stat: "94%", label: "Prediction accuracy" },
                { stat: "4.8★", label: "Interview rating" },
              ].map((s) => (
                <div key={s.label}>
                  <p className="text-2xl font-bold gradient-text sm:text-3xl">{s.stat}</p>
                  <p className="mt-1 text-xs text-slate-500">{s.label}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Features */}
        <section id="features" className="border-t border-violet-500/10 px-6 py-24">
          <div className="mx-auto max-w-7xl">
            <div className="flex justify-center">
              <SectionHeader
                badge="Features"
                title="Everything you need to excel"
                subtitle="Six AI-powered modules built for modern student success."
              />
            </div>
            <div className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {features.map((f) => (
                <Card
                  key={f.title}
                  title={f.title}
                  description={f.description}
                  icon={f.icon}
                />
              ))}
            </div>
          </div>
        </section>

        {/* AI Capabilities */}
        <section
          id="ai-capabilities"
          className="border-t border-violet-500/10 bg-gradient-to-b from-violet-950/20 to-transparent px-6 py-24"
        >
          <div className="mx-auto max-w-7xl">
            <div className="grid items-center gap-12 lg:grid-cols-2">
              <SectionHeader
                badge="AI Engine"
                title="Powered by real machine learning"
                subtitle="Not just chatbots — trained models, computer vision, and RAG pipelines working together."
                align="left"
              />
              <div className="grid gap-4 sm:grid-cols-2">
                {aiCapabilities.map((cap) => (
                  <div
                    key={cap.label}
                    className="glass rounded-2xl p-5 transition hover:ring-violet-500/30"
                  >
                    <p className="text-sm text-slate-400">{cap.label}</p>
                    <p className="mt-1 text-lg font-semibold text-white">{cap.value}</p>
                  </div>
                ))}
              </div>
            </div>
            <div className="mt-12 rounded-2xl border border-violet-500/20 bg-gradient-to-r from-violet-600/10 via-transparent to-blue-600/10 p-8 sm:p-10">
              <div className="flex flex-col items-center justify-between gap-6 sm:flex-row">
                <div>
                  <h3 className="text-xl font-bold text-white">
                    Real-time confidence & emotion analysis
                  </h3>
                  <p className="mt-2 max-w-xl text-slate-400">
                    Webcam + microphone feed into our emotion detection pipeline
                    during mock interviews — see your confidence score live.
                  </p>
                </div>
                <Button variant="gradient" href="/interview">
                  Launch Interview UI
                </Button>
              </div>
            </div>
          </div>
        </section>

        {/* Testimonials */}
        <section id="testimonials" className="border-t border-violet-500/10 px-6 py-24">
          <div className="mx-auto max-w-7xl">
            <div className="flex justify-center">
              <SectionHeader
                badge="Reviews"
                title="Trusted by students"
                subtitle="Built to impress recruiters and hiring managers."
              />
            </div>
            <div className="mt-14 grid gap-6 md:grid-cols-3">
              {testimonials.map((t) => (
                <div key={t.name} className="glass rounded-2xl p-6">
                  <div className="mb-4 flex gap-0.5 text-amber-400">
                    {Array.from({ length: t.rating }).map((_, i) => (
                      <span key={i}>★</span>
                    ))}
                  </div>
                  <p className="text-slate-300 leading-relaxed">&ldquo;{t.quote}&rdquo;</p>
                  <div className="mt-6 flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-violet-600 to-blue-600 text-sm font-bold text-white">
                      {t.name[0]}
                    </div>
                    <div>
                      <p className="font-semibold text-white">{t.name}</p>
                      <p className="text-xs text-slate-500">{t.role}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="px-6 py-24">
          <div className="relative mx-auto max-w-4xl overflow-hidden rounded-3xl">
            <div className="absolute inset-0 bg-gradient-to-br from-violet-600 via-violet-800 to-blue-900" />
            <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg width=\'60\' height=\'60\' viewBox=\'0 0 60 60\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cg fill=\'none\' fill-rule=\'evenodd\'%3E%3Cg fill=\'%23ffffff\' fill-opacity=\'0.05\'%3E%3Cpath d=\'M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z\'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')] opacity-50" />
            <div className="relative px-8 py-16 text-center sm:px-16 sm:py-20">
              <h2 className="text-3xl font-bold text-white sm:text-4xl">
                Ready to transform your learning?
              </h2>
              <p className="mx-auto mt-4 max-w-xl text-violet-100/90">
                Join MentorMind AI — your personal coach for academics and
                interviews. Free to start during development.
              </p>
              <div className="mt-10 flex flex-wrap justify-center gap-4">
                <Button
                  variant="secondary"
                  href="/dashboard"
                  className="!bg-white !text-violet-900 hover:!bg-violet-50 border-0"
                >
                  Open Dashboard
                </Button>
                <Button
                  variant="ghost"
                  href="/interview"
                  className="!text-white hover:!bg-white/10"
                >
                  Practice Interview →
                </Button>
              </div>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
