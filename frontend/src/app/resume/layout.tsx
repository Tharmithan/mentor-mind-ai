import { DashboardLayout } from "@/components/layout/DashboardLayout";

export default function ResumeRootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <DashboardLayout>{children}</DashboardLayout>;
}
