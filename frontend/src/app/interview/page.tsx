import dynamic from "next/dynamic";
import { PageHeader } from "@/components/ui/PageHeader";
import { ChartSkeleton } from "@/components/charts/ChartSkeleton";

const InterviewCoach = dynamic(
  () => import("@/components/interview/InterviewCoach").then((m) => m.InterviewCoach),
  { ssr: false, loading: () => <ChartSkeleton className="h-96" /> }
);

export default function InterviewPage() {
  return (
    <>
      <PageHeader
        title="AI Interview Coach"
        subtitle="HR, technical, or behavioral mock interviews — AI asks questions, scores your answers, and gives feedback"
      />
      <InterviewCoach />
    </>
  );
}
