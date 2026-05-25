import { PageHeader } from "@/components/ui/PageHeader";
import { DashboardMVP } from "@/components/dashboard/DashboardMVP";

export default function DashboardPage() {
  return (
    <>
      <PageHeader
        title="Welcome back, Student"
        subtitle="MVP dashboard — performance, study habits, weak topics, and AI coaching"
      />
      <DashboardMVP />
    </>
  );
}
