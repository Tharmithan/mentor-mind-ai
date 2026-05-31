import { PageHeader } from "@/components/ui/PageHeader";
import { CoachDashboard } from "@/components/coach/CoachDashboard";

export default function CoachPage() {
  return (
    <>
      <PageHeader
        title="AI Coach Dashboard"
        subtitle="Learning scores, career readiness, skill gaps, and weekly AI progress reports"
      />
      <CoachDashboard />
    </>
  );
}
