import { DashboardLayout } from "@/components/layout/DashboardLayout";

export default function PlannerRootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <DashboardLayout>{children}</DashboardLayout>;
}
