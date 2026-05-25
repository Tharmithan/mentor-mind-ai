import { DashboardLayout } from "@/components/layout/DashboardLayout";

export default function InterviewRootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <DashboardLayout>{children}</DashboardLayout>;
}
