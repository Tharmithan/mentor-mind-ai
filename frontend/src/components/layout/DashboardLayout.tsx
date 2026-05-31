import { Sidebar } from "@/components/layout/Sidebar";
import { MobileNav } from "@/components/layout/MobileNav";

export function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen bg-background bg-mesh">
      <Sidebar />
      <div className="flex flex-1 flex-col pb-[4.5rem] md:pb-0">
        <main className="flex-1 p-4 sm:p-6 md:p-8">{children}</main>
      </div>
      <MobileNav />
    </div>
  );
}
