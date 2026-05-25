import { PageHeader } from "@/components/ui/PageHeader";
import { InterviewRoom } from "@/components/interview/InterviewRoom";

export default function InterviewPage() {
  return (
    <>
      <PageHeader
        title="AI Mock Interview"
        subtitle="Practice with live confidence tracking — webcam, mic, and AI feedback"
      />
      <InterviewRoom />
    </>
  );
}
