import { PageHeader } from "@/components/ui/PageHeader";
import { DashboardMVP } from "@/components/dashboard/DashboardMVP";

export default function DashboardPage() {
  return (
    <>
      <PageHeader
        title="Welcome back, Student"
        subtitle="Your AI learning command center — insights, charts, and coaching"
      />
      <DashboardMVP />
    </>
  );
}
