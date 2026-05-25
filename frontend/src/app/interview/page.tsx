import { DashboardShell } from "@/components/layout/DashboardShell";
import { InterviewRoom } from "@/components/interview/InterviewRoom";

export default function InterviewPage() {
  return (
    <DashboardShell
      title="AI Mock Interview"
      subtitle="Practice with live confidence tracking — webcam, mic, and AI feedback"
    >
      <InterviewRoom />
    </DashboardShell>
  );
}
