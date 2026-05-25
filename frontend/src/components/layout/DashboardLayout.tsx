import { Sidebar } from "@/components/layout/Sidebar";
import { MobileNav } from "@/components/layout/MobileNav";

export function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen bg-[#030712] bg-mesh">
      <Sidebar />
      <div className="flex flex-1 flex-col pb-20 md:pb-0">
        <main className="flex-1 p-4 pb-28 sm:p-6 md:p-8">{children}</main>
      </div>
      <MobileNav />
    </div>
  );
}
