import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { AnimatedSection } from "@/components/ui/AnimatedSection";
import {
  BarChart3,
  BookOpen,
  Mic,
  Smile,
  TrendingUp,
  FileText,
  Brain,
  Sparkles,
  Star,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";

const features: { title: string; description: string; icon: LucideIcon }[] = [
  {
    title: "Performance Prediction",
    description:
      "ML models analyze study patterns and predict outcomes so you focus where it matters most.",
    icon: BarChart3,
  },
  {
    title: "Personalized Study Planner",
    description:
      "Weak-topic detection and smart revision schedules tailored to your learning pace.",
    icon: BookOpen,
  },
  {
    title: "AI Mock Interview",
    description:
      "Practice with AI-generated questions, voice interaction, and real-time scoring.",
    icon: Mic,
  },
  {
    title: "Emotion & Confidence",
    description:
      "Webcam-based stress and confidence analysis during study and interview sessions.",
    icon: Smile,
  },
  {
    title: "Career Recommendations",
    description:
      "Data-driven career path suggestions based on your skills and performance trends.",
    icon: TrendingUp,
  },
  {
    title: "RAG PDF Assistant",
    description:
      "Upload course PDFs and get instant answers with semantic search and citations.",
    icon: FileText,
  },
];

const aiCapabilities = [
  { label: "ML Performance Models", value: "XGBoost · LightGBM", icon: BarChart3 },
  { label: "Emotion Detection", value: "FER2013 · MediaPipe", icon: Smile },
  { label: "Interview AI", value: "LLM + Speech-to-Text", icon: Mic },
  { label: "RAG Engine", value: "Embeddings + pgvector", icon: Brain },
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
        <section className="relative overflow-hidden px-4 pb-28 pt-16 sm:px-6 sm:pt-24">
          <div className="pointer-events-none absolute inset-0 bg-mesh" />
          <div className="pointer-events-none absolute left-1/2 top-0 h-[500px] w-[min(800px,100vw)] -translate-x-1/2 rounded-full bg-violet-600/20 blur-[120px]" />
          <div className="relative mx-auto max-w-5xl text-center">
            <AnimatedSection>
              <p className="mb-6 inline-flex items-center gap-2 rounded-full border border-violet-500/30 bg-violet-500/10 px-4 py-1.5 text-sm text-violet-300">
                <Sparkles className="h-4 w-4" />
                AI-Powered Learning Platform
              </p>
            </AnimatedSection>
            <AnimatedSection delay={100}>
              <h1 className="text-4xl font-bold leading-tight tracking-tight text-white sm:text-6xl lg:text-7xl">
                Learn smarter.
                <br />
                <span className="gradient-text">Interview stronger.</span>
              </h1>
            </AnimatedSection>
            <AnimatedSection delay={200}>
              <p className="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-slate-400 sm:text-xl">
                The all-in-one AI coach for students — performance prediction,
                personalized study plans, mock interviews, and confidence analytics.
              </p>
            </AnimatedSection>
            <AnimatedSection delay={300}>
              <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
                <Button variant="gradient" href="/dashboard">
                  Start Free — Get Started
                </Button>
                <Button variant="secondary" href="/interview">
                  Try Mock Interview
                </Button>
              </div>
            </AnimatedSection>
            <div className="stagger-children mx-auto mt-16 grid max-w-lg grid-cols-3 gap-6 border-t border-violet-500/10 pt-12">
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

        <section id="features" className="border-t border-violet-500/10 px-4 py-24 sm:px-6">
          <div className="mx-auto max-w-7xl">
            <div className="flex justify-center">
              <SectionHeader
                badge="Features"
                title="Everything you need to excel"
                subtitle="Six AI-powered modules built for modern student success."
              />
            </div>
            <div className="stagger-children mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {features.map((f) => {
                const Icon = f.icon;
                return (
                  <Card
                    key={f.title}
                    title={f.title}
                    description={f.description}
                    icon={<Icon className="h-6 w-6" />}
                  />
                );
              })}
            </div>
          </div>
        </section>

        <section
          id="ai-capabilities"
          className="border-t border-violet-500/10 bg-gradient-to-b from-violet-950/20 to-transparent px-4 py-24 sm:px-6"
        >
          <div className="mx-auto max-w-7xl">
            <div className="grid items-center gap-12 lg:grid-cols-2">
              <AnimatedSection>
                <SectionHeader
                  badge="AI Engine"
                  title="Powered by real machine learning"
                  subtitle="Trained models, computer vision, and RAG pipelines — not just chatbots."
                  align="left"
                />
              </AnimatedSection>
              <div className="stagger-children grid gap-4 sm:grid-cols-2">
                {aiCapabilities.map((cap) => {
                  const Icon = cap.icon;
                  return (
                    <div key={cap.label} className="glass rounded-2xl p-5 transition duration-300 hover:scale-[1.02] hover:shadow-lg hover:shadow-violet-500/10">
                      <Icon className="mb-3 h-5 w-5 text-violet-400" />
                      <p className="text-sm text-slate-400">{cap.label}</p>
                      <p className="mt-1 text-lg font-semibold text-white">{cap.value}</p>
                    </div>
                  );
                })}
              </div>
            </div>
            <AnimatedSection delay={200} className="mt-12">
              <div className="glass animate-shimmer rounded-2xl p-8 sm:p-10">
                <div className="flex flex-col items-center justify-between gap-6 sm:flex-row">
                  <div>
                    <h3 className="text-xl font-bold text-white">
                      Real-time confidence & emotion analysis
                    </h3>
                    <p className="mt-2 max-w-xl text-slate-400">
                      Webcam + microphone feed into our emotion pipeline during mock interviews.
                    </p>
                  </div>
                  <Button variant="gradient" href="/interview">
                    Launch Interview UI
                  </Button>
                </div>
              </div>
            </AnimatedSection>
          </div>
        </section>

        <section id="testimonials" className="border-t border-violet-500/10 px-4 py-24 sm:px-6">
          <div className="mx-auto max-w-7xl">
            <div className="flex justify-center">
              <SectionHeader
                badge="Reviews"
                title="Trusted by students"
                subtitle="Built to impress recruiters and hiring managers."
              />
            </div>
            <div className="stagger-children mt-14 grid gap-6 md:grid-cols-3">
              {testimonials.map((t) => (
                <div key={t.name} className="glass rounded-2xl p-6 transition duration-300 hover:scale-[1.02]">
                  <div className="mb-4 flex gap-0.5 text-amber-400">
                    {Array.from({ length: t.rating }).map((_, i) => (
                      <Star key={i} className="h-4 w-4 fill-current" />
                    ))}
                  </div>
                  <p className="leading-relaxed text-slate-300">&ldquo;{t.quote}&rdquo;</p>
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

        <section className="px-4 py-24 sm:px-6">
          <AnimatedSection>
            <div className="relative mx-auto max-w-4xl overflow-hidden rounded-3xl">
              <div className="absolute inset-0 bg-gradient-to-br from-violet-600 via-violet-800 to-blue-900" />
              <div className="relative px-8 py-16 text-center sm:px-16 sm:py-20">
                <h2 className="text-3xl font-bold text-white sm:text-4xl">
                  Ready to transform your learning?
                </h2>
                <p className="mx-auto mt-4 max-w-xl text-violet-100/90">
                  Join MentorMind AI — your personal coach for academics and interviews.
                </p>
                <div className="mt-10 flex flex-wrap justify-center gap-4">
                  <Button
                    variant="secondary"
                    href="/dashboard"
                    className="!border-0 !bg-white !text-violet-900 hover:!bg-violet-50"
                  >
                    Open Dashboard
                  </Button>
                  <Button variant="ghost" href="/interview" className="!text-white hover:!bg-white/10">
                    Practice Interview →
                  </Button>
                </div>
              </div>
            </div>
          </AnimatedSection>
        </section>
      </main>

      <Footer />
    </div>
  );
}
