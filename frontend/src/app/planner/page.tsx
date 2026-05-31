import { PageHeader } from "@/components/ui/PageHeader";
import { LearningPlannerPanel } from "@/components/planner/LearningPlannerPanel";

export default function PlannerPage() {
  return (
    <>
      <PageHeader
        title="Personalized Learning Planner"
        subtitle="Set a career goal — get a month-by-month roadmap, milestones, and weekly study plans"
      />
      <LearningPlannerPanel />
    </>
  );
}
