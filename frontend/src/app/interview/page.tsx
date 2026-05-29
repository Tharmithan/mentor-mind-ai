import { PageHeader } from "@/components/ui/PageHeader";
import { InterviewCoach } from "@/components/interview/InterviewCoach";

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
