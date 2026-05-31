import { DashboardLayout } from "@/components/layout/DashboardLayout";

export default function CoachRootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <DashboardLayout>{children}</DashboardLayout>;
}
